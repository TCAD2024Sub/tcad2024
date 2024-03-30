from veriloggen import *
from math import ceil, log2
from src.python.util.hw_util import HwUtil


class HwComponents:
    """
        Collection of hardware components.
    """

    def __init__(self, ):
        self.cache = {}

    def create_fetch_data(self, input_data_width, output_data_width):
        """
                Creates a module for fetching data.

                Args:
                    input_data_width (int): Width of the input data.
                    output_data_width (int): Width of the output data.

                Returns:
                    Module: Fetch data module.
        """
        name = f'fetch_data_{input_data_width}_{output_data_width}'
        if name in self.cache.keys():
            return self.cache[name]
        m = Module(name)

        clk = m.Input('clk')
        start = m.Input('start')
        rst = m.Input('rst')

        request_read = m.OutputReg('request_read')
        data_valid = m.Input('data_valid')
        read_data = m.Input('read_data', input_data_width)

        pop_data = m.Input('pop_data')
        available_pop = m.OutputReg('available_pop')
        data_out = m.Output('data_out', output_data_width)

        num = input_data_width // output_data_width

        fsm_read = m.Reg('fsm_read', 1)
        fsm_control = m.Reg('fsm_control', 1)
        data = m.Reg('data', input_data_width)
        buffer = m.Reg('buffer', input_data_width)
        count = m.Reg('count', num)
        has_buffer = m.Reg('has_buffer')
        buffer_read = m.Reg('buffer_read')
        en = m.Reg('en')

        m.EmbeddedCode('')
        data_out.assign(data[0:output_data_width])

        m.Always(Posedge(clk))(
            If(rst)(
                en(Int(0, 1, 2))
            ).Else(
                en(Mux(en, en, start))
            )
        )

        m.Always(Posedge(clk))(
            If(rst)(
                fsm_read(0),
                request_read(0),
                has_buffer(0)
            ).Else(
                request_read(0),
                Case(fsm_read)(
                    When(0)(
                        If(en & data_valid)(
                            buffer(read_data),
                            request_read(1),
                            has_buffer(1),
                            fsm_read(1)
                        )
                    ),
                    When(1)(
                        If(buffer_read)(
                            has_buffer(0),
                            fsm_read(0)
                        )
                    )
                )
            )
        )

        m.Always(Posedge(clk))(
            If(rst)(
                fsm_control(0),
                available_pop(0),
                count(0),
                buffer_read(0)
            ).Else(
                buffer_read(0),
                Case(fsm_control)(
                    When(0)(
                        If(has_buffer)(
                            data(buffer),
                            count(1),
                            buffer_read(1),
                            available_pop(1),
                            fsm_control(1)
                        )
                    ),
                    When(1)(
                        If(pop_data & ~count[num - 1])(
                            count(count << 1),
                            data(data[output_data_width:]) if output_data_width < input_data_width else data(
                                data)
                        ),
                        If(pop_data & count[num - 1] & has_buffer)(
                            count(1),
                            data(buffer),
                            buffer_read(1)
                        ),
                        If(count[num - 1] & pop_data & ~has_buffer)(
                            count(count << 1),
                            data(data[output_data_width:]) if output_data_width < input_data_width else data(
                                data),
                            available_pop(0),
                            fsm_control(0)
                        )
                    )
                )
            )
        )

        HwUtil.initialize_regs(m)

        self.cache[name] = m
        return m

    def create_memory_1r_1w(self, simulate: bool = False) -> Module:
        name = 'mem_1r_1w'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        width = m.Parameter('width', 8)
        depth = m.Parameter('depth', 4)
        read_f = m.Parameter('read_f', 0)
        init_file = m.Parameter('init_file', 'mem_file.txt')
        write_f = m.Parameter('write_f', 0)
        output_file = m.Parameter('output_file', 'mem_out_file.txt')

        clk = m.Input('clk')
        rd = m.Input('rd')
        rd_addr = m.Input('rd_addr', depth)
        out = m.OutputReg('out', width)
        # out = m.Output('out', width)

        wr = m.Input('wr')
        wr_addr = m.Input('wr_addr', depth)
        wr_data = m.Input('wr_data', width)

        m.EmbeddedCode(f'(* ram_style = "M20K" *) reg [{width}-1:0] mem[0:2**{depth}-1];')
        m.EmbeddedCode('/*')
        mem = m.Reg('mem', width, Power(2, depth))
        m.EmbeddedCode('*/')

        # out.assign(mem[rd_addr])

        m.Always(Posedge(clk))(
            If(wr)(
                mem[wr_addr](wr_data)
            ),
            If(rd)(
                out(mem[rd_addr])
            ),
        )

        if simulate:
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

    def create_memory_2r_1w(self, simulate: bool = False) -> Module:
        name = 'mem_2r_1w'
        if name in self.cache.keys():
            return self.cache[name]

        m = Module(name)
        width = m.Parameter('width', 8)
        depth = m.Parameter('depth', 4)
        read_f = m.Parameter('read_f', 0)
        init_file = m.Parameter('init_file', 'mem_file.txt')
        write_f = m.Parameter('write_f', 0)
        output_file = m.Parameter('output_file', 'mem_out_file.txt')

        clk = m.Input('clk')
        rd = m.Input('rd')
        rd_addr0 = m.Input('rd_addr0', depth)
        rd_addr1 = m.Input('rd_addr1', depth)
        out0 = m.OutputReg('out0', width)
        out1 = m.OutputReg('out1', width)

        wr = m.Input('wr')
        wr_addr = m.Input('wr_addr', depth)
        wr_data = m.Input('wr_data', width)

        m.EmbeddedCode(f'(* ram_style = "M20K" *) reg [{width}-1:0] mem[0:2**{depth}-1];')
        m.EmbeddedCode('/*')
        mem = m.Reg('mem', width, Power(2, depth))
        m.EmbeddedCode('*/')

        # out0.assign(mem[rd_addr0])
        # out1.assign(mem[rd_addr1])

        m.Always(Posedge(clk))(
            If(wr)(
                mem[wr_addr](wr_data)
            ),
            If(rd)(
                out0(mem[rd_addr0]),
                out1(mem[rd_addr1]),
            ),
        )

        if simulate:
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

    def create_fifo(self) -> Module:
        name = 'fifo'
        if name in self.cache.keys():
            return self.cache[name]
        m = Module(name)
        FIFO_WIDTH = m.Parameter('FIFO_WIDTH', 32)
        FIFO_DEPTH_BITS = m.Parameter('FIFO_DEPTH_BITS', 8)
        FIFO_ALMOSTFULL_THRESHOLD = m.Parameter(
            'FIFO_ALMOSTFULL_THRESHOLD', Power(2, FIFO_DEPTH_BITS) - 4)
        FIFO_ALMOSTEMPTY_THRESHOLD = m.Parameter(
            'FIFO_ALMOSTEMPTY_THRESHOLD', 4)

        clk = m.Input('clk')
        rst = m.Input('rst')
        write_enable = m.Input('write_enable')
        input_data = m.Input('input_data', FIFO_WIDTH)
        output_read_enable = m.Input('output_read_enable')
        output_valid = m.OutputReg('output_valid')
        output_data = m.OutputReg('output_data', FIFO_WIDTH)
        empty = m.OutputReg('empty')
        almostempty = m.OutputReg('almostempty')
        full = m.OutputReg('full')
        almostfull = m.OutputReg('almostfull')
        data_count = m.OutputReg('data_count', FIFO_DEPTH_BITS + 1)

        read_pointer = m.Reg('read_pointer', FIFO_DEPTH_BITS)
        write_pointer = m.Reg('write_pointer', FIFO_DEPTH_BITS)

        # m.EmbeddedCode(
        #    '(*rom_style = "block" *) reg [FIFO_WIDTH-1:0] mem[0:2**FIFO_DEPTH_BITS-1];')
        # m.EmbeddedCode('/*')
        mem = m.Reg('mem', FIFO_WIDTH, Power(2, FIFO_DEPTH_BITS))
        # m.EmbeddedCode('*/')

        m.Always(Posedge(clk))(
            If(rst)(
                empty(1),
                almostempty(1),
                full(0),
                almostfull(0),
                read_pointer(0),
                write_pointer(0),
                data_count(0)
            ).Else(
                Case(Cat(write_enable, output_read_enable))(
                    When(3)(
                        read_pointer(read_pointer + 1),
                        write_pointer(write_pointer + 1),
                    ),
                    When(2)(
                        If(~full)(
                            write_pointer(write_pointer + 1),
                            data_count(data_count + 1),
                            empty(0),
                            If(data_count == (FIFO_ALMOSTEMPTY_THRESHOLD - 1))(
                                almostempty(0)
                            ),
                            If(data_count == Power(2, FIFO_DEPTH_BITS) - 1)(
                                full(1)
                            ),
                            If(data_count == (FIFO_ALMOSTFULL_THRESHOLD - 1))(
                                almostfull(1)
                            )
                        )
                    ),
                    When(1)(
                        If(~empty)(
                            read_pointer(read_pointer + 1),
                            data_count(data_count - 1),
                            full(0),
                            If(data_count == FIFO_ALMOSTFULL_THRESHOLD)(
                                almostfull(0)
                            ),
                            If(data_count == 1)(
                                empty(1)
                            ),
                            If(data_count == FIFO_ALMOSTEMPTY_THRESHOLD)(
                                almostempty(1)
                            )
                        )
                    ),
                )
            )
        )
        m.Always(Posedge(clk))(
            If(rst)(
                output_valid(0)
            ).Else(
                output_valid(0),
                If(write_enable == 1)(
                    mem[write_pointer](input_data)
                ),
                If(output_read_enable == 1)(
                    output_data(mem[read_pointer]),
                    output_valid(1)
                )
            )
        )
        self.cache[name] = m
        return m
