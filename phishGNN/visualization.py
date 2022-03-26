import collections
import os
from typing import Dict, Set

from pyvis.network import Network
import networkx as nx
import torch
from torch_geometric.data import Data

from utils import tensor_to_tuple_list, extract_domain_name


ROOT_COLOR          = '#0096FF'
DOMAIN_COLOR        = '#73FCD6'
OUT_DOMAIN_COLOR    = '#FFD479'
ERROR_COLOR         = '#FF7E79'


def visualize(
    data: Data,
    width: int=1000,
    height: int=800,
    html_save_file: str="graph.html",
):
    """Create an html file with the corresponding graph
    plotted using the pyvis library.
    """

    folder = os.path.dirname(html_save_file)
    if folder != '':
        os.makedirs(folder, exist_ok=True)

    edge_index = data.edge_index
    viz_utils = data.pos
    id_to_url = {v: k for k, v in viz_utils['url_to_id'].items()}
    edges = tensor_to_tuple_list(edge_index)
    # edges = [(x, y) for x, y in edges if x == 0]

    G = nx.MultiDiGraph()
    G.add_edges_from(edges)

    net = Network(width=width, height=height, directed=True)
    net.from_nx(G)

    net.show_buttons(filter_=['physics'])

    root_url = id_to_url[0]
    domain = extract_domain_name(root_url)
    for node in net.nodes:
        node_url = id_to_url[node['id']]
        node['size'] = 15
        node['label'] = ''
        if domain in node_url:
            node['color'] = DOMAIN_COLOR
        else:
            node['color'] = OUT_DOMAIN_COLOR
        if node['id'] == 0:
            node['color'] = ROOT_COLOR
        if node_url in viz_utils['error_pages']:
            node['color'] = ERROR_COLOR

        node['title'] = f'<a href="{id_to_url[node["id"]]}">{id_to_url[node["id"]]}</a>'

    count_edges = dict(collections.Counter(edges))
    for e in net.edges:
        t = (e['from'], e['to'])
        nb_occurences = 0
        if t not in count_edges:
            nb_occurences = count_edges[(e['to'], e['from'])]
        else:
            nb_occurences = count_edges[t]
        if nb_occurences > 1:
            e['label'] = nb_occurences

    net.save_graph(html_save_file)

    with open(html_save_file, 'a') as html_file:
        graph_data_html = f"""
            <div id="graph_data" 
                is_phishing="{data.y == 1.}"
                url="{root_url}"
                nb_edges="{len(edges)}">
            </div>
        """
        html_file.write(graph_data_html)
