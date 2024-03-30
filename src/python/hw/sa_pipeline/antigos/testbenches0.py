from veriloggen import *

from src.python.hw import SAComponents
from old.sa_pipeline import create_rom_files, initialize_regs
from math import ceil, log2, sqrt


def create_sa_test_bench(sa_comp: SAComponents) -> str:
    sa_graph = sa_comp.per_graph
    n_cells = sa_comp.per_graph.n_cells
    n_neighbors = sa_comp.n_neighbors
    align_bits = sa_comp.align_bits
    n_threads = sa_comp.n_threads

    name = "testbench_sa_%dthreads_%dcells_%dneighbors" % (
        n_threads, n_cells, n_neighbors)
    if name in sa_comp.cache.keys():
        return sa_comp.cache[name]

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits + 1
    lines = columns = int(sqrt(n_cells))
    d_width = ceil(log2(lines+columns))
    d_width += ceil(log2(n_neighbors))

    # 1º - Create the memory archives: c-n n-c and neighbors
    create_rom_files(sa_comp)

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
    aux = sa_comp.create_sa()
    m.Instance(aux, aux.name, par, con)

    initialize_regs(m, {"clk": 0, "rst": 1, "start": 0})
    simulation.setup_waveform(m)
    m.Initial(
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        EmbeddedCode("@(posedge clk);"),
        rst(0),
        start(1),
        Delay(450),
        Finish(),
    )
    m.EmbeddedCode("always #5clk=~clk;")
    # m.Always(Posedge(clk))(
    #    If(rnd_en)(
    #        Display("%d", rnd_rnd[0:4])
    #    )
    # )

    m.to_verilog(os.getcwd() + "/verilog/sa_test_bench_hw.v")
    sim = simulation.Simulator(m, sim="iverilog")
    rslt = sim.run_parallel()
    print(rslt)
