from veriloggen import *
import old.sa_pipeline.util as _u
import src.python.hw.sa_aws as _sa


class SaAccelerator:
    def __init__(self, sa_graph: _u.SaGraph, copies):
        # constants
        self.acc_num_in = copies
        self.acc_num_out = copies

        self.sa_graph = sa_graph
        self.copies = copies
        self.bus_width = 32
        self.acc_data_in_width = self.bus_width
        self.acc_data_out_width = self.bus_width
        self.axi_bus_data_width = self.acc_data_in_width

    def get_num_in(self):
        return self.acc_num_in

    def get_num_out(self):
        return self.acc_num_out

    def get(self):
        return self.__create_sa_accelerator()

    def __create_sa_accelerator(self):
        sa_aws = _sa.SaAws()

        m = Module('sa_acc')
        clk = m.Input('clk')
        rst = m.Input('rst')
        start = m.Input('start')
        acc_user_done_rd_data = m.Input('acc_user_done_rd_data', self.acc_num_in)
        acc_user_done_wr_data = m.Input('acc_user_done_wr_data', self.acc_num_out)

        acc_user_request_read = m.Output('acc_user_request_read', self.acc_num_in)
        acc_user_read_data_valid = m.Input('acc_user_read_data_valid', self.acc_num_in)
        acc_user_read_data = m.Input('acc_user_read_data', self.axi_bus_data_width * self.acc_num_in)

        acc_user_available_write = m.Input('acc_user_available_write', self.acc_num_out)
        acc_user_request_write = m.Output('acc_user_request_write', self.acc_num_out)
        acc_user_write_data = m.Output('acc_user_write_data', self.axi_bus_data_width * self.acc_num_out)

        acc_user_done = m.Output('acc_user_done')

        start_reg = m.Reg('start_reg')
        sa_aws_done = m.Wire('sa_aws_done', self.get_num_in())

        acc_user_done.assign(Uand(sa_aws_done))

        m.Always(Posedge(clk))(
            If(rst)(
                start_reg(0)
            ).Else(
                start_reg(Or(start_reg, start))
            )
        )
        if self.copies < 1:
            raise ValueError("The copies value can't be lower than 1")
        sa_aws = sa_aws.get(self.sa_graph, self.bus_width)
        for i in range(self.copies):
            par = []
            con = [
                ('clk', clk),
                ('rst', rst),
                ('start', start_reg),
                ('sa_aws_done_rd_data', acc_user_done_rd_data[i]),
                ('sa_aws_done_wr_data', acc_user_done_wr_data[i]),
                ('sa_aws_request_read', acc_user_request_read[i]),
                ('sa_aws_read_data_valid', acc_user_read_data_valid[i]),
                ('sa_aws_read_data', acc_user_read_data[i * self.acc_data_in_width:(i + 1) * self.acc_data_in_width]),
                ('sa_aws_available_write', acc_user_available_write[i]),
                ('sa_aws_request_write', acc_user_request_write[i]),
                ('sa_aws_write_data',
                 acc_user_write_data[i * self.acc_data_out_width:(i + 1) * self.acc_data_out_width]),
                ('sa_aws_done', sa_aws_done[i])]
            m.EmbeddedCode("(* keep_hierarchy = \"yes\" *)")
            m.Instance(sa_aws, sa_aws.name + "_" + str(i), par, con)

        _u.initialize_regs(m)

        return m
