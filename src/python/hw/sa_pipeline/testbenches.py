from veriloggen import *
from math import ceil, log2, sqrt
import src.python.hw.sa_fsm.sa_components as _sa
import old.sa_pipeline.util as _u
import src.python.hw.sa_aws as _aws
import src.python.hw.sa_fsm.sa_components as _comp


def create_threads_controller_test_bench(sa_comp: _sa.SAComponents) -> str:
    sa_graph = sa_comp.proj_graph
    n_cells = sa_comp.proj_graph.n_cells
    n_neighbors = sa_comp.n_neighbors
    align_bits = sa_comp.align_bits
    n_threads = sa_comp.n_threads

    name = "testbench_threads_controller_%dthreads_%dcells" % (
        n_threads, n_cells)
    if name in sa_comp.cache.keys():
        return sa_comp.cache[name]

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits
    lines = columns = int(sqrt(n_cells))
    w_bits = t_bits + c_bits + node_bits + 1
    dist_bits = c_bits + ceil(log2(n_neighbors * 2))

    # FIXME
    # 1º - Create the memory archives: c-n n-c and neighbors
    # create_rom_files(sa_comp)

    # 2º - Create testbench and execute it

    # TEST BENCH MODULE
    m = Module(name)
    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    # threads controller
    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start)
    ]
    aux = sa_comp.create_threads_controller()
    m.Instance(aux, aux.name, par, con)

    _u.initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        rst(0),
        start(1),
        Delay(4000),
        Finish(),
    )
    m.EmbeddedCode("always #5clk=~clk;")
    # m.Always(Posedge(clk))(
    #    If(rnd_en)(
    #        Display("%d", rnd_rnd[0:4])
    #    )
    # )

    m.to_verilog(os.getcwd() + "/verilog/threads_controller.v")
    sim = simulation.Simulator(m, sim="iverilog")
    # rslt = sim.run()
    # print(rslt)


def create_sa_verilog_test_bench(sa_comp: _sa.SAComponents) -> str:
    sa_graph = sa_comp.proj_graph
    n_cells = sa_comp.proj_graph.n_cells
    n_neighbors = sa_comp.n_neighbors
    align_bits = sa_comp.align_bits
    n_threads = sa_comp.n_threads

    name = "testbench_sa_pipeline_%dthreads_%dcells" % (
        n_threads, n_cells)
    if name in sa_comp.cache.keys():
        return sa_comp.cache[name]

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits
    lines = columns = int(sqrt(n_cells))
    w_bits = t_bits + c_bits + node_bits + 1
    dist_bits = c_bits + ceil(log2(n_neighbors * 2))

    # FIXME
    # 1º - Create the memory archives: c-n n-c and neighbors
    _u.create_rom_files(sa_comp)

    # 2º - Create testbench and execute it

    # TEST BENCH MODULE
    m = Module(name)
    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    done = m.Wire('done')

    # threads controller
    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start),
        ('n_exec', Int(1, 16, 10)),
        ('done', done)
    ]
    aux = sa_comp.create_sa_pipeline()
    m.Instance(aux, aux.name, par, con)

    _u.initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        rst(0),
        start(1),
        # Delay(4000),
        # Finish(),
    )

    m.Always(Posedge(clk))(
        If(done)(
            Finish()
        )
    )

    m.EmbeddedCode("always #5clk=~clk;")
    # m.Always(Posedge(clk))(
    #    If(rnd_en)(
    #        Display("%d", rnd_rnd[0:4])
    #    )
    # )

    m.to_verilog(os.getcwd() + '/verilog/sa_verilog_test.v')
    sim = simulation.Simulator(m, sim="iverilog")
    rslt = sim.run_parallel()
    print(rslt)
    _u.create_dot_from_rom_files(
        os.getcwd() + '/rom/c_n.rom', 'ini_th', os.getcwd() + '/rom/', n_threads, n_cells)
    _u.create_dot_from_rom_files(
        os.getcwd() + '/rom/c_n_out.rom', 'end_th', os.getcwd() + '/rom/', n_threads, n_cells)
    print(sa_graph.neighbors)


def create_sa_aws_test_bench(comp: _comp.SAComponents) -> str:
    _u.create_rom_files(comp, os.getcwd() + "/verilog")

    bus_width = 16
    sa_graph = comp.proj_graph
    n_cells = comp.n_cells
    n_neighbors = comp.n_neighbors
    align_bits = comp.align_bits
    n_threads = comp.n_threads

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits
    lines = columns = int(sqrt(n_cells))
    w_bits = t_bits + c_bits + node_bits + 1
    dist_bits = c_bits + ceil(log2(n_neighbors * 2))
    lc_bits = ceil(log2(lines)) * 2

    m = Module('test_bench_sa_acc')

    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    sa_aws_done_rd_data = m.Reg('sa_aws_done_rd_data')
    sa_aws_done_wr_data = m.Reg('sa_aws_done_wr_data')
    sa_aws_request_read = m.Wire('sa_aws_request_read')
    sa_aws_read_data_valid = m.Reg('sa_aws_read_data_valid')
    sa_aws_read_data = m.Reg('sa_aws_read_data', bus_width)
    sa_aws_available_write = m.Reg('sa_aws_available_write')
    sa_aws_request_write = m.Wire('sa_aws_request_write')
    sa_aws_write_data = m.Wire('sa_aws_write_data', bus_width)
    sa_aws_done = m.Wire('sa_aws_done')

    fsm_produce_data = m.Reg('fsm_produce_data', 2)
    fsm_produce = m.Localparam('fsm_produce', 0)
    fsm_done = m.Localparam('fsm_done', 1)

    m.Always(Posedge(clk))(
        If(rst)(
            start(0),
            sa_aws_read_data_valid(0),
            sa_aws_done_rd_data(0),
            fsm_produce_data(fsm_produce),
        ).Else(
            start(1),
            Case(fsm_produce_data)(
                When(fsm_produce)(
                    sa_aws_read_data_valid(1),
                    sa_aws_read_data(Int(1, 16, 10)),
                    If(AndList(sa_aws_request_read, sa_aws_read_data_valid))(
                        sa_aws_read_data_valid(0),
                        # fsm_produce_data(fsm_done)
                    ),
                ),
                When(fsm_done)(
                    sa_aws_done_rd_data(1)
                ),
            )
        )
    )

    rd_counter = m.Reg('rd_counter', t_bits + c_bits + 1)

    fsm_consume_data = m.Reg('fsm_consume_data', 2)
    fsm_consume_data_rd = m.Localparam('fsm_consume_data_rd', 0)
    fsm_consume_data_done = m.Localparam('fsm_consume_data_done', 1)

    m.Always(Posedge(clk))(
        If(rst)(
            rd_counter(0),
            sa_aws_available_write(0),
            sa_aws_done_wr_data(0),
            fsm_consume_data(fsm_consume_data_rd),
        ).Else(
            Case(fsm_consume_data)(
                When(fsm_consume_data_rd)(
                    sa_aws_available_write(1),
                    If(sa_aws_request_write)(
                        rd_counter.inc(),
                        Display('%b', sa_aws_write_data),
                        If(rd_counter == pow(2, t_bits + c_bits) - 1)(
                            sa_aws_available_write(0),
                            fsm_consume_data(fsm_consume_data_done),
                        )
                    )
                ),
                When(fsm_consume_data_done)(
                    sa_aws_done_wr_data(1),
                ),
            ),
        )
    )

    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start),
        ('sa_aws_done_rd_data', sa_aws_done_rd_data),
        ('sa_aws_done_wr_data', sa_aws_done_wr_data),
        ('sa_aws_request_read', sa_aws_request_read),
        ('sa_aws_read_data_valid', sa_aws_read_data_valid),
        ('sa_aws_read_data', sa_aws_read_data),
        ('sa_aws_available_write', sa_aws_available_write),
        ('sa_aws_request_write', sa_aws_request_write),
        ('sa_aws_write_data', sa_aws_write_data),
        ('sa_aws_done', sa_aws_done)
    ]
    aws = _aws.SaAws()
    aux = aws.get(comp.proj_graph, bus_width)
    m.Instance(aux, aux.name, par, con)

    _u.initialize_regs(m, {'clk': 0, 'rst': 1, 'start': 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        rst(0),
        Delay(40000), Finish()
    )
    m.EmbeddedCode('always #5clk=~clk;')
    m.Always(Posedge(clk))(
        If(sa_aws_done)(
            Display('ACC DONE!'),
            Finish()
        )
    )
    m.EmbeddedCode('\n//Simulation sector - End')
    m.to_verilog(os.getcwd() + "/verilog/sa_aws_testbench.v")
    #sim = simulation.Simulator(m, sim='iverilog')
    # rslt = sim.run()
    # print(rslt)


def create_sa_pipeline_test_bench(comp: _comp.SAComponents) -> str:
    _u.create_rom_files(comp, os.getcwd() + "/verilog")

    bus_width = 16
    sa_graph = comp.proj_graph
    n_cells = comp.n_cells
    n_neighbors = comp.n_neighbors
    align_bits = comp.align_bits
    n_threads = comp.n_threads

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits
    lines = columns = int(sqrt(n_cells))
    w_bits = t_bits + c_bits + node_bits + 1
    dist_bits = c_bits + ceil(log2(n_neighbors * 2))
    lc_bits = ceil(log2(lines)) * 2

    m = Module('test_bench_sa_pipeline')

    clk = m.Reg('clk')
    rst = m.Reg('rst')
    start = m.Reg('start')

    done = m.Wire('done')

    par = []
    con = [
        ('clk', clk),
        ('rst', rst),
        ('start', start),
        ('n_exec', Int(1, 16, 10)),
        ('rd',0),
        ('done',done),
    ]
    #aws = _aws.SaAws()
    aux = comp.create_sa_pipeline()#aws.get(comp.sa_graph, bus_width)
    m.Instance(aux, aux.name, par, con)

    _u.initialize_regs(m, {'clk': 0, 'rst': 1, 'start': 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        EmbeddedCode('@(posedge clk);'),
        rst(0),
        start(1),
        Delay(40000), Finish()
    )
    m.EmbeddedCode('always #5clk=~clk;')
    m.Always(Posedge(clk))(
        If(done)(
            Display('ACC DONE!'),
            Finish()
        )
    )
    m.EmbeddedCode('\n//Simulation sector - End')
    m.to_verilog(os.getcwd() + "/verilog/sa_aws_testbench.v")
    #sim = simulation.Simulator(m, sim='iverilog')
    # rslt = sim.run()
    # print(rslt)
