import types

import owlready


def nx_to_ontology(graph, source_node, output_path, base_iri):
    """
    Graph nodes are ID's, and have a 'label' in the node data with the right label

    :param graph:
    :param source_node:
    :param output_path:
    :param base_iri:
    :return:
    """
    ontology = owlready.Ontology(base_iri)

    parent_lookup = {
        source_node: types.new_class(source_node, (owlready.Thing,), kwds={"ontology": ontology})
    }

    def recur(pnode):
        for neighbor in graph.neighbors(pnode):
            data = graph.node[neighbor]
            neighbor_class = types.new_class(neighbor, (parent_lookup[pnode],), kwds={"ontology": ontology})
            owlready.ANNOTATIONS[neighbor_class].add_annotation(owlready.rdfs.label, data['label'])
            recur(neighbor)

    recur(source_node)

    ontology.save(filename=output_path)
