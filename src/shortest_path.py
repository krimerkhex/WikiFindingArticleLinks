import argparse
import logging
import sys
from cache_wiki import Graph


def ssp_rec(graph: Graph, cur: str, end: str, path: list, full_path: list):
    path.append(cur)
    for i in list(graph.data[cur]):
        if i == end:
            path.append(i)
            full_path.append(path)
            break
        elif i != end and i not in path:
            full_path.append(ssp_rec(graph, i, end, path.copy(), full_path))

    return path


def search_short_path(graph: Graph, start: str, end: str):
    if start not in graph.data or end not in graph.data:
        return False
    path = [start]
    full_path = []
    for i in list(graph.data[start]):
        ssp_rec(graph, i, end, path.copy(), full_path)
    l = graph.data.number_of_nodes() + 1
    if len(full_path) > 0:
        for i in full_path:
            if end in i and l > len(i):
                l = len(i)
                path = i
    if end not in path:
        path.clear()
    return path


def print_path(path: list, flag: bool):
    if len(path) == 0:
        print("Path not found")
    elif flag:
        st = ""
        for i in path:
            st += i + (' -> ' if i != path[-1] else '')
        print(st)


def init_args(args):
    args.add_argument('-v',
                      help="""This flag show you path of shorted way. Default value is False""",
                      action='store_true', dest='v')
    args.add_argument('--from', type=str,
                      help="""This flag describes the starting node. Default value is not specified""",
                      required=True, dest='f')
    args.add_argument('--to', type=str,
                      help="""This flag describes the ending node. Default value is not specified""",
                      required=True, dest='t')
    args.add_argument('--non-directed',
                      help="""The flag enables bidirectional connections in the graph, if mentioned.
                      The default value means that the nodes are unidirectional""",
                      action='store_true', dest='nd')
    return args.parse_args()


def args_validation(args) -> bool:
    return len(args.f) != 0 and len(args.t) != 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Shortcuts: find the shortest path length between two pages in serialized database')
    args = init_args(parser)
    if args_validation(args):
        path = '../materials/wiki.json'
        logging.info(f"Parsing graph starting, path to file: {path}")
        graph = Graph(args.nd)
        graph.load_graph(path)
        if args.f in graph.data and args.t in graph.data:
            print_path(search_short_path(graph, args.f, args.t), args.v)
        else:
            logging.error(f"""Graph doesn't have one/both of them : --from "{args.f}" or --to "{args.t}".""")
    else:
        logging.error("--from or --to is empty. This field is necessarily.")


def mine():
    G = Graph(True)
    G.load_graph('../materials/wiki.json')
    print_path(search_short_path(G, 'Erdős_number', "Mathematics Genealogy Project"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
    main()