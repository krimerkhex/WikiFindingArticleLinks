import os
import sys
import logging
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
from json import loads


def pngCreationFromJson(wikiJson):
    G = nx.Graph(wikiJson)
    nx.draw(G, font_weight='bold')
    plt.show()


def getJson():
    res = ''
    try:
        script_dir = os.path.dirname(sys.argv[0])
        with open(os.path.join(script_dir, '..\\materials\\wiki.json'), 'r', encoding="utf-16") as wikiJson:
            res = loads(wikiJson.read())
    except Exception:
        logging.error("Error while creating json file", exc_info=True)
    return res


def main():
    error = 0
    logging.info("Start work program")
    wikiJson = getJson()
    if not wikiJson:
        error = 1
    else:
        pngCreationFromJson(wikiJson)
    return error


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stdout)
    logging.info("The program terminated with a code: " + str(main()) + '\n')
