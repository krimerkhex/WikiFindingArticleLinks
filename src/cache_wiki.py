import sys
import argparse
import requests
import bs4
import logging
import networkx as nx
from json import dumps, loads


class Graph:
    def __init__(self, flag: bool):
        self.data = nx.DiGraph() if flag else nx.Graph()
        self.list_place = {}

    def update_graph(self, nodes_o, list_w=[]):
        self.list_place[nodes_o] = True
        for i in list_w:
            if i:
                self.data.add_edge(nodes_o, i)
                self.data.edges[nodes_o, i]['link'] = f"https://en.wikipedia.org/wiki/{i}"
                if i not in self.list_place:
                    self.list_place[i] = False

    def check(self, str):
        return self.list_place[str]

    def load_graph(self, path):
        res = ''
        try:
            with open(path, 'r', encoding="utf-16") as wikiJson:
                res = loads(wikiJson.read())
        except Exception:
            logging.error("Error while creating json file", exc_info=True)
        self.data = nx.DiGraph(res)

def saveNewJson(jsonStr):
    error = False
    logging.info("attempt to (create / overwrite) the wiki.json file")
    try:
        with open('..\materials\wiki.json', 'w', encoding="utf-16") as NewJson:
            NewJson.write(jsonStr)
            logging.info("Successful")
    except Exception:
        error = True
        logging.error("Error while creating json file", exc_info=True)
        logging.info(
            "Make sure that the location where the script is run matches this path '..\materials\graph.json'.")
    return error


def graphJsonCreation(graph):
    logging.info("start graphJsonCreation function")
    return saveNewJson(dumps(nx.to_dict_of_dicts(graph.data)))


def get_a(see_also) -> list:
    see_also_h2 = see_also.find_parent()
    next_h2 = see_also_h2.find_next_sibling("h2")
    temp = []
    while see_also_h2 != next_h2:
        if (see_also_h2.name == 'ul' and str(see_also_h2).count('<ul>')) or str(see_also_h2).count(
                '<div class="div-col"'):
            temp += see_also_h2.find_all('li')
        see_also_h2 = see_also_h2.find_next_sibling()
    return temp


def get_wiki_see_also(page_name) -> list:
    if len(page_name) != 0:
        response = requests.get(url=f"https://en.wikipedia.org/wiki/{page_name}")
        links = []
        if response.status_code == 200:
            try:
                logging.info(f"Code visited wikipedia page with page name is {page_name}")
                soup = bs4.BeautifulSoup(response.text, "html.parser")
                see_also = soup.find(id='See_also')
                if see_also is not None:
                    see_also = get_a(see_also)
                    temp = ''
                    for li_line in see_also:
                        temp = li_line.find('a').get('href')
                        if temp is not None:
                            if temp.count('/wiki/'):
                                links.append(li_line.find('a').get('title'))
            except Exception as ex:
                logging.critical(f"Current linens to parse\n{page_name}, {ex}")
        else:
            logging.critical(f"Bad answer from server: {response.status_code}")
        return links


def initArgs(parser):
    parser.add_argument('-d', type=int,
                        help="Indicates the deep \
                              Argument format: 5\n \
                              Default value is 3", default=1)
    parser.add_argument('-p', type=str, help="Wikipedia article title", default="Erdős_number")
    return parser.parse_args()


def deep_counter(graph, args):
    temp_1 = get_wiki_see_also(args.p)
    temp_2 = []
    for j in range(args.d):
        graph.update_graph(args.p, temp_1)
        for deep in range(args.d):
            for name in temp_1:
                if not graph.check(name):
                    current = get_wiki_see_also(name)
                    if len(current) != 0:
                        temp_2 += current
                    graph.update_graph(name, current)
                    if graph.data.number_of_nodes() > 1000:
                        break
            print(f"Numbers nodes {graph.data.number_of_nodes()}")
            if graph.data.number_of_nodes() > 1000:
                break
            temp_1, temp_2 = temp_2, []
    return graph


def main():
    parser = argparse.ArgumentParser(description='Old Style: create json on based wiki pages and links')
    args = initArgs(parser)
    if args.p is not None and args.d > 0:
        graph = deep_counter(Graph(False), args)
        graphJsonCreation(graph)
    else:
        logging.error("You don't given article title")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
    main()
