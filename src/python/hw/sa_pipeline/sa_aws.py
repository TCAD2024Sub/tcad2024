from veriloggen import *
import src.python.hw.sa_fsm.sa_components as _sa
import src.python.hw.sa_pipeline.util as _u
from math import ceil, log2, sqrt


class SaAws:

    def get(self, sa_graph: _u.SaGraph, bus_width):
        self.sa_graph = sa_graph
        # self.copies = copies
        self.bus_width = bus_width
        self.pipe_width = 16
        self.sa_components = _sa.SAComponents(sa_graph)
        return self.__create_sa_aws()

    def __create_sa_aws(self):
        sa_graph = self.sa_components.proj_graph
        n_cells = self.sa_components.n_cells
        n_neighbors = self.sa_components.n_neighbors
        align_bits = self.sa_components.align_bits
        n_threads = self.sa_components.n_threads

        c_bits = ceil(log2(n_cells))
        t_bits = ceil(log2(n_threads))
        t_bits = 1 if t_bits == 0 else t_bits
        node_bits = c_bits
        lines = columns = int(sqrt(n_cells))
        w_bits = t_bits + c_bits + node_bits + 1
        dist_bits = c_bits + ceil(log2(n_neighbors * 2))

        name = 'sa_aws'

        m = Module(name)

        # interface I/O interface - Begin ------------------------------------------------------------------------------
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')

        sa_aws_done_rd_data = m.Input('sa_aws_done_rd_data')
        sa_aws_done_wr_data = m.Input('sa_aws_done_wr_data')

        sa_aws_request_read = m.Output('sa_aws_request_read')
        sa_aws_read_data_valid = m.Input('sa_aws_read_data_valid')
        sa_aws_read_data = m.Input('sa_aws_read_data', self.bus_width)

        sa_aws_available_write = m.Input('sa_aws_available_write')
        sa_aws_request_write = m.OutputReg('sa_aws_request_write')
        sa_aws_write_data = m.OutputReg('sa_aws_write_data', self.bus_width)

        sa_aws_done = m.Output('sa_aws_done')
        # interface I/O interface - End --------------------------------------------------------------------------------

        sa_aws_done.assign(Uand(Cat(sa_aws_done_wr_data, sa_aws_done_rd_data)))

        start_pipe = m.Reg('start_pipe')

        pop_data = m.Reg('pop_data')
        available_pop = m.Wire('available_pop')
        data_out = m.Wire('data_out', self.pipe_width)
        # config_valid = m.Reg('config_valid')
        config_data = m.Reg('config_data', self.pipe_width)

        fsm_sd = m.Reg('fms_sd', 4)
        fsm_sd_c2n_idle = m.Localparam('fsm_sd_c2n_idle', 0, 4)
        fsm_sd_c2n_send_data = m.Localparam('fsm_sd_c2n_send_data', 1, 4)
        fsm_sd_c2n_verify = m.Localparam('fsm_sd_c2n_verify', 2, 4)
        fsm_sd_n2c_idle = m.Localparam('fsm_sd_n2c_idle', 3, 4)
        fsm_sd_n2c_send_data = m.Localparam('fsm_sd_n2c_send_data', 4, 4)
        fsm_sd_n2c_verify = m.Localparam('fsm_sd_n2c_verify', 5, 4)
        fsm_sd_n_idle = m.Localparam('fsm_sd_n_idle', 6, 4)
        fsm_sd_n_send_data = m.Localparam('fsm_sd_n_send_data', 7, 4)
        fsm_sd_n_verify = m.Localparam('fsm_sd_n_verify', 8, 4)
        fsm_sd_n_exec_idle = m.Localparam('fsm_sd_n_exec_idle', 9, 4)
        fsm_sd_n_exec_send_data = m.Localparam('fsm_sd_n_exec_send_data', 10, 4)
        fsm_sd_done = m.Localparam('fsm_sd_done', 11, 4)

        sa_done = m.Wire('sa_done')
        sa_rd = m.Reg('sa_rd')
        sa_rd_addr = m.Reg('sa_rd_addr', t_bits + c_bits + 1)
        sa_out_v = m.Wire('sa_out_v')
        sa_out_data = m.Wire('sa_out_data', node_bits + 1)

        # input config interfaces
        st1_wr = m.Reg('st1_wr')
        st1_wr_addr = m.Reg('st1_wr_addr', t_bits + c_bits)
        st1_wr_data = m.Reg('st1_wr_data', node_bits + 1)
        st2_mem_sel = m.Reg('st2_mem_sel', n_neighbors)
        st2_wr = m.Reg('st2_wr', n_neighbors)
        st2_wr_addr = m.Reg('st2_wr_addr', node_bits)
        st2_wr_data = m.Reg('st2_wr_data', node_bits + 1)
        st3_wr = m.Reg('st3_wr')
        st3_wr_addr = m.Reg('st3_wr_addr', t_bits + node_bits)
        st3_wr_data = m.Reg('st3_wr_data', c_bits)

        m.Always(Posedge(clk))(
            If(rst)(
                st1_wr(0),
                st1_wr_addr(0),
                st1_wr_data(0),
                st2_mem_sel(1),
                st2_wr(0),
                st2_wr_addr(0),
                st2_wr_data(0),
                st3_wr(0),
                st3_wr_addr(0),
                st3_wr_data(0),
                pop_data(0),
                fsm_sd(fsm_sd_c2n_idle),
            ).Elif(start)(
                st1_wr(0),
                st2_wr(0),
                st3_wr(0),
                start_pipe(0),
                pop_data(0),
                Case(fsm_sd)(
                    When(fsm_sd_c2n_idle)(
                        If(available_pop)(
                            pop_data(1),
                            fsm_sd(fsm_sd_c2n_send_data)
                        )
                    ),
                    When(fsm_sd_c2n_send_data)(
                        st1_wr(1),
                        st1_wr_data(data_out[:st1_wr_data.width]),
                        fsm_sd(fsm_sd_c2n_verify)
                    ),
                    When(fsm_sd_c2n_verify)(
                        If(Uand(st1_wr_addr))(
                            fsm_sd(fsm_sd_n2c_idle)
                        ).Else(
                            st1_wr_addr.inc(),
                            fsm_sd(fsm_sd_c2n_idle)
                        ),
                    ),
                    When(fsm_sd_n2c_idle)(
                        If(available_pop)(
                            pop_data(1),
                            fsm_sd(fsm_sd_n2c_send_data)
                        )
                    ),
                    When(fsm_sd_n2c_send_data)(
                        st3_wr(1),
                        st3_wr_data(data_out[:st3_wr_data.width]),
                        fsm_sd(fsm_sd_n2c_verify)
                    ),
                    When(fsm_sd_n2c_verify)(
                        If(Uand(st3_wr_addr))(
                            fsm_sd(fsm_sd_n_idle)
                        ).Else(
                            st3_wr_addr.inc(),
                            fsm_sd(fsm_sd_n2c_idle)
                        ),
                    ),
                    When(fsm_sd_n_idle)(
                        If(available_pop)(
                            pop_data(1),
                            fsm_sd(fsm_sd_n_send_data)
                        )
                    ),
                    When(fsm_sd_n_send_data)(
                        st2_wr(st2_mem_sel),
                        st2_wr_data(data_out[:st2_wr_data.width]),
                        fsm_sd(fsm_sd_n_verify)
                    ),
                    When(fsm_sd_n_verify)(
                        If(Uand(st2_wr_addr))(
                            If(st2_mem_sel[n_neighbors-1])(
                                fsm_sd(fsm_sd_n_exec_idle)
                            ).Else(
                                st2_mem_sel(st2_mem_sel << 1),
                                st2_wr_addr.inc(),
                                fsm_sd(fsm_sd_n_idle)
                            ),
                        ).Else(
                            st2_wr_addr.inc(),
                            fsm_sd(fsm_sd_n_idle)
                        ),
                    ),
                    When(fsm_sd_n_exec_idle)(
                        If(available_pop)(
                            pop_data(1),
                            fsm_sd(fsm_sd_n_exec_send_data)
                        )
                    ),
                    When(fsm_sd_n_exec_send_data)(
                        config_data(data_out),
                        fsm_sd(fsm_sd_done)
                    ),
                    When(fsm_sd_done)(
                        start_pipe(1)
                    )
                )
            )
        )

        # Data Consumer - Begin ----------------------------------------------------------------------------------------
        m.EmbeddedCode('\n//Data Consumer - Begin')
        fsm_consume = m.Reg('fsm_consume', 2)
        fsm_consume_wait = m.Localparam('fsm_consume_wait', 0)
        fsm_consume_consume = m.Localparam('fsm_consume_consume', 1)
        fsm_consume_verify = m.Localparam('fsm_consume_verify', 2)
        fsm_consume_done = m.Localparam('fsm_consume_done', 3)

        m.Always(Posedge(clk))(
            If(rst)(
                sa_rd(0),
                sa_rd_addr(0),
                sa_aws_request_write(0),
                fsm_consume(fsm_consume_wait)
            ).Else(
                sa_rd(0),
                sa_aws_request_write(0),
                Case(fsm_consume)(
                    When(fsm_consume_wait)(
                        If(sa_aws_available_write)(
                            If(sa_done)(
                                sa_rd(1),
                                fsm_consume(fsm_consume_consume),
                            ),
                        ),

                    ),
                    When(fsm_consume_consume)(
                        If(sa_out_v)(
                            sa_aws_request_write(1),
                            sa_aws_write_data(Cat(Int(0, self.bus_width - sa_out_data.width, 10), sa_out_data)),
                            sa_rd_addr.inc(),
                            fsm_consume(fsm_consume_verify)
                        ),
                    ),
                    When(fsm_consume_verify)(
                        If(sa_rd_addr == pow(2, t_bits + c_bits))(
                            fsm_consume(fsm_consume_done)
                        ).Else(
                            fsm_consume(fsm_consume_wait)
                        )
                    ),
                    When(fsm_consume_done)(

                    ),
                )
            )
        )
        m.EmbeddedCode('//Data Consumer - Begin')
        # Data Consumer - End ------------------------------------------------------------------------------------------

        fetch_data = self.sa_components.create_fecth_data(self.bus_width, self.pipe_width)
        par = []
        con = [
            ('clk', clk),
            ('rst', rst),
            ('start', start),
            ('request_read', sa_aws_request_read),
            ('data_valid', sa_aws_read_data_valid),
            ('read_data', sa_aws_read_data),
            ('pop_data', pop_data),
            ('available_pop', available_pop),
            ('data_out', data_out)
        ]
        m.EmbeddedCode("(* keep_hierarchy = \"yes\" *)")
        m.Instance(fetch_data, fetch_data.name, par, con)

        par = []
        con = [
            ('st1_wr', st1_wr),
            ('st1_wr_addr', st1_wr_addr),
            ('st1_wr_data', st1_wr_data),
            ('st2_wr', st2_wr),
            ('st2_wr_addr', st2_wr_addr),
            ('st2_wr_data', st2_wr_data),
            ('st3_wr', st3_wr),
            ('st3_wr_addr', st3_wr_addr),
            ('st3_wr_data', st3_wr_data),
            ('clk', clk),
            ('rst', rst),
            ('start', start_pipe),
            ('n_exec', config_data),
            ('done', sa_done),
            ('rd', sa_rd),
            ('rd_addr', sa_rd_addr[:t_bits + c_bits]),
            ('out_v', sa_out_v),
            ('out_data', sa_out_data),
        ]
        aux = self.sa_components.create_sa_pipeline()
        m.Instance(aux, aux.name, par, con)

        _u.initialize_regs(m)
        return m
