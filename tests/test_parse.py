import unittest

from onto2nx.ontospy import Ontospy

from onto2nx import parse_aba
import networkx as nx


class TestImport(unittest.TestCase):
    def test_wine(self):
        wine_iri = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine'
        o = Ontospy(uri_or_path=wine_iri)

        self.assertEquals(len(o.classes), 74)
        self.assertEquals(len(o.properties), 13)
        self.assertEquals(len(o.annotationProperties), 0)
        self.assertEquals(len(o.objectProperties), 12)
        self.assertEquals(len(o.datatypeProperties), 1)
        self.assertEquals(len(o.skosConcepts), 0)
        self.assertEquals(len(o.rdfgraph), 1839)

    def test_pizza(self):
        pizza_iri = 'http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl'
        o = Ontospy(uri_or_path=pizza_iri)

        self.assertEquals(len(o.classes), 0)
        self.assertEquals(len(o.properties), 0)
        self.assertEquals(len(o.annotationProperties), 0)
        self.assertEquals(len(o.objectProperties), 0)
        self.assertEquals(len(o.datatypeProperties), 0)
        self.assertEquals(len(o.skosConcepts), 0)
        self.assertEquals(len(o.rdfgraph), 40)

    def test_ado(self):
        ado_iri = 'http://data.bioontology.org/ontologies/ADO/submissions/3/download?apikey=8b5b7825-538d-40e0-9e9e-5ab9274a9aeb'
        o = Ontospy(uri_or_path=ado_iri)

        self.assertEquals(len(o.classes), 1556)
        self.assertEquals(len(o.properties), 28)
        self.assertEquals(len(o.annotationProperties), 16)
        self.assertEquals(len(o.objectProperties), 12)
        self.assertEquals(len(o.datatypeProperties), 0)
        self.assertEquals(len(o.skosConcepts), 0)
        self.assertEquals(len(o.rdfgraph), 10836)


class TestAllenParser(unittest.TestCase):
    def test_aba_human(self):
        aba_human = parse_aba.parser(str_gr_id=10)

        # check if ontology is a tree
        # if not, then something is wrong with the id
        self.assertTrue(nx.is_tree(aba_human))
        # check if root is the (human) brain with id = 4005
        self.assertEquals(nx.topological_sort(aba_human)[0], 4005)

    def test_aba_mouse(self):
        aba_mouse = parse_aba.parser(str_gr_id=1)

        # check if ontology is a tree
        # if not, then something is wrong with the id
        self.assertTrue(nx.is_tree(aba_mouse))
        # check if root is the (mouse) brain with id = 997
        self.assertEquals(nx.topological_sort(aba_mouse)[0], 997)
