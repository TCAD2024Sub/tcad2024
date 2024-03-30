from veriloggen import *
import networkx as nx
from src.python.util.util import Util

from src.python.util.per_graph import PeRGraph

#FIXME - Troughput % error
class DfSimulHw:
    def __init__(self, per_graph: PeRGraph, n_data: int = 5000):
        self.per_graph = per_graph
        self.n_data = n_data
        self.verilog_file = f'dfg.v'
        self.output_file = f'dfg.out'
        self.df_compat: nx.DiGraph = self.make_dfg_compatible()
        self.test_bench: Module = self.make_test_bench()

    def run_simulation(self):
        self.test_bench.to_verilog(self.verilog_file)
        sim = simulation.Simulator(self.test_bench, sim='iverilog')
        print('Starting simulation')
        rslt = sim.run(outputfile=self.output_file)
        print(rslt)
        print('Simulation done')

        th = self.get_thoughputs(rslt)
        return th

    def get_thoughputs(self, rslt: str):
        lines = rslt.split('\n')

        th: list = []

        for line in lines:
            if 'throughput' in line:
                line_spl = line.replace(' ', '').replace('%', '').split(':')
                th.append([line_spl[1], float(line_spl[2])])
        return th

    def make_dfg_compatible(self) -> nx.DiGraph:
        df: nx.DiGraph = self.per_graph.g.copy()
        nodes_ports: dict = {}
        insert_output_nodes: set = set()
        for node in df.nodes():
            df.nodes[node]['op'] = 'add'
            if df.in_degree(node) == 0:
                df.nodes[node]['op'] = 'in'
            elif df.out_degree(node) == 0:
                if df.in_degree(node) > 1:
                    insert_output_nodes.add(node)
                else:
                    df.nodes[node]['op'] = 'out'
            elif df.in_degree(node) == 1:
                df.nodes[node]['op'] = 'reg'

        new_df: nx.DiGraph = df.copy()

        for edge in df.edges():
            src = edge[0]
            dst = edge[1]

            # verify if the weight parameter is in each edge
            if 'weight' not in new_df.edges[edge].keys():
                new_df.edges[edge]['weight'] = 0
            # specify wich port to connect to each node
            if dst not in nodes_ports.keys():
                nodes_ports[dst] = 0
            dst_port = nodes_ports[dst]
            nodes_ports[dst] += 1
            if int(new_df.edges[edge]['weight']) > 0:
                for r in range(int(new_df.edges[edge]['weight'])):
                    reg_idx = f'{src}_{dst}_{r}'
                    new_df.add_node(reg_idx)
                    nx.set_node_attributes(new_df, {reg_idx: {'label': f'reg_{reg_idx}', 'op': 'add'}})
                    new_df.add_edge(src, reg_idx)
                    if reg_idx not in nodes_ports.keys():
                        nodes_ports[reg_idx] = 0
                    reg_port = nodes_ports[reg_idx]
                    nodes_ports[reg_idx] += 1
                    nx.set_edge_attributes(new_df, {(src, reg_idx): {'port': reg_port, 'weight': 0}})
                    src = reg_idx
                new_df.add_edge(src, dst)
                nx.set_edge_attributes(new_df, {(src, dst): {'port': dst_port, 'weight': 0}})
                new_df.remove_edge(edge[0], edge[1])
            else:
                if 'port' not in new_df.edges[edge].keys():
                    new_df.edges[edge]['port'] = dst_port
                else:
                    new_df.edges[edge]['port'] = dst_port
        for node in insert_output_nodes:
            out_idx = f'{node}_out'
            new_df.add_node(out_idx)
            nx.set_node_attributes(new_df, {out_idx: {'label': out_idx, 'op': 'out'}})
            new_df.add_edge(node, out_idx)
            nx.set_edge_attributes(new_df, {(node, out_idx): {'port': 0, 'weight': 0}})
        return new_df

    def make_test_bench(self) -> Module:
        df = self.df_compat
        dataflow = self.make_dataflow()
        m = Module(self.per_graph.dot_name.replace(".", "_"))
        data_width = m.Localparam('data_width', 32)
        fail_rate_producer = m.Localparam('fail_rate_producer', 0)
        fail_rate_consumer = m.Localparam('fail_rate_consumer', 0)
        is_const = m.Localparam('is_const', 'false')
        initial_value = m.Localparam('initial_value', 0)

        max_data_size = m.Localparam('max_data_size', self.n_data)

        clk = m.Reg('clk')
        rst = m.Reg('rst')

        df_ports = dataflow.get_ports()
        ports = m.get_vars()
        for p in df_ports:
            if p not in ports:
                m.Wire(p, df_ports[p].width)

        ports = m.get_vars()

        n_in = 0
        n_out = 0
        for no in df.nodes:
            op = str.lower(df.nodes[no]['op'])
            if op == 'in':
                n_in += 1
            elif op == 'out':
                n_out += 1

        count_producer = m.Wire('count_producer', 32, n_in)
        count_consumer = m.Wire('count_consumer', 32, n_out)
        count_clock = m.Real('count_clock', 32)

        m.EmbeddedCode('')
        consumers_done = m.Wire('consumers_done', n_out)
        done = m.Wire('done')
        for i in range(n_out):
            consumers_done[i].assign(count_consumer[i] >= max_data_size)

        done.assign(Uand(consumers_done))

        simulation.setup_clock(m, clk, hperiod=1)
        simulation.setup_reset(m, rst, period=1)
        simulation.setup_waveform(m, dumpfile='uut.vcd')

        i = m.Integer('i')

        m.Always(Posedge(clk))(
            If(rst)(
                count_clock(0)
            ),
            count_clock.inc(),
            If(done)(
                For(i(0), i < n_out, i.inc())(
                    Display(self.per_graph.dot_name.replace(".", "_") + " throughput: %d : %5.2f%%", i,
                            Mul(100.0, (count_consumer[i] / (count_clock / 4.0)))),
                ),
                Display("%d d_in, %d d_out, %d clk", count_producer[0], count_consumer[0], count_clock),
                Finish()
            )
        )
        p = self.make_producer()
        c = self.make_consumer()
        c_in = 0
        c_out = 0
        for no in df.nodes:
            op = str.lower(df.nodes[no]['op'])
            if op == 'in':
                param = [
                    ('producer_id', int(c_in)),
                    ('data_width', data_width),
                    ('fail_rate', fail_rate_producer),
                    ('initial_value', initial_value),
                    ('is_const', is_const)
                ]
                con = [
                    ('clk', clk),
                    ('rst', rst),
                    ('req', ports['din_req_%s' % no]),
                    ('ack', ports['din_ack_%s' % no]),
                    ('dout', ports['din_%s' % no]),
                    ('count', count_producer[c_in])
                ]
                m.Instance(p, p.name + '_%s' % no, param, con)
                c_in += 1
            elif op == 'out':
                df.nodes[no]['idx'] = str(c_out)
                param = [
                    ('consumer_id', int(c_out)),
                    ('data_width', data_width),
                    ('fail_rate', fail_rate_consumer)
                ]
                con = [
                    ('clk', clk),
                    ('rst', rst),
                    ('req', ports['dout_req_%s' % no]),
                    ('ack', ports['dout_ack_%s' % no]),
                    ('din', ports['dout_%s' % no]),
                    ('count', count_consumer[c_out])
                ]
                m.Instance(c, c.name + '_%s' % no, param, con)
                c_out += 1

        m.Instance(dataflow, dataflow.name,
                   dataflow.get_params(), dataflow.get_ports())

        return m

    def make_dataflow(self):
        df = self.df_compat
        m = Module(df.name)
        data_width = m.Parameter('data_width', 32)
        clk = m.Input('clk')
        rst = m.Input('rst')
        wires = self.create_wires(m)
        operator = self.make_async_operator()
        for no in df.nodes:
            immediate = 0  # self.get_immediate(df.nodes[no])
            input_size = df.in_degree(no)
            output_size = df.out_degree(no)
            op = str.lower(df.nodes[no]['op'])
            if op == 'in':
                input_size += 1
            elif op == 'out':
                output_size += 1

            req_l, ack_l, din, req_r, ack_r, dout = self.create_con_node(no, op)
            param = [('data_width', data_width),
                     ('op', op),
                     ('immediate', immediate),
                     ('input_size', input_size),
                     ('output_size', output_size)
                     ]
            con = [('clk', clk),
                   ('rst', rst),
                   ('req_l', req_l),
                   ('ack_l', ack_l),
                   ('req_r', req_r),
                   ('ack_r', ack_r),
                   ('din', din),
                   ('dout', dout)]
            m.Instance(operator, '%s_%s' % (op, no), param, con)

        return m

    def create_wires(self, m: Module()) -> dict:
        df = self.df_compat
        data_width = m.get_params()['data_width']
        wires = {}
        for no in df.nodes:
            for n in df.successors(no):
                req_r = m.Wire('req_%s_%s' % (no, n))
                wires[req_r.name] = req_r
            op = str.lower(df.nodes[no]['op'])
            if op == 'in':
                req_r = m.Output('din_req_%s' % no)
                ack_r = m.Input('din_ack_%s' % no)
                d = m.Input('din_%s' % no, data_width)
                wires[req_r.name] = req_r
                wires[ack_r.name] = ack_r
                wires[d.name] = d
                ack_r = m.Wire('ack_%s' % no)
                d = m.Wire('d%s' % no, data_width)
                wires[ack_r.name] = ack_r
                wires[d.name] = d
            elif op == 'out':
                parent = [n for n in df.predecessors(no)][0]
                req_r = m.Input('dout_req_%s' % no)
                ack_r = m.Output('dout_ack_%s' % no)
                d = m.Output('dout_%s' % no, data_width)
                wires['req_%s' % parent] = req_r
                wires['ack_%s' % parent] = ack_r
                wires['d%s' % parent] = d
            else:
                ack_r = m.Wire('ack_%s' % no)
                d = m.Wire('d%s' % no, data_width)
                wires[ack_r.name] = ack_r
                wires[d.name] = d

        return wires

    def make_async_operator(self) -> Module():
        m = Module('async_operator')
        data_width = m.Parameter('data_width', 32)
        op = m.Parameter('op', 'reg')
        immediate = m.Parameter('immediate', data_width)
        input_size = m.Parameter('input_size', 1)
        output_size = m.Parameter('output_size', 1)

        clk = m.Input('clk')
        rst = m.Input('rst')
        req_l = m.OutputReg('req_l', input_size)
        ack_l = m.Input('ack_l', input_size)
        req_r = m.Input('req_r', output_size)
        ack_r = m.Output('ack_r')
        din = m.Input('din', Mul(data_width, input_size))
        dout = m.Output('dout', data_width)

        din_r = m.Reg('din_r', Mul(data_width, input_size))
        has_all = m.Wire('has_all')
        req_r_all = m.Wire('req_r_all')
        ack_r_all = m.Reg('ack_r_all', output_size)
        has = m.Reg('has', input_size)

        i = m.Integer('i')
        g = m.Genvar('g')

        has_all.assign(Uand(has))
        req_r_all.assign(Uand(req_r))
        ack_r.assign(Uand(ack_r_all))
        m.Always(Posedge(clk))(
            If(rst)(
                has(Repeat(Int(0, 1, 2), input_size)),
                ack_r_all(Repeat(Int(0, 1, 2), output_size)),
                req_l(Repeat(Int(0, 1, 2), input_size))
            ).Else(
                For(i(0), i < input_size, i.inc())(
                    If(~has[i] & ~req_l[i])(
                        req_l[i](Int(1, 1, 2))
                    ),
                    If(ack_l[i])(
                        has[i](Int(1, 1, 2)),
                        req_l[i](Int(0, 1, 2))
                    )
                ),
                If(has_all & req_r_all)(
                    ack_r_all(Repeat(Int(1, 1, 2), output_size)),
                    has(Repeat(Int(0, 1, 2), input_size)),
                ),
                If(~has_all)(
                    ack_r_all(Repeat(Int(0, 1, 2), output_size)),
                )
            )
        )
        genfor = m.GenerateFor(g(0), g < input_size, g.inc(), 'rcv')
        genfor.Always(Posedge(ack_l[g]))(
            din_r[Mul(data_width, g):Mul(data_width, g + 1)](din[Mul(data_width, g):Mul(data_width, g + 1)])
        )

        operator = self.make_operator()
        param = [('input_size', input_size), ('op', op),
                 ('immediate', immediate), ('data_width', data_width)]
        con = [('din', din_r), ('dout', dout)]
        m.Instance(operator, 'operator', param, con)

        return m

    def make_operator(self) -> Module():
        m = Module('operator')
        fanin = m.Parameter('input_size', 1)
        op = m.Parameter('op', 'reg')
        immediate = m.Parameter('immediate', 0)
        data_width = m.Parameter('data_width', 32)

        din = m.Input('din', Mul(data_width, fanin))
        dout = m.Output('dout', data_width)

        unary_code = 'assign dout = din%simmediate;'
        binary_code = 'assign dout = din[data_width-1:0]%sdin[data_width*2-1:data_width];'
        ternary_code = 'assign dout = din[data_width-1:0]%sdin[data_width*2-1:data_width]%sdin[data_width*3-1:data_width*2];'

        genif = m.GenerateIf(fanin == 1, 'gen_op')
        genif.GenerateIf(OrList(Eql(op, "reg"), Eql(op, "in"), Eql(
            op, "out"))).EmbeddedCode('assign dout = din;')
        genif.GenerateIf(Eql(op, "addi")).EmbeddedCode(unary_code % '+')
        genif.GenerateIf(Eql(op, "subi")).EmbeddedCode(unary_code % '-')
        genif.GenerateIf(Eql(op, "muli")).EmbeddedCode(unary_code % '*')
        genif = genif.Else.GenerateIf(fanin == 2)
        genif.GenerateIf(Eql(op, "add")).EmbeddedCode(binary_code % '+')
        genif.GenerateIf(Eql(op, "sub")).EmbeddedCode(binary_code % '-')
        genif.GenerateIf(Eql(op, "mul")).EmbeddedCode(binary_code % '*')
        genif = genif.Else.GenerateIf(fanin == 3)
        genif.GenerateIf(Eql(op, "add")).EmbeddedCode(ternary_code % ('+', '+'))
        genif.GenerateIf(Eql(op, "sub")).EmbeddedCode(ternary_code % ('-', '-'))
        genif.GenerateIf(Eql(op, "mul")).EmbeddedCode(ternary_code % ('*', '*'))

        return m

    def get_immediate(self, no: dict) -> int:
        immediate = 0
        operators = ['addi', 'subi', 'muli']
        name = str.lower(no['op'])
        if name in operators:
            immediate = int(no['value'])
        return immediate

    def create_con_node(self, no: str, op: str) -> list:
        df = self.df_compat
        din = ''
        req_l = ''
        ack_l = ''
        req_r = ''
        dout = ''
        ack_r = ''

        if op == 'in':
            req_l = 'din_req_%s' % no
            ack_l = 'din_ack_%s' % no
            ack_r = 'ack_%s' % no
            din = 'din_%s' % no
            dout = 'd%s' % no
            req_r = '{'
            for d in df.successors(no):
                req_r += 'req_%s_%s, ' % (no, d)
            req_r = req_r[:-2]
            req_r += '}'
        elif op == 'out':
            req_r = 'dout_req_%s' % no
            ack_r = 'dout_ack_%s' % no
            dout = 'dout_%s' % no
            for d in df.predecessors(no):
                req_l = 'req_%s_%s' % (d, no)
                ack_l = 'ack_%s' % d
                din = 'd%s' % d
                break
        else:
            req_l = '{'
            ack_l = '{'
            din = '{'
            req_r = '{'
            ack_r = ''
            dout = ''
            for d in df.successors(no):
                req_r += 'req_%s_%s, ' % (no, d)
            req_r = req_r[:-2]
            req_r += '}'
            ack_r += 'ack_%s' % no
            dout += 'd%s' % no
            portsl = [0 for _ in df.predecessors(no)]
            for d in df.predecessors(no):
                portsl[int(df.edges[(d, no)]['port'])] = d
                req_l += 'req_%s_%s, ' % ('%s', no)
                ack_l += 'ack_%s, '
                din += 'd%s, '
            req_l = req_l[:-2]
            ack_l = ack_l[:-2]
            din = din[:-2]
            req_l += '}'
            ack_l += '}'
            din += '}'
            portsl = tuple(reversed(portsl))
            req_l = req_l % portsl
            ack_l = ack_l % portsl
            din = din % portsl

        req_l = EmbeddedCode(req_l)
        ack_l = EmbeddedCode(ack_l)
        din = EmbeddedCode(din)
        req_r = EmbeddedCode(req_r)
        ack_r = EmbeddedCode(ack_r)
        dout = EmbeddedCode(dout)
        con = req_l, ack_l, din, req_r, ack_r, dout

        return con

    def make_producer(self) -> Module():
        m = Module('producer')
        producer_id = m.Parameter('producer_id', 0)
        data_width = m.Parameter('data_width', 8)
        fail_rate = m.Parameter('fail_rate', 0)
        is_const = m.Parameter('is_const', 'false')
        initial_value = m.Parameter('initial_value', 0)
        clk = m.Input('clk')
        rst = m.Input('rst')
        req = m.Input('req')
        ack = m.OutputReg('ack')
        dout = m.OutputReg('dout', data_width)
        count = m.OutputReg('count', 32)

        dout_next = m.Reg('dout_next', data_width)
        stop = m.Reg('stop')
        randd = m.Real('randd')
        m.Always(Posedge(clk))(
            If(rst)(
                dout(initial_value),
                dout_next(initial_value),
                ack(0),
                count(0),
                stop(0),
                randd(EmbeddedCode('$abs($random%101)+1')),
            ).Else(
                ack(0),
                randd(EmbeddedCode('$abs($random%101)+1')),
                stop(Mux(randd > fail_rate, 0, 1)),
                # If(ack)(
                #    Write("p_%d,%d\\n",producer_id,dout)
                # ),
                If(req & ~ack & Not(stop))(
                    ack(1),
                    dout(dout_next),
                    If(is_const == "false")(
                        dout_next.inc()
                    ),
                    count.inc()
                )
            )
        )

        return m

    def make_consumer(self) -> Module():
        m = Module('consumer')
        consumer_id = m.Parameter('consumer_id', 0)
        data_width = m.Parameter('data_width', 8)
        fail_rate = m.Parameter('fail_rate', 0)
        clk = m.Input('clk')
        rst = m.Input('rst')
        req = m.OutputReg('req')
        ack = m.Input('ack')
        din = m.Input('din', data_width)
        count = m.OutputReg('count', 32)
        stop = m.Reg('stop')
        randd = m.Real('randd')
        m.Always(Posedge(clk))(
            If(rst)(
                req(0),
                count(0),
                stop(0),
                randd(EmbeddedCode('$abs($random%101)+1'))
            ).Else(
                req(0),
                randd(EmbeddedCode('$abs($random%101)+1')),
                stop(Mux(randd > fail_rate, 0, 1)),
                If(Not(stop))(
                    req(1)
                ),
                If(ack)(
                    count.inc(),
                    # Write("c_%d, %d\\n", consumer_id, din)
                )
            )
        )
        return m
