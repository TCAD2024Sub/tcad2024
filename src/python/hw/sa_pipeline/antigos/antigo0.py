from math import ceil, log2, sqrt
from veriloggen import *
from utils import initialize_regs


class SAComponents:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
            self, n_cells: int = 16, n_neighbors: int = 5, align_bits: int = 8
    ):
        self.cache = {}
        self.n_cells = n_cells
        self.n_neighbors = n_neighbors
        self.align_bits = align_bits

    def create_fetch_data(self, input_data_width, output_data_width):
        name = "fetch_data_%d_%d" % (input_data_width, output_data_width)
        if name in self.cache.keys():
            return self.cache[name]
        m = Module(name)

        clk = m.Input("clk")
        start = m.Input("start")
        rst = m.Input("rst")

        request_read = m.OutputReg("request_read")
        data_valid = m.Input("data_valid")
        read_data = m.Input("read_data", input_data_width)

        pop_data = m.Input("pop_data")
        available_pop = m.OutputReg("available_pop")
        data_out = m.Output("data_out", output_data_width)

        NUM = input_data_width // output_data_width

        fsm_read = m.Reg("fsm_read", 1)
        fsm_control = m.Reg("fsm_control", 1)
        data = m.Reg("data", input_data_width)
        buffer = m.Reg("buffer", input_data_width)
        count = m.Reg("count", NUM)
        has_buffer = m.Reg("has_buffer")
        buffer_read = m.Reg("buffer_read")
        en = m.Reg("en")

        m.EmbeddedCode("")
        data_out.assign(data[0:output_data_width])

        m.Always(Posedge(clk))(
            If(rst)(en(Int(0, 1, 2))).Else(en(Mux(en, en, start)))
        )

        m.Always(Posedge(clk))(
            If(rst)(fsm_read(0), request_read(0), has_buffer(0)).Else(
                request_read(0),
                Case(fsm_read)(
                    When(0)(
                        If(en & data_valid)(
                            buffer(read_data),
                            request_read(1),
                            has_buffer(1),
                            fsm_read(1),
                        )
                    ),
                    When(1)(If(buffer_read)(has_buffer(0), fsm_read(0))),
                ),
            )
        )

        m.Always(Posedge(clk))(
            If(rst)(
                fsm_control(0), available_pop(0), count(0), buffer_read(0)
            ).Else(
                buffer_read(0),
                Case(fsm_control)(
                    When(0)(
                        If(has_buffer)(
                            data(buffer),
                            count(1),
                            buffer_read(1),
                            available_pop(1),
                            fsm_control(1),
                        )
                    ),
                    When(1)(
                        If(pop_data & ~count[NUM - 1])(
                            count(count << 1), data(data[output_data_width:])
                        ),
                        If(pop_data & count[NUM - 1] & has_buffer)(
                            count(1), data(buffer), buffer_read(1)
                        ),
                        If(count[NUM - 1] & pop_data & ~has_buffer)(
                            count(count << 1),
                            data(data[output_data_width:]),
                            available_pop(0),
                            fsm_control(0),
                        ),
                    ),
                ),
            )
        )

        initialize_regs(m)

        self.cache[name] = m
        return m

    def create_random_generator_11b(self) -> Module:
        # LFSR random generator based on Fibonacci's LFSR
        name = "random_generator_11b"
        if name in self.cache.keys():
            return self.cache[name]

        bits = 11

        m = Module(name)

        clk = m.Input("clk")
        rst = m.Input("rst")
        en = m.Input("en")
        seed = m.Input("seed", bits)
        rnd = m.OutputReg("rnd", bits)

        m.Always(Posedge(clk))(
            If(rst)(rnd(seed)).Elif(en)(
                rnd(
                    Cat(
                        rnd[0: rnd.width - 1],
                        Not(Xor(Xor(Xor(rnd[10], rnd[9]), rnd[7]), rnd[1])),
                    )
                )
            )
        )

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_cnc_memory(self) -> Module:
        name = "cnc_memory"
        if name in self.cache.keys():
            return self.cache[name]
        n_cells = self.n_cells
        bits = ceil(log2(n_cells))

        m = Module(name)

        clk = m.Input("clk")
        wr = m.Input("wr")
        rd = m.Input("rd")

        w_addr = m.Input("w_addr", bits)
        din = m.Input("din", bits + 1)

        r_addr1 = m.Input("r_addr1", bits)
        d_out1 = m.OutputReg("d_out1", bits + 1)

        r_addr2 = m.Input("r_addr2", bits)
        d_out2 = m.OutputReg("d_out2", bits + 1)

        # m.EmbeddedCode(
        #    '(* ramstyle = "AUTO, no_rw_check" *) reg  [data_width-1:0] mem[0:2**addr_width-1];')
        # m.EmbeddedCode('/*')
        mem_data = m.Reg("mem_data", bits + 1, n_cells)
        # m.EmbeddedCode('*/')

        m.Always(Posedge(clk))(
            If(wr)(
                mem_data[w_addr](din),
            ),
            If(rd)(
                d_out1(mem_data[r_addr1]),
                d_out2(mem_data[r_addr2]),
            ),
        )
        m.EmbeddedCode("//synthesis translate_off")

        i = m.Integer("i")
        m.Initial(
            d_out1(0),
            d_out2(0),
            For(i(0), i < Power(2, bits), i.inc())(
                mem_data[i](0),
            ),
            # Systask('readmemh', init_file, mem_data)
        )
        m.EmbeddedCode("//synthesis translate_on")
        self.cache[name] = m
        return m

    def create_graph_memory(self) -> Module:
        name = "graph_memory"
        if name in self.cache.keys():
            return self.cache[name]
        n_cells = self.n_cells
        n_neighbors = self.n_neighbors
        bits_mem = ceil(log2(n_cells))
        bits_word = (
                ceil((ceil(log2(n_cells)) + 1) / self.align_bits)
                * self.align_bits
                * n_neighbors
        )
        m = Module(name)

        clk = m.Input("clk")

        rd = m.Input("rd")
        node1 = m.Input("node1", bits_mem)
        neighbors1_out = m.OutputReg("neighbors1_out", bits_word)

        node2 = m.Input("node2", bits_mem)
        neighbors2_out = m.OutputReg("neighbors2_out", bits_word)

        wr = m.Input("wr")
        wr_addr = m.Input("wr_addr", bits_mem)
        data_in = m.Input("data_in", bits_word)

        mem_neighbors = m.Reg("mem_neighbors", bits_word, n_cells)

        m.Always(Posedge(clk))(
            If(wr)(mem_neighbors[wr_addr](data_in)),
            If(rd)(
                neighbors1_out(mem_neighbors[node1]),
                neighbors1_out(mem_neighbors[node2]),
            ),
        )

        m.EmbeddedCode("//synthesis translate_off")

        i = m.Integer("i")
        m.Initial(
            neighbors1_out(0),
            neighbors2_out(0),
            For(i(0), i < Power(2, bits_mem), i.inc())(
                mem_neighbors[i](0),
            ),
            # Systask('readmemh', init_file, mem_data)
        )
        m.EmbeddedCode("//synthesis translate_on")
        self.cache[name] = m
        return m

    def create_manhattan_dist_calc(self) -> Module:
        name = "manhattan_dist_calc"
        if name in self.cache.keys():
            return self.cache[name]

        n_cells = self.n_cells
        bits = ceil(log2(n_cells))

        m = Module(name)

        clk = m.Input("clk")
        cell1 = m.Input("cell1", bits)
        cell2 = m.Input("cell2", bits)
        manhattan = m.OutputReg("manhattan", bits)

        manhattan_rom = m.Wire("manhattan_rom", bits, n_cells * n_cells)

        m.Always(Posedge(clk))(
            manhattan(manhattan_rom[Cat(cell1, cell2)]),
        )

        r = int(sqrt(int(n_cells)))
        c = 0

        for x1 in range(r):
            for y1 in range(r):
                for x2 in range(r):
                    for y2 in range(r):
                        d = abs(y1 - y2) + abs(x1 - x2)
                        manhattan_rom[c].assign(Int(d, bits, 10))
                        c = c + 1

        initialize_regs(m)
        self.cache[name] = m
        return m

    def create_sa_pe(self) -> Module:
        name = "sa_pe"
        if name in self.cache.keys():
            return self.cache[name]

        align_bits = self.align_bits
        n_cells = self.n_cells
        n_neighbors = self.n_neighbors
        bits = ceil(log2(n_cells))

        m = Module(name)
        clk = m.Input("clk")
        rst = m.Input("rst")

        conf_g_in = m.Input("config_g_in", align_bits)
        conf_g_in_v = m.Input("conf_g_v")
        conf_g_out = m.OutputReg("conf_g_out", align_bits)
        conf_g_out_v = m.OutputReg("conf_g_out_v")

        conf_o_in = m.Input("config_o_in", align_bits)
        conf_o_in_v = m.Input("conf_o_v")
        conf_o_out = m.OutputReg("conf_o_out", align_bits)
        conf_o_out_v = m.OutputReg("conf_o_out_v")

        m.EmbeddedCode("//graph memory regs and wires")
        gm_data_bits = (
                ceil((ceil(log2(n_cells)) + 1) / align_bits)
                * align_bits
                * n_neighbors
        )
        gm_rd = m.Reg("gm_rd")
        gm_node1 = m.Reg("gm_node1", bits)
        gm_node2 = m.Reg("gm_node2", bits)
        gm_wr = m.Reg("gm_wr")
        gm_wr_addr = m.Reg("gm_wr_addr", bits + 1)
        gm_data_in = m.Reg("gm_data_in", gm_data_bits)
        gm_neighbors1_out = m.Wire("gm_neighbors1_out", gm_data_bits)
        gm_neighbors2_out = m.Wire("gm_neighbors2_out", gm_data_bits)
        m.EmbeddedCode("//----------------")

        m.EmbeddedCode("//gm configuration")
        n_conf = gm_data_bits // align_bits
        conf_g_counter_bits = ceil(log2(n_conf)) + 1
        conf_g_counter = m.Reg("conf_g_counter", conf_g_counter_bits)
        m.Always(Posedge(clk))(
            conf_g_out(conf_g_in),
            conf_g_out_v(conf_g_in_v),
            gm_wr(0),
            If(rst)(conf_g_counter(0), gm_wr_addr(0), ).Elif(conf_g_in_v)(
                If(conf_g_counter == n_conf - 1)(
                    conf_g_counter(0),
                    gm_wr(1),
                ).Else(
                    conf_g_counter.inc(),
                ),
                gm_data_in(
                    Cat(
                        gm_data_in[conf_g_in.width: gm_data_in.width],
                        conf_g_in,
                    )
                ),
            ),
        )
        m.EmbeddedCode("//----------------")

        m.EmbeddedCode("//c - n memory")
        cnm_wr = m.Wire("cnm_wr")
        cnm_conf_o_wr = m.Reg("cnm_conf_o_wr")
        cnm_exec_wr = m.Reg("cnm_exec_wr")
        cnm_w_addr = m.Wire("cnm_w_addr", bits)
        cnm_conf_o_w_addr = m.Reg("cnm_conf_o_w_addr", bits)
        cnm_exec_w_addr = m.Reg("cnm_exec_w_addr", bits)
        cnm_din = m.Wire("cnm_din", bits + 1)
        cnm_conf_o_din = m.Wire("cnm_conf_o_din", bits)
        cnm_exec_din = m.Reg("cnm_exec_din", bits + 1)
        cnm_rd = m.Reg("cnm_rd")
        cnm_r_addr1 = m.Reg("cnm_r_addr1", bits)
        cnm_r_addr2 = m.Reg("cnm_r_addr2", bits)
        cnm_d_out1 = m.Wire("cnm_d_out1", bits + 1)
        cnm_d_out2 = m.Wire("cnm_d_out2", bits + 1)
        m.EmbeddedCode("//----------------")
        m.EmbeddedCode("//n - c memories")
        m.EmbeddedCode("//----------------")
        m.EmbeddedCode("// cnc memories configuration")
        is_configured = m.Reg("is_configured")
        cnm_wr.assign(Mux(is_configured, cnm_exec_wr, cnm_conf_o_wr))
        cnm_w_addr.assign(Mux(is_configured, cnm_exec_w_addr, cnm_conf_o_w_addr))
        cnm_din.assign(Mux(is_configured, cnm_exec_din, cnm_conf_o_din))

        m.Always(Posedge(clk))(
            cnm_conf_o_wr(0),
            If(rst)(
                cnm_conf_o_din(0),
                cnm_conf_o_w_addr(0),
            ),
        )

        m.EmbeddedCode("//----------------")

        m.EmbeddedCode("// modules instantiation")
        con = [
            ("clk", clk),
            ("rd", gm_rd),
            ("node1", gm_node1),
            ("node2", gm_node2),
            ("wr", gm_wr),
            ("wr_addr", gm_wr_addr),
            ("data_in", gm_data_in),
            ("neighbors1_out", gm_neighbors1_out),
            ("neighbors2_out", gm_neighbors2_out),
        ]
        par = []
        im = self.create_graph_memory()
        m.Instance(im, im.name, par, con)

        # ---

        con = [
            ("clk", clk),
            ("wr", cnm_wr),
            ("rd", cnm_rd),
            ("w_addr", cnm_w_addr),
            ("din", cnm_din),
            ("r_addr1", cnm_r_addr1),
            ("r_addr2", cnm_r_addr2),
            ("d_out1", cnm_d_out1),
            ("d_out2", cnm_d_out2),
        ]
        par = []
        im = self.create_cnc_memory()
        m.Instance(im, "%s_%s" % (im.name, "c_n"), par, con)
        m.EmbeddedCode("//----------------")

        self.cache[name] = m
        return m


comp = SAComponents()

comp.create_manhattan_dist_calc().to_verilog("manhattan.v")
comp.create_cnc_memory().to_verilog("cnc_memory.v")
comp.create_graph_memory().to_verilog("graph_memory.v")
comp.create_sa_pe().to_verilog("sa_pe.v")
