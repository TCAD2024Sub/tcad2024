from veriloggen import *
from src.python.util.hw_util import sa_fsm_create_rom_files
from src.python.util.hw_util import HwUtil as Vu
from src.python.util.per_graph import PeRGraph
from src.python.hw.sa_fsm.sa_components import SAComponents


def create_sa_single_test_bench(base_path: str, sa_graph: PeRGraph, test_number: int = 0):
    name = 'test_bench_sa_single_%d' % test_number
    dumpfile = base_path + "/verilog/%s.vcd" % name
    verilog_file = base_path + "/verilog/%s.v" % name
    output_file = base_path + "/verilog/a.out"
    sa_graph = sa_graph

    sa_comp = SAComponents(sa_graph, base_path, name)
    sa_fsm_create_rom_files(sa_graph, sa_comp, base_path + "/verilog/" + name)

    cell_bits = sa_comp.cell_bits
    node_bits = sa_comp.node_bits
    n_neighbors = sa_comp.n_neighbors

    m = Module(name)

    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    done = m.Wire('done')

    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start),
        ('done', done),
        ('n_exec', Int(1000, 10, 10)),

        ('conf_c2n_rd', Int(0, 1, 10)),
        ('conf_c2n_rd_addr', Int(0, cell_bits, 10)),

        ('conf_wr', Int(0, 1, 10)),

        ('conf_c2n_wr', Int(0, 1, 10)),
        ('conf_c2n_wr_addr', Int(0, cell_bits, 10)),
        ('conf_c2n_wr_data', Int(0, node_bits + 1, 10)),

        ('conf_n_wr', Int(0, n_neighbors, 10)),
        ('conf_n_wr_addr', Int(0, node_bits, 10)),
        ('conf_n_wr_data', Int(0, node_bits + 1, 10)),

        ('conf_n2c_wr', Int(0, n_neighbors, 10)),
        ('conf_n2c_wr_addr', Int(0, cell_bits, 10)),
        ('conf_n2c_wr_data', Int(0, node_bits, 10)),
    ]
    sa_single = sa_comp.create_sa_fsm_single_thread()
    m.Instance(sa_single, sa_single.name, par, con)

    Vu.initialize_regs(m, {'clk': 0, 'rst': 1, 'start': 0})

    simulation.setup_waveform(m, dumpfile=dumpfile)
    m.Initial(
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        rst(0),
        start(1),
        Delay(1000), Finish()
    )
    m.EmbeddedCode('always #5clk=~clk;')
    m.Always(Posedge(clk))(
        If(done)(
            Display('ACC DONE!'),
            Finish()
        )
    )
    m.EmbeddedCode('\n//Simulation sector - End')

    m.to_verilog(verilog_file)
    main_module_file = base_path + "/verilog/%s.v" % sa_single.name
    sa_single.to_verilog(main_module_file)
    # sim = simulation.Simulator(m, sim='iverilog')
    # rslt = sim.run(outputfile=output_file)
    # print(rslt)
