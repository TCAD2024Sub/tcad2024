from math import ceil, log2, sqrt

from veriloggen import *
from src.python.util.hw_util import HwUtil as Vu
from src.python.util.per_graph import PeRGraph


class SAComponents:
    def __init__(
            self,
            proj_graph: PeRGraph,
            base_path: str,
            parent_name: str,
            n_neighbors: int = 4,
            align_bits: int = 8,
    ):
        self.proj_graph = proj_graph
        self.base_path = base_path
        self.parent_name = parent_name
        self.n_neighbors = n_neighbors
        self.align_bits = align_bits

        self.cell_bits = ceil(log2(self.proj_graph.n_cells))
        self.node_bits = self.cell_bits
        self.lines = self.columns = int(sqrt(self.proj_graph.n_cells))
        self.dist_bits = self.cell_bits + ceil(log2(self.n_neighbors * 2))
        self.lc_bits = ceil(log2(self.lines)) * 2

        self.cache = {}

    # FIXME
    def create_memory_2r_1w(self, width, depth) -> Module:
        name = 'mem_2r_1w_width%d_depth%d' % (width, depth)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        read_f = m.Parameter('read_f', 0)
        init_file = m.Parameter('init_file', 'mem_file.txt')
        write_f = m.Parameter('write_f', 0)
        output_file = m.Parameter('output_file', 'mem_out_file.txt')
        width = m.Parameter('width', 8)
        depth = m.Parameter('depth', 3)

        clk = m.Input('clk')
        rd = m.Input('rd')
        rd_addr0 = m.Input('rd_addr0', depth)
        rd_addr1 = m.Input('rd_addr1', depth)
        out0 = m.Output('out0', width)
        out1 = m.Output('out1', width)

        wr = m.Input('wr')
        wr_addr = m.Input('wr_addr', depth)
        wr_data = m.Input('wr_data', width)

        # m.EmbeddedCode(
        #    '(*rom_style = "block" *) reg [%d-1:0] mem[0:2**%d-1];' % (width, depth))
        # m.EmbeddedCode('/*')
        mem = m.Reg('mem', width, Power(2, depth))
        # m.EmbeddedCode('*/')

        # FIXME
        out0.assign(Mux(rd, mem[rd_addr0], Int(0, width, 10)))
        out1.assign(Mux(rd, mem[rd_addr1], Int(0, width, 10)))

        m.Always(Posedge(clk))(
            If(wr)(
                mem[wr_addr](wr_data)
            ),
        )

        m.EmbeddedCode('//synthesis translate_off')
        m.Always(Posedge(clk))(
            If(AndList(wr, write_f))(
                Systask('writememb', output_file, mem)
            ),
        )
        m.EmbeddedCode('//synthesis translate_on')

        m.Initial(
            If(read_f)(
                Systask('readmemb', init_file, mem),
            )
        )
        self.cache[name] = m
        return m

    def create_lc_table(self) -> Module:
        # LC table.
        # Finds the line/column values for each cell
        n_cells = self.proj_graph.n_cells
        cell_bits = self.cell_bits
        lines = self.lines
        columns = self.columns
        lc_bits = self.lc_bits

        name = 'lc_table_%d_%d' % (lines, columns)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        ca = m.Input('ca', cell_bits)
        cb = m.Input('cb', cell_bits)
        lca = m.Output('lca', lc_bits)
        lcb = m.Output('lcb', lc_bits)

        lc_table = m.Wire('lc_table', lc_bits, n_cells)

        lca.assign(lc_table[ca])
        lcb.assign(lc_table[cb])

        counter = 0
        for line in range(lines):
            for column in range(columns):
                w = lc_bits // 2
                lc_table[counter].assign(Cat(Int(line, w, 10), Int(column, w, 10)))
                counter += 1

        Vu.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_distance_table(self) -> Module:
        # manhattan
        lines = self.lines
        columns = self.columns
        dist_bits = self.dist_bits
        lc_bits = self.lc_bits
        w = lc_bits // 2

        name = 'distance_table_%d_%d' % (lines, columns)
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        opa0 = m.Input('opa0', lc_bits)
        opa1 = m.Input('opa1', lc_bits)
        opa_v = m.Input('opa_v')
        opb_0 = m.Input('opb_0', lc_bits)
        opb_1 = m.Input('opb_1', lc_bits)
        opb_v = m.Input('opb_v')
        da = m.Output('da', dist_bits)
        db = m.Output('db', dist_bits)

        dist_table = m.Wire('dist_table', dist_bits, Power(2, lc_bits))

        da_t = m.Wire('da_t', dist_bits)
        db_t = m.Wire('db_t', dist_bits)

        m.EmbeddedCode('')
        da_t.assign(dist_table[Cat(opa1[:w], opa0[:w])] +
                    dist_table[Cat(opa1[w:], opa0[w:])])
        db_t.assign(dist_table[Cat(opb_1[:w], opb_0[:w])] +
                    dist_table[Cat(opb_1[w:], opb_0[w:])])

        m.EmbeddedCode('')
        da.assign(Mux(opa_v, da_t, 0))
        db.assign(Mux(opb_v, db_t, 0))

        m.EmbeddedCode('')
        for i in range(lines):
            for j in range(lines):
                dist_table[(i << w) | j].assign(abs(i - j))

        Vu.initialize_regs(m)
        self.cache[name] = m
        return m

    def create_sa_fsm_single_thread(self):
        n_cells = self.proj_graph.n_cells
        n_cells_sqrt = self.proj_graph.n_cells_sqrt
        n_neighbors = self.n_neighbors
        cell_bits = self.cell_bits
        node_bits = self.node_bits
        lc_bits = self.lc_bits
        dist_bits = self.dist_bits
        base_path = self.base_path
        parent_name = self.parent_name

        name = 'sa_single_%dcells' % n_cells
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)

        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        n_exec = m.Input('n_exec', 10)
        done = m.OutputReg('done')

        conf_c2n_rd = m.Input('conf_c2n_rd')
        conf_c2n_rd_addr = m.Input('conf_c2n_rd_addr', cell_bits)
        conf_c2n_rd_data = m.Output('conf_c2n_rd_data', node_bits + 1)

        conf_wr = m.Input('conf_wr')

        conf_c2n_wr = m.Input('conf_c2n_wr')
        conf_c2n_wr_addr = m.Input('conf_c2n_wr_addr', cell_bits)
        conf_c2n_wr_data = m.Input('conf_c2n_wr_data', node_bits + 1)

        conf_n_wr = m.Input('conf_n_wr', n_neighbors)
        conf_n_wr_addr = m.Input('conf_n_wr_addr', node_bits)
        conf_n_wr_data = m.Input('conf_n_wr_data', node_bits + 1)

        conf_n2c_wr = m.Input('conf_n2c_wr', n_neighbors)
        conf_n2c_wr_addr = m.Input('conf_n2c_wr_addr', cell_bits)
        conf_n2c_wr_data = m.Input('conf_n2c_wr_data', node_bits)

        n_exec_counter = m.Reg('n_exec_counter', n_exec.width + 1)

        m.EmbeddedCode('// SA single thread states declaration')
        fsm_sa = m.Reg('fsm_sa', 4)
        select_cells = m.Localparam('select_cells', Int(0, fsm_sa.width, 10))
        cell_to_nodes = m.Localparam('cell_to_nodes', Int(1, fsm_sa.width, 10))
        neighborhood = m.Localparam('neighborhood', Int(2, fsm_sa.width, 10))
        nodes_to_cell = m.Localparam('nodes_to_cell', Int(3, fsm_sa.width, 10))
        line_column_finder = m.Localparam('line_column_finder', Int(4, fsm_sa.width, 10))
        distance_calculator = m.Localparam('distance_calculator', Int(5, fsm_sa.width, 10))
        sum_reduction_p = m.Localparam('sum_reduction_p', Int(6, fsm_sa.width, 10))
        sum_reduction = m.Localparam('sum_reduction', Int(7, fsm_sa.width, 10))
        total_cost = m.Localparam('total_cost', Int(8, fsm_sa.width, 10))
        decision = m.Localparam('decision', Int(9, fsm_sa.width, 10))
        write_a = m.Localparam('write_a', Int(10, fsm_sa.width, 10))
        write_b = m.Localparam('write_b', Int(11, fsm_sa.width, 10))
        end = m.Localparam('end', Int(12, fsm_sa.width, 10))
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// select cells stage variables')
        ca = m.Reg('ca', cell_bits)
        cb = m.Reg('cb', cell_bits)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// cell to nodes stage variables')
        na = m.Reg('na', node_bits)
        na_v = m.Reg('na_v')
        nb = m.Reg('nb', node_bits)
        nb_v = m.Reg('nb_v')
        na_t = m.Wire('na_t', node_bits)
        na_v_t = m.Wire('na_v_t')
        nb_t = m.Wire('nb_t', node_bits)
        nb_v_t = m.Wire('nb_v_t')
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// neighborhood stage variables')
        va = m.Reg('va', node_bits * n_neighbors)
        va_v = m.Reg('va_v', n_neighbors)
        vb = m.Reg('vb', node_bits * n_neighbors)
        vb_v = m.Reg('vb_v', n_neighbors)
        va_t = m.Wire('va_t', node_bits * n_neighbors)
        va_v_t = m.Wire('va_v_t', n_neighbors)
        va_v_m = m.Wire('va_v_m', n_neighbors)
        vb_t = m.Wire('vb_t', node_bits * n_neighbors)
        vb_v_t = m.Wire('vb_v_t', n_neighbors)
        vb_v_m = m.Wire('vb_v_m', n_neighbors)

        m.EmbeddedCode('')
        m.EmbeddedCode('//here we guarantee that only valid nodes can give us neighbors ')
        va_v_t.assign(Mux(na_v, va_v_m, Int(0, n_neighbors, 2)))
        vb_v_t.assign(Mux(nb_v, vb_v_m, Int(0, n_neighbors, 2)))
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// node to cell stage variables')
        cva_v = m.Reg('cva_v', n_neighbors)
        cva = m.Reg('cva', cell_bits * n_neighbors)
        cvb_v = m.Reg('cvb_v', n_neighbors)
        cvb = m.Reg('cvb', cell_bits * n_neighbors)
        cva_v_t = m.Wire('cva_v_t', n_neighbors)
        cva_t = m.Wire('cva_t', cell_bits * n_neighbors)
        cvb_v_t = m.Wire('cvb_v_t', n_neighbors)
        cvb_t = m.Wire('cvb_t', cell_bits * n_neighbors)

        m.EmbeddedCode('')
        m.EmbeddedCode('// This is only for legibility')
        cva_v_t.assign(va_v)
        cvb_v_t.assign(vb_v)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// line column finder stage variables')
        lc_a = m.Reg('lc_a', lc_bits)
        lc_b = m.Reg('lc_b', lc_bits)
        lc_va = m.Reg('lc_va', lc_bits * n_neighbors)
        lc_va_v = m.Reg('lc_va_v', n_neighbors)
        lc_vb = m.Reg('lc_vb', lc_bits * n_neighbors)
        lc_vb_v = m.Reg('lc_vb_v', n_neighbors)

        lc_a_t = m.Wire('lc_a_t', lc_bits)
        lcb_t = m.Wire('lcb_t', lc_bits)
        lc_va_t = m.Wire('lc_va_t', lc_bits * n_neighbors)
        lc_vb_t = m.Wire('lc_vb_t', lc_bits * n_neighbors)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// Distance calculator stage variables')
        m.EmbeddedCode('// Before changes')
        dva_before = m.Reg('dva_before', n_neighbors * dist_bits)
        dvb_before = m.Reg('dvb_before', n_neighbors * dist_bits)
        lca_before = m.Wire('lca_before', lc_bits)
        lcb_before = m.Wire('lcb_before', lc_bits)
        dva_before_t = m.Wire('dva_before_t', n_neighbors * dist_bits)
        dvb_before_t = m.Wire('dvb_before_t', n_neighbors * dist_bits)

        m.EmbeddedCode('')
        lca_before.assign(lc_a)
        lcb_before.assign(lc_b)

        m.EmbeddedCode('')
        m.EmbeddedCode('// After changes')
        dva_after = m.Reg('dva_after', n_neighbors * dist_bits)
        dvb_after = m.Reg('dvb_after', n_neighbors * dist_bits)
        lca_after = m.Wire('lca_after', lc_bits)
        lcb_after = m.Wire('lcb_after', lc_bits)
        opva_after = m.Wire('opva_after', lc_bits * n_neighbors)
        opvb_after = m.Wire('opvb_after', lc_bits * n_neighbors)
        dva_after_t = m.Wire('dva_after_t', n_neighbors * dist_bits)
        dvb_after_t = m.Wire('dvb_after_t', n_neighbors * dist_bits)

        m.EmbeddedCode('')
        lca_after.assign(lc_b)
        lcb_after.assign(lc_a)
        for i in range(n_neighbors):
            opva_after[i * lc_bits:lc_bits * (i + 1)].assign(
                Mux(lc_va[i * lc_bits:lc_bits * (i + 1)]
                    == lca_after, lcb_after,
                    lc_va[i * lc_bits:lc_bits * (i + 1)])
            )

        for i in range(n_neighbors):
            opvb_after[i * lc_bits:lc_bits * (i + 1)].assign(
                Mux(lc_vb[i * lc_bits:lc_bits * (i + 1)]
                    == lcb_after, lca_after,
                    lc_vb[i * lc_bits:lc_bits * (i + 1)])
            )
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// Sum Reduction stage variables')
        m.EmbeddedCode('// Sum Before change')
        sum_dva_before_p = m.Reg('sum_dva_before_p', n_neighbors // 2 * dist_bits)
        sum_dva_before_p_t = m.Wire('sum_dva_before_p_t', n_neighbors // 2 * dist_bits)
        sum_dvb_before_p = m.Reg('sum_dvb_before_p', n_neighbors // 2 * dist_bits)
        sum_dvb_before_p_t = m.Wire('sum_dvb_before_p_t', n_neighbors // 2 * dist_bits)

        sum_dva_before = m.Reg('sum_dva_before', dist_bits)
        sum_dva_before_t = m.Wire('sum_dva_before_t', dist_bits)
        sum_dvb_before = m.Reg('sum_dvb_before', dist_bits)
        sum_dvb_before_t = m.Wire('sum_dvb_before_t', dist_bits)

        m.EmbeddedCode('')
        for i in range(0, (n_neighbors // 2) + 1, 2):
            n = i // 2
            sum_dva_before_p_t[n * dist_bits:dist_bits * (n + 1)].assign(
                dva_before[i * dist_bits:dist_bits * (i + 1)] + dva_before[dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(0, (n_neighbors // 2) + 1, 2):
            n = i // 2
            sum_dvb_before_p_t[n * dist_bits:dist_bits * (n + 1)].assign(
                dvb_before[i * dist_bits:dist_bits * (i + 1)] + dvb_before[dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(0, (n_neighbors // 4) + 1, 2):
            n = i // 2
            sum_dva_before_t[n * dist_bits:dist_bits * (n + 1)].assign(
                sum_dva_before_p[i * dist_bits:dist_bits * (i + 1)] + sum_dva_before_p[
                                                                      dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(0, (n_neighbors // 4) + 1, 2):
            n = i // 2
            sum_dvb_before_t[n * dist_bits:dist_bits * (n + 1)].assign(
                sum_dvb_before_p[i * dist_bits:dist_bits * (i + 1)] + sum_dvb_before_p[
                                                                      dist_bits * (i + 1):dist_bits * (i + 2)])

        m.EmbeddedCode('')
        m.EmbeddedCode('// Sum after change')
        sum_dva_after_p = m.Reg('sum_dva_after_p', n_neighbors // 2 * dist_bits)
        sum_dva_after_p_t = m.Wire('sum_dva_after_p_t', n_neighbors // 2 * dist_bits)
        sum_dvb_after_p = m.Reg('sum_dvb_after_p', n_neighbors // 2 * dist_bits)
        sum_dvb_after_p_t = m.Wire('sum_dvb_after_p_t', n_neighbors // 2 * dist_bits)

        sum_dva_after = m.Reg('sum_dva_after', dist_bits)
        sum_dva_after_t = m.Wire('sum_dva_after_t', dist_bits)
        sum_dvb_after = m.Reg('sum_dvb_after', dist_bits)
        sum_dvb_after_t = m.Wire('sum_dvb_after_t', dist_bits)

        m.EmbeddedCode('')
        for i in range(0, (n_neighbors // 2) + 1, 2):
            n = i // 2
            sum_dva_after_p_t[n * dist_bits:dist_bits * (n + 1)].assign(
                dva_after[i * dist_bits:dist_bits * (i + 1)] + dva_after[dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(0, (n_neighbors // 2) + 1, 2):
            n = i // 2
            sum_dvb_after_p_t[n * dist_bits:dist_bits * (n + 1)].assign(
                dvb_after[i * dist_bits:dist_bits * (i + 1)] + dvb_after[dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(0, (n_neighbors // 4) + 1, 2):
            n = i // 2
            sum_dva_after_t[n * dist_bits:dist_bits * (n + 1)].assign(
                sum_dva_after_p[i * dist_bits:dist_bits * (i + 1)] + sum_dva_after_p[
                                                                     dist_bits * (i + 1):dist_bits * (i + 2)])

        for i in range(0, (n_neighbors // 4) + 1, 2):
            n = i // 2
            sum_dvb_after_t[n * dist_bits:dist_bits * (n + 1)].assign(
                sum_dvb_after_p[i * dist_bits:dist_bits * (i + 1)] + sum_dvb_after_p[
                                                                     dist_bits * (i + 1):dist_bits * (i + 2)])
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// Total cost stage variables')
        total_cost_before = m.Reg('total_cost_before', dist_bits)
        total_cost_before_t = m.Wire('total_cost_before_t', dist_bits)
        total_cost_after = m.Reg('total_cost_after', dist_bits)
        total_cost_after_t = m.Wire('total_cost_after_t', dist_bits)

        m.EmbeddedCode('')
        total_cost_before_t.assign(sum_dva_before + sum_dvb_before)
        total_cost_after_t.assign(sum_dva_after + sum_dvb_after)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// Decision stage variables')
        decision = m.Wire('decision')

        m.EmbeddedCode('')
        decision.assign(total_cost_after < total_cost_before)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// Write a and b cost stage variables')
        fsm_c2n_wr_signal = m.Reg('fsm_c2n_wr_signal')
        fsm_n2c_wr_signal = m.Reg('fsm_n2c_wr_signal')
        fsm_mem_c2n_wr_addr = m.Reg('fsm_mem_c2n_wr_addr', cell_bits)
        fsm_mem_c2n_wr_data = m.Reg('fsm_mem_c2n_wr_data', node_bits + 1)
        fsm_mem_n2c_wr_addr = m.Reg('fsm_mem_n2c_wr_addr', node_bits)
        fsm_mem_n2c_wr_data = m.Reg('fsm_mem_n2c_wr_data', cell_bits)

        mem_c2n_rd_addr = m.Wire('mem_c2n_rd_addr', cell_bits)

        mem_c2n_wr = m.Wire('mem_c2n_wr')
        mem_c2n_wr_addr = m.Wire('mem_c2n_wr_addr', cell_bits)
        mem_c2n_wr_data = m.Wire('mem_c2n_wr_data', node_bits + 1)

        mem_n_wr = m.Wire('mem_n_wr', n_neighbors)
        mem_n_wr_addr = m.Wire('mem_n_wr_addr', node_bits)
        mem_n_wr_data = m.Wire('mem_n_wr_data', node_bits + 1)

        mem_n2c_wr = m.Wire('mem_n2c_wr', n_neighbors)
        mem_n2c_wr_addr = m.Wire('mem_n2c_wr_addr', node_bits)
        mem_n2c_wr_data = m.Wire('mem_n2c_wr_data', cell_bits)

        m.EmbeddedCode('')
        mem_c2n_wr.assign(Mux(conf_wr, conf_c2n_wr, fsm_c2n_wr_signal))
        mem_c2n_wr_addr.assign(Mux(conf_wr, conf_c2n_wr_addr, fsm_mem_c2n_wr_addr))
        mem_c2n_wr_data.assign(Mux(conf_wr, conf_c2n_wr_data, fsm_mem_c2n_wr_data))

        m.EmbeddedCode('')
        mem_n_wr.assign(conf_n_wr)
        mem_n_wr_addr.assign(conf_n_wr_addr)
        mem_n_wr_data.assign(conf_n_wr_data)

        m.EmbeddedCode('')
        mem_n2c_wr.assign(Mux(conf_wr, conf_n2c_wr, Repeat(fsm_n2c_wr_signal, n_neighbors)))
        mem_n2c_wr_addr.assign(Mux(conf_wr, conf_n2c_wr_addr, fsm_mem_n2c_wr_addr))
        mem_n2c_wr_data.assign(Mux(conf_wr, conf_n2c_wr_data, fsm_mem_n2c_wr_data))

        m.EmbeddedCode('')
        mem_c2n_rd_addr.assign(Mux(conf_c2n_rd, conf_c2n_rd_addr, ca))
        conf_c2n_rd_data.assign(Cat(na_v_t, na_t))
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// SA single thread FSM')
        m.Always(Posedge(clk))(
            If(rst)(
                done(Int(0, 1, 10)),
                n_exec_counter(Int(0, n_exec_counter.width, 10)),
                ca(Int(0, ca.width, 10)),
                cb(Int(0, cb.width, 10)),
                na(Int(0, na.width, 10)),
                na_v(Int(0, 1, 10)),
                nb(Int(0, nb.width, 10)),
                nb_v(Int(0, 1, 10)),
                va(Int(0, va.width, 10)),
                va_v(Int(0, va_v.width, 10)),
                vb(Int(0, vb.width, 10)),
                vb_v(Int(0, vb_v.width, 10)),
                lc_a(Int(0, lc_a.width, 10)),
                lc_b(Int(0, lc_b.width, 10)),
                lc_va(Int(0, lc_va.width, 10)),
                lc_va_v(Int(0, lc_va_v.width, 10)),
                lc_vb(Int(0, lc_vb.width, 10)),
                lc_vb_v(Int(0, lc_vb_v.width, 10)),
                dva_before(Int(0, dva_before.width, 10)),
                dvb_before(Int(0, dvb_before.width, 10)),
                dva_after(Int(0, dva_after.width, 10)),
                dvb_after(Int(0, dvb_after.width, 10)),
                sum_dva_before_p(Int(0, sum_dva_before_p.width, 10)),
                sum_dvb_before_p(Int(0, sum_dvb_before_p.width, 10)),
                sum_dva_after_p(Int(0, sum_dva_after_p.width, 10)),
                sum_dvb_after_p(Int(0, sum_dvb_after_p.width, 10)),
                sum_dva_before(Int(0, sum_dva_before.width, 10)),
                sum_dvb_before(Int(0, sum_dvb_before.width, 10)),
                sum_dva_after(Int(0, sum_dva_after.width, 10)),
                sum_dvb_after(Int(0, sum_dvb_after.width, 10)),
                total_cost_before(Int(0, total_cost_before.width, 10)),
                total_cost_after(Int(0, total_cost_after.width, 10)),
                fsm_c2n_wr_signal(Int(0, 1, 10)),
                fsm_n2c_wr_signal(Int(0, 1, 10)),
                fsm_mem_c2n_wr_addr(Int(0, fsm_mem_c2n_wr_addr.width, 10)),
                fsm_mem_c2n_wr_data(Int(0, fsm_mem_c2n_wr_data.width, 10)),
                fsm_mem_n2c_wr_addr(Int(0, fsm_mem_n2c_wr_addr.width, 10)),
                fsm_mem_n2c_wr_data(Int(0, fsm_mem_n2c_wr_data.width, 10)),
                fsm_sa(cell_to_nodes),
            ).Elif(start)(
                fsm_c2n_wr_signal(Int(0, 1, 10)),
                fsm_n2c_wr_signal(Int(0, 1, 10)),
                Case(fsm_sa)(
                    When(select_cells)(
                        If(ca == Int(n_cells_sqrt, ca.width, 10))(
                            ca(Int(0, ca.width, 10)),
                            If(cb == Int(n_cells_sqrt, cb.width, 10))(
                                cb(Int(0, cb.width, 10)),
                                n_exec_counter(n_exec_counter + Int(1, n_exec_counter.width, 10)),
                                fsm_sa(end)
                            ).Else(
                                cb(cb + Int(1, cb.width, 10)),
                                fsm_sa(cell_to_nodes),
                            )
                        ).Else(
                            ca(ca + Int(1, ca.width, 10)),
                            fsm_sa(cell_to_nodes),
                        ),
                    ),
                    When(cell_to_nodes)(
                        If(Uand(Cat(~na_v_t, ~nb_v_t)))(
                            fsm_sa(select_cells),
                        ).Else(
                            na(na_t),
                            na_v(na_v_t),
                            nb(nb_t),
                            nb_v(nb_v_t),
                            fsm_sa(neighborhood),
                        ),
                    ),
                    When(neighborhood)(
                        va(va_t),
                        va_v(va_v_t),
                        vb(vb_t),
                        vb_v(vb_v_t),
                        fsm_sa(nodes_to_cell),
                    ),
                    When(nodes_to_cell)(
                        cva_v(cva_v_t),
                        cva(cva_t),
                        cvb_v(cvb_v_t),
                        cvb(cvb),
                        fsm_sa(line_column_finder)
                    ),
                    When(line_column_finder)(
                        lc_a(lc_a_t),
                        lc_b(lcb_t),
                        lc_va(lc_va_t),
                        lc_va_v(cva_v),
                        lc_vb(lc_vb_t),
                        lc_vb_v(cvb_v),
                        fsm_sa(distance_calculator),
                    ),
                    When(distance_calculator)(
                        dva_before(dva_before_t),
                        dvb_before(dvb_before_t),
                        dva_after(dva_after_t),
                        dvb_after(dvb_after_t),
                        fsm_sa(sum_reduction_p)
                    ),
                    When(sum_reduction_p)(
                        sum_dva_before_p(sum_dva_before_p_t),
                        sum_dvb_before_p(sum_dvb_before_p_t),
                        sum_dva_after_p(sum_dva_after_p_t),
                        sum_dvb_after_p(sum_dvb_after_p_t),
                        fsm_sa(sum_reduction)
                    ),
                    When(sum_reduction)(
                        sum_dva_before(sum_dva_before_t),
                        sum_dvb_before(sum_dvb_before_t),
                        sum_dva_after(sum_dva_after_t),
                        sum_dvb_after(sum_dvb_after_t),
                        fsm_sa(total_cost)
                    ),
                    When(total_cost)(
                        total_cost_before(total_cost_before_t),
                        total_cost_after(total_cost_after_t),
                        fsm_sa(decision)
                    ),
                    When(decision)(
                        If(decision)(
                            fsm_sa(write_a),
                        ).Else(
                            fsm_sa(select_cells)
                        ),
                    ),
                    When(write_a)(
                        fsm_c2n_wr_signal(Int(1, 1, 10)),
                        fsm_mem_c2n_wr_addr(cb),
                        fsm_mem_c2n_wr_data(Cat(na_v, na)),
                        fsm_n2c_wr_signal(na_v),
                        fsm_mem_n2c_wr_addr(na),
                        fsm_mem_n2c_wr_data(cb),
                        fsm_sa(write_b)
                    ),
                    When(write_b)(
                        fsm_c2n_wr_signal(Int(1, 1, 10)),
                        fsm_mem_c2n_wr_addr(ca),
                        fsm_mem_c2n_wr_data(Cat(nb_v, nb)),
                        fsm_n2c_wr_signal(nb_v),
                        fsm_mem_n2c_wr_addr(nb),
                        fsm_mem_n2c_wr_data(ca),
                        fsm_sa(select_cells)
                    ),
                    When(end)(
                        If(n_exec_counter == n_exec)(
                            fsm_sa(select_cells)
                        ).Else(
                            done(Int(1, 1, 10))
                        ),

                    ),
                )
            )
        )

        m.EmbeddedCode('// cell to nodes stage memory instantiation')
        par = [
            ('READ_F', 1),
            ('INIT_FILE', base_path + '/verilog/' + parent_name + '_c_n.rom'),
            ('WRITE_F', 1),
            ('OUTPUT_FILE', base_path + '/verilog/' + parent_name + '_c_n_out.rom')
        ]
        con = [
            ('clk', clk),
            ('rd', Int(1, 1, 10)),
            ('rd_addr0', ca),
            ('rd_addr1', cb),
            ('out0', Cat(na_v_t, na_t)),
            ('out1', Cat(nb_v_t, nb_t)),
            ('wr', mem_c2n_wr),
            ('wr_addr', mem_c2n_wr_addr),
            ('wr_data', mem_c2n_wr_data),
        ]
        aux = self.create_memory_2r_1w(node_bits + 1, cell_bits)
        m.Instance(aux, aux.name, par, con)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// neighborhood stage memory instantiation')
        for i in range(n_neighbors):
            par = [
                ('READ_F', 1),
                ('INIT_FILE', base_path + '/verilog/' + parent_name + '_n%d.rom' % i),
                ('WRITE_F', 0)
            ]
            con = [
                ('clk', clk),
                ('rd', Int(1, 1, 10)),
                ('rd_addr0', na),
                ('rd_addr1', nb),
                ('out0', Cat(va_v_m[i], va_t[node_bits * i:node_bits * (i + 1)])),
                ('out1', Cat(vb_v_m[i], vb_t[node_bits * i:node_bits * (i + 1)])),
                ('wr', mem_n_wr[i]),
                ('wr_addr', mem_n_wr_addr),
                ('wr_data', mem_n_wr_data),
            ]
            aux = self.create_memory_2r_1w(node_bits + 1, node_bits)
            m.Instance(aux, '%s_%i' % (aux.name, i), par, con)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// node to cell stage memory instantiation')
        for i in range(n_neighbors):
            par = [
                ('READ_F', 1),
                ('INIT_FILE', base_path + '/verilog/' + parent_name + '_n_c.rom'),
                ('WRITE_F', 1 if i == 0 else 0),
                ('OUTPUT_FILE', base_path + '/verilog/' + parent_name + '_n_c_out%d.rom' % i)
            ]
            con = [
                ('clk', clk),
                ('rd', Int(1, 1, 10)),
                ('rd_addr0', va[i * node_bits:node_bits * (i + 1)]),
                ('rd_addr1', vb[i * node_bits:node_bits * (i + 1)]),
                ('out0', cva_t[i * cell_bits:cell_bits * (i + 1)]),
                ('out1', cvb_t[i * cell_bits:cell_bits * (i + 1)]),
                ('wr', mem_n2c_wr[i]),
                ('wr_addr', mem_n2c_wr_addr),
                ('wr_data', mem_n2c_wr_data),
            ]
            aux = self.create_memory_2r_1w(cell_bits, node_bits)
            m.Instance(aux, '%s_%d' % (aux.name, i), par, con)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// line column finder stage lc_table instantiation')
        aux = self.create_lc_table()
        par = []
        con = [
            ('ca', ca),
            ('cb', cb),
            ('lc_a', lc_a_t),
            ('lc_b', lcb_t),
        ]
        m.Instance(aux, "%s_c" % aux.name, par, con)

        for i in range(n_neighbors):
            par = []
            con = [
                ('ca', cva[i * cell_bits:cell_bits * (i + 1)]),
                ('cb', cvb[i * cell_bits:cell_bits * (i + 1)]),
                ('lc_a', lc_va_t[i * lc_bits:lc_bits * (i + 1)]),
                ('lc_b', lc_vb_t[i * lc_bits:lc_bits * (i + 1)]),
            ]
            m.Instance(aux, '%s_v_%d' % (aux.name, i), par, con)
        m.EmbeddedCode('// #####')

        m.EmbeddedCode('')
        m.EmbeddedCode('// Distance calculator stage distance tables instantiation')
        m.EmbeddedCode('// Distance before change')
        for i in range(0, (n_neighbors // 2) + 1, 2):
            par = []
            con = [
                ('opa0', lca_before),
                ('opa1', lc_va[i * lc_bits:lc_bits * (i + 1)]),
                ('opav', lc_va_v[i]),
                ('opb0', lca_before),
                ('opb1', lc_va[lc_bits * (i + 1):lc_bits * (i + 2)]),
                ('opbv', lc_va_v[i + 1]),
                ('da', dva_before_t[i * dist_bits:dist_bits * (i + 1)]),
                ('db', dva_before_t[dist_bits * (i + 1):dist_bits * (i + 2)]),
            ]
            aux = self.create_distance_table()
            m.Instance(aux, '%s_dac_%d' % (aux.name, (i // 2)), par, con)

        for i in range(0, (n_neighbors // 2) + 1, 2):
            par = []
            con = [
                ('opa0', lcb_before),
                ('opa1', lc_vb[i * lc_bits:lc_bits * (i + 1)]),
                ('opav', lc_vb_v[i]),
                ('opb0', lcb_before),
                ('opb1', lc_vb[lc_bits * (i + 1):lc_bits * (i + 2)]),
                ('opbv', lc_vb_v[i + 1]),
                ('da', dvb_before_t[i * dist_bits:dist_bits * (i + 1)]),
                ('db', dvb_before_t[dist_bits * (i + 1):dist_bits * (i + 2)]),
            ]
            aux = self.create_distance_table()
            m.Instance(aux, '%s_dbc_%d' % (aux.name, (i // 2)), par, con)

        m.EmbeddedCode('')
        m.EmbeddedCode('// Distance after change')
        for i in range(0, (n_neighbors // 2) + 1, 2):
            par = []
            con = [
                ('opa0', lca_after),
                ('opa1', opva_after[i * lc_bits:lc_bits * (i + 1)]),
                ('opav', lc_va_v[i]),
                ('opb0', lca_after),
                ('opb1', opva_after[lc_bits * (i + 1):lc_bits * (i + 2)]),
                ('opbv', lc_va_v[i + 1]),
                ('da', dva_after_t[i * dist_bits:dist_bits * (i + 1)]),
                ('db', dva_after_t[dist_bits * (i + 1):dist_bits * (i + 2)]),
            ]
            aux = self.create_distance_table()
            m.Instance(aux, '%s_das_%d' % (aux.name, (i // 2)), par, con)

        for i in range(0, (n_neighbors // 2) + 1, 2):
            par = []
            con = [
                ('opa0', lcb_after),
                ('opa1', opvb_after[i * lc_bits:lc_bits * (i + 1)]),
                ('opav', lc_vb_v[i]),
                ('opb0', lcb_after),
                ('opb1', opvb_after[lc_bits * (i + 1):lc_bits * (i + 2)]),
                ('opbv', lc_vb_v[i + 1]),
                ('da', dvb_after_t[i * dist_bits:dist_bits * (i + 1)]),
                ('db', dvb_after_t[dist_bits * (i + 1):dist_bits * (i + 2)]),
            ]
            aux = self.create_distance_table()
            m.Instance(aux, '%s_dbs_%d' % (aux.name, (i // 2)), par, con)
        m.EmbeddedCode('// #####')

        Vu.initialize_regs(m)

        self.cache[name] = m

        return m
