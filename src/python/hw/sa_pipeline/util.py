from math import ceil, log2, sqrt
import subprocess


def to_bytes_string_list(conf_string):
    list_ret = []
    for i in range(len(conf_string), 0, -8):
        list_ret.append(conf_string[i - 8: i])
    return list_ret


def state(val, size):
    return format(val, "0%dx" % size)


def commands_getoutput(cmd):
    byte_out = subprocess.check_output(cmd.split())
    str_out = byte_out.decode("utf-8")
    return str_out


def get_n_bits(n):
    if n < 2:
        return 1
    else:
        return int(ceil(log2(n)))


def create_rom_files(sa_comp, path: str):
    sa_graph = sa_comp.per_graph
    n_cells = sa_comp.per_graph.n_cells
    n_neighbors = sa_comp.n_neighbors
    n_threads = sa_comp.n_threads

    c_bits = ceil(log2(n_cells))
    t_bits = ceil(log2(n_threads))
    t_bits = 1 if t_bits == 0 else t_bits
    node_bits = c_bits

    sa_graph.reset_random()

    c_n = []
    n_c = []
    for i in range(n_threads):
        c_n_i, n_c_i = sa_graph.get_initial_n2c()
        c_n.append(c_n_i)
        n_c.append(n_c_i)

    cn_str_f = '{:0%db}' % (node_bits + 1)
    nc_str_f = '{:0%db}' % c_bits
    n_str_f = '{:0%db}' % (node_bits + 1)
    t_str = '{:0%db}' % t_bits

    cn_w = []
    nc_w = []
    n_w = []
    for t in range(pow(2, ceil(sqrt(n_threads)))):
        cn_w.append([cn_str_f.format(0)
                     for _ in range(ceil(sqrt(n_cells)) * ceil(sqrt(n_cells)))])
        nc_w.append([nc_str_f.format(0)
                     for _ in range(ceil(sqrt(n_cells)) * ceil(sqrt(n_cells)))])

    for c in range(pow(2, ceil(sqrt(n_cells)))):
        n_w.append([n_str_f.format(0) for _ in range(n_neighbors)])
    for k in sa_graph.neighbors.keys():
        idx = 0
        for n in sa_graph.neighbors[k]:
            n_w[k][idx] = n_str_f.format((1 << node_bits) | n)
            idx += 1

    for t in range(len(c_n)):
        for cni in range(len(c_n[t])):
            if c_n[t][cni] is not None:
                cn_w[t][cni] = cn_str_f.format((1 << node_bits) | c_n[t][cni])

    for t in range(len(n_c)):
        for nci in range(len(n_c[t])):
            if n_c[t][nci] is not None:
                nc_w[t][nci] = nc_str_f.format(n_c[t][nci])

    with open(path + '/th.rom', 'w') as f:
        for i in range(pow(2, ceil(sqrt(n_threads)))):
            f.write(t_str.format(0))
            f.write('\n')
        f.close()

    with open(path + '/n_c.rom', 'w') as f:
        for t in nc_w:
            for d in t:
                f.write(d)
                f.write('\n')
        if n_threads == 1:
            for d in range(n_cells):
                f.write(nc_str_f.format(0))
                f.write('\n')
        f.close()
    with open(path + '/c_n.rom', 'w') as f:
        for t in cn_w:
            for d in t:
                f.write(d)
                f.write('\n')
        if n_threads == 1:
            for d in range(n_cells):
                f.write(cn_str_f.format(0))
                f.write('\n')
        f.close()

    for i in range(n_neighbors):
        with open(path + '/n%d.rom' % i, 'w') as f:
            for c in range(n_cells):
                f.write(n_w[c][i])
                f.write('\n')
            f.close()


def create_dot_from_rom_files(rom_file: str, prefix: str, output_path: str, n_threads: int, n_cells: int):
    output_dot_files = [prefix + '%d.dot_db' % i for i in range(n_threads)]
    dot_head = ('digraph layout{\n rankdir=TB;\n splines=ortho;\n node [style=filled shape=square fixedsize=true '
                'width=0.6];\n')
    dot_foot = 'edge [constraint=true, style=invis];\n'
    sqrt_cells = ceil(sqrt(n_cells))

    for i in range(sqrt_cells):
        for j in range(sqrt_cells):
            dot_foot = dot_foot + '%d' % (j * sqrt_cells + i)
            if (j + 1) % sqrt_cells == 0:
                dot_foot = dot_foot + ';\n'
            else:
                dot_foot = dot_foot + ' -> '

    for i in range(n_cells):
        if i % sqrt_cells == 0:
            dot_foot = dot_foot + 'rank = same {'
        dot_foot = dot_foot + '%d' % i
        if (i + 1) % sqrt_cells == 0:
            dot_foot = dot_foot + '};\n'
        else:
            dot_foot = dot_foot + ' -> '

    dot_foot = dot_foot + '}'

    str_out = [dot_head for i in range(n_threads)]
    file_lines = []
    with open(rom_file) as f:
        file_lines = f.readlines()
        f.close()
    for t in range(n_threads):
        c = 0
        while c < n_cells:
            c_content = file_lines.pop(0)
            if '//' in c_content:
                continue
            c_content = c_content.split('\n')[0]
            v = int(c_content, 16)
            v = v & (n_cells - 1)
            v = str(v)
            # print('%d[label="%s", fontsize=8, fillcolor="%s"];\n' % (
            #    c, '' if int(c_content, 16) == 0 else v, '#ffffff' if int(c_content, 16) == 0 else '#d9d9d9'))
            str_out[t] += '%d[label="%s", fontsize=8, fillcolor="%s"];\n' % (
                c, '' if int(c_content, 16) == 0 else v, '#ffffff' if int(c_content, 16) == 0 else '#d9d9d9')
            c += 1
        str_out[t] += dot_foot

    for t in range(n_threads):
        with open(output_path + output_dot_files[t], 'w') as f:
            f.write(str_out[t])
        f.close()
