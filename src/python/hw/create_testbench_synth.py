import random

from veriloggen import *

from src.python.hw.yoto_pipeline.yoto_pipeline_hw import YotoPipelineHw
from src.python.util.hw_util import HwUtil
from src.python.util.per_enum import ArchType
from src.python.util.per_graph import PeRGraph
from src.python.util.util import Util


def create_testbench_synth(module: Module()):
    m = Module('testbench_synth')
    clk = m.Input('clk')
    rst = m.Input('rst')
    out = m.Output('out')
    regs_reset = []
    regs_inc = []
    or_list = ''
    start = m.Reg('start')

    params = module.get_params()
    for p in params:
        m.Localparam(params[p].name, params[p].value)

    ports = module.get_ports()
    con = []
    max_width_out = 1

    for port in ports:
        if module.is_input(port) and port in ['clk', 'rst']:
            con.append((port, m.get_ports()[port]))
        elif module.is_input(port) and port in ['start']:
            con.append((port, start))
        elif module.is_input(port) and port not in ['clk', 'rst', 'start']:
            p = ports[port]
            if p.width:
                reg = m.Reg(f'{port}', p.width)
            else:
                reg = m.Reg(f'{port}')
            regs_reset.append(reg(0))
            regs_inc.append(reg.inc())
            con.append((port, reg))
        elif module.is_output(port):
            p = ports[port]
            if p.width:
                if str(p.width) in params:
                    p.width = p.width.value

                wire = m.Wire(f'{module.name}_{port}', p.width)
                max_width_out = max(max_width_out, p.width)
            else:
                wire = m.Wire(f'{module.name}_{port}')
            or_list += wire.name + '|'
            con.append((port, wire))

    data = m.Wire('data', max_width_out)
    m.Instance(module, f'{module.name}', params, con)

    m.Always(Posedge(clk))(
        If(rst)(
            regs_reset
        ).Else(
            regs_inc
        )
    )

    m.Always(Posedge(clk))(
        If(rst)(
            start(0)
        ).Else(
            start(1)
        )
    )

    data.assign(EmbeddedCode(or_list[:-1]))
    out.assign(Uxor(data))

    HwUtil.initialize_regs(m)

    return m


random.seed(0)
threads_per_copy: int = 6
total_threads: int = 6
arch_type: ArchType = ArchType.ONE_HOP
make_shuffle: bool = True
distance_table_bits: int = 4
simul = True

root_path: str = Util.get_project_root()
dot_path_base = root_path + '/dot_db/'
dot_connected_path = dot_path_base + 'connected/'

report_path_base = os.getcwd() + '/reports/sw/yoto/yoto_pipeline/t_%d/%s/' % (total_threads, arch_type)
verilog_path_base = os.getcwd() + '/verilog/yoto/yoto_pipeline/t_%d/%s/' % (total_threads, arch_type)

Util.create_folder_if_not_exist(report_path_base)
Util.create_folder_if_not_exist(verilog_path_base)

yoto_pipeline_hw = None

dots_list = [[dot_connected_path + 'mac.dot', 'mac.dot']]
for dot_path, dot_name in dots_list:
    per_graph = PeRGraph(dot_path, dot_name)
    print(per_graph.dot_name)
    yoto_pipeline_hw = YotoPipelineHw(per_graph, arch_type, distance_table_bits, make_shuffle, threads_per_copy, )
acc = yoto_pipeline_hw.create_acc(15)
m = create_testbench_synth(acc)
m.to_verilog('synth.v')

'''def create_testbench_sim(cgraAcc, num_data: int, conf_lines, files):
    num_in = len(cgraAcc.cgra.input_ids)
    num_out = len(cgraAcc.cgra.output_ids)
    data_producer = Components().create_data_producer()
    data_consumer = Components().create_data_consumer()

    m = Module('testbench_sim')

    INTERFACE_DATA_WIDTH = m.Localparam('INTERFACE_DATA_WIDTH', 512)

    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    rd_done = m.Wire('rd_done', num_in)
    wr_done = m.Wire('wr_done', num_out)

    rd_request = m.Wire('rd_request', num_in)
    rd_valid = m.Wire('rd_valid', num_in)
    rd_data = m.Wire('rd_data', Mul(INTERFACE_DATA_WIDTH, num_in))

    wr_available = m.Wire('wr_available', num_out)
    wr_request = m.Wire('wr_request', num_out)
    wr_data = m.Wire('wr_data', Mul(INTERFACE_DATA_WIDTH, num_out))

    acc_done = m.Wire('acc_done')

    for i in range(num_in):
        params = [('file', files[i]),
                  ('data_width', INTERFACE_DATA_WIDTH),
                  ('num_data', num_data + conf_lines if i == 0 else num_data),
                  ('addr_width', 1 + ceil(log2(num_data + conf_lines if i == 0
                                               else num_data)))]
        con = [('clk', clk),
               ('rst', rst),
               ('rd_request', rd_request[i]),
               ('read_data_valid', rd_valid[i]),
               ('rd_done', rd_done[i]),
               ('read_data', rd_data[Mul(i, INTERFACE_DATA_WIDTH):
                                     Mul(i + 1, INTERFACE_DATA_WIDTH)])]

        m.Instance(data_producer, 'data_producer_%d' % i, params, con)

    for i in range(num_out):
        params = [('data_width', INTERFACE_DATA_WIDTH),
                  ('id', i),
                  ('num_data', num_data),
                  ('counter_num_data_width', 1 + ceil(log2(num_data)))]
        con = [('clk', clk),
               ('rst', rst),
               ('wr_done', wr_done[i]),
               ('wr_available', wr_available[i]),
               ('wr_request', wr_request[i]),
               ('wr_data', wr_data[Mul(i, INTERFACE_DATA_WIDTH):
                                   Mul(i + 1, INTERFACE_DATA_WIDTH)])]
        m.Instance(data_consumer, 'data_consumer_%d' % i, params, con)

    params = [('INTERFACE_DATA_WIDTH', INTERFACE_DATA_WIDTH)]
    con = [('clk', clk), ('rst', rst), ('start', start),
           ('acc_user_done_rd_data', rd_done),
           ('acc_user_done_wr_data', wr_done),
           ('acc_user_request_read', rd_request),
           ('acc_user_read_data_valid', rd_valid),
           ('acc_user_read_data', rd_data),
           ('acc_user_available_write', wr_available),
           ('acc_user_request_write', wr_request),
           ('acc_user_write_data', wr_data),
           ('acc_user_done', acc_done)
           ]
    module = cgraAcc.get()

    m.Instance(module, module.name, params, con)

    initialize_regs(m, {'clk': 0, 'rst': 1, 'wr_available': 2 ** num_out - 1})

    simulation.setup_waveform(m)

    m.Initial(
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        rst(0),
        start(1),
        Delay(10000), Finish()
    )
    m.EmbeddedCode('always #5clk=~clk;')

    m.Always(Posedge(clk))(
        If(acc_done)(
            # Display('ACC DONE!'),
            Finish()
        )
    )

    return m'''
