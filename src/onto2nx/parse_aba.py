import requests
import networkx as nx

ABA_API_FORMAT = 'http://api.brain-map.org/api/v2/structure_graph_download/{}.json'


def parser(str_gr_id=10):
    """ Downloads and parse the Allen Brain Atlas ontologies into a network object

    StructureGraphs ID corresponds to the following ontologies:
    1 – "Mouse Brain Atlas",
    10 – "Human Brain Atlas", 8 – "Non-Human Primate Brain Atlas",
    15 – "Glioblastoma",
    16 – "Developing Human Brain Atlas", 17 – "Developing Mouse Brain Atlas".

    More information about Allen Brain Atlas API can be found using following links:
    http://help.brain-map.org/display/api/Atlas+Drawings+and+Ontologies#AtlasDrawingsandOntologies-StructuresAndOntologies
    http://help.brain-map.org/display/api/Downloading+an+Ontology%27s+Structure+Graph

    :param str_gr_id: StructureGraph ID, default 10 refers to Human Brain Atlas Ontology
    :return: a networkx with the brain regions as nodes, and the subclass/instanceof relationships as edges
    :rtype: :class:`networkx.DiGraph`
    """
    netw = nx.DiGraph()

    # Downloading and parsing json structure graph
    r = requests.get(url=ABA_API_FORMAT.format(str_gr_id))
    str_gr_json = r.json()

    def add_children(tree, netw):
        for child in tree['children']:
            child_dct = {key: value for key, value in child.items() if key not in ['children', 'id']}
            # not including children information into the attributes
            # while it will be edges
            netw.add_node(child['id'], attr_dict=child_dct)
            netw.add_edge(tree['id'], child['id'])
            add_children(child, netw)

    # Putting information into the network
    # Edge case for the recursive function
    root = str_gr_json['msg'][0]
    root_dct = {key: value for key, value in root.items() if key not in ['children', 'id']}
    netw.add_node(root['id'], attr_dict=root_dct)

    add_children(root, netw)

    return netw
