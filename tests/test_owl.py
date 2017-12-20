# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
from pathlib import Path

from onto2nx import OWLParser, parse_owl, parse_owl_xml
from tests.contants import pizza_iri, test_owl_ado, test_owl_pizza, test_owl_wine
from tests.mocks import mock_parse_owl_rdf, mock_parse_owl_xml

EXPECTED_PIZZA_NODES = {
    'Pizza',
    'Topping',
    'CheeseTopping',
    'FishTopping',
    'MeatTopping',
    'TomatoTopping'
}

EXPECTED_PIZZA_EDGES = {
    ('CheeseTopping', 'Topping'),
    ('FishTopping', 'Topping'),
    ('MeatTopping', 'Topping'),
    ('TomatoTopping', 'Topping')
}

wine_prefixes = {
    'owl': "http://www.w3.org/2002/07/owl#",
    'rdf': "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
}

wine_classes = {
    'Region',
    'Vintage',
    'VintageYear',
    'Wine',
    'WineDescriptor',
    'WineColor',
    'WineTaste',
    'WineBody',
    'WineFlavor',
    'WineSugar',
    'Winery'
}

wine_individuals = {
    'Red',
    'Rose',
    'White',
    'Full',
    'Light',
    'Medium',
    'Delicate',
    'Moderate',
    'Strong',
    'Dry',
    'OffDry',
    'Sweet',

    # Wineries
    'Bancroft',
    'Beringer',
    'ChateauChevalBlanc',
    'ChateauDeMeursault',
    'ChateauDYchem',
    'ChateauLafiteRothschild',
    'ChateauMargauxWinery',
    'ChateauMorgon',
    'ClosDeLaPoussie',
    'ClosDeVougeot',
    'CongressSprings',
    'Corbans',
    'CortonMontrachet',
    'Cotturi',
    'DAnjou',
    'Elyse',
    'Forman',
    'Foxen',
    'GaryFarrell',
    'Handley',
    'KalinCellars',
    'KathrynKennedy',
    'LaneTanner',
    'Longridge',
    'Marietta',
    'McGuinnesso',
    'Mountadam',
    'MountEdenVineyard',
    'PageMillWinery',
    'PeterMccoy',
    'PulignyMontrachet',
    'SantaCruzMountainVineyard',
    'SaucelitoCanyon',
    'SchlossRothermel',
    'SchlossVolrad',
    'SeanThackrey',
    'Selaks',
    'SevreEtMaine',
    'StGenevieve',
    'Stonleigh',
    'Taylor',
    'Ventana',
    'WhitehallLane',

    # Wines
}

wine_nodes = wine_classes | wine_individuals

wine_subclasses = {

    ('WineSugar', 'WineTaste'),
    ('WineTaste', 'WineDescriptor'),
    ('WineColor', 'WineDescriptor')
}

wine_membership = {
    ('Red', 'WineColor'),
    ('Rose', 'WineColor'),
    ('White', 'WineColor'),
    ('Full', 'WineBody'),
    ('Light', 'WineBody'),
    ('Medium', 'WineBody'),
    ('Delicate', 'WineFlavor'),
    ('Moderate', 'WineFlavor'),
    ('Strong', 'WineFlavor'),
    ('Dry', 'WineSugar'),
    ('OffDry', 'WineSugar'),
    ('Sweet', 'WineSugar'),

    # Winery Membership
    ('Bancroft', 'Winery'),
    ('Beringer', 'Winery'),
    ('ChateauChevalBlanc', 'Winery'),
    ('ChateauDeMeursault', 'Winery'),
    ('ChateauDYchem', 'Winery'),
    ('ChateauLafiteRothschild', 'Winery'),
    ('ChateauMargauxWinery', 'Winery'),
    ('ChateauMorgon', 'Winery'),
    ('ClosDeLaPoussie', 'Winery'),
    ('ClosDeVougeot', 'Winery'),
    ('CongressSprings', 'Winery'),
    ('Corbans', 'Winery'),
    ('CortonMontrachet', 'Winery'),
    ('Cotturi', 'Winery'),
    ('DAnjou', 'Winery'),
    ('Elyse', 'Winery'),
    ('Forman', 'Winery'),
    ('Foxen', 'Winery'),
    ('GaryFarrell', 'Winery'),
    ('Handley', 'Winery'),
    ('KalinCellars', 'Winery'),
    ('KathrynKennedy', 'Winery'),
    ('LaneTanner', 'Winery'),
    ('Longridge', 'Winery'),
    ('Marietta', 'Winery'),
    ('McGuinnesso', 'Winery'),
    ('Mountadam', 'Winery'),
    ('MountEdenVineyard', 'Winery'),
    ('PageMillWinery', 'Winery'),
    ('PeterMccoy', 'Winery'),
    ('PulignyMontrachet', 'Winery'),
    ('SantaCruzMountainVineyard', 'Winery'),
    ('SaucelitoCanyon', 'Winery'),
    ('SchlossRothermel', 'Winery'),
    ('SchlossVolrad', 'Winery'),
    ('SeanThackrey', 'Winery'),
    ('Selaks', 'Winery'),
    ('SevreEtMaine', 'Winery'),
    ('StGenevieve', 'Winery'),
    ('Stonleigh', 'Winery'),
    ('Taylor', 'Winery'),
    ('Ventana', 'Winery'),
    ('WhitehallLane', 'Winery'),
}

wine_edges = wine_subclasses | wine_membership

ado_expected_nodes_subset = {
    'immunotherapy',
    'In_vitro_models',
    'white',
    'ProcessualEntity'
}

ado_expected_edges_subset = {
    ('control_trials_study_arm', 'Study_arm'),
    ('copper', 'MaterialEntity'),
    ('curcumin_plant', 'plant'),
    ('cytokine', 'cell_signalling')  # Line 12389 of ado.owl
}

expected_prefixes = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "owl": "http://www.w3.org/2002/07/owl#"
}


class TestOwlUtils(unittest.TestCase):
    def test_value_error(self):
        with self.assertRaises(ValueError):
            OWLParser()

    def test_invalid_owl(self):
        with self.assertRaises(Exception):
            parse_owl('http://example.com/not_owl')


class TestParse(unittest.TestCase):
    """This class tests the parsing of OWL documents and doesn't need a connection"""

    def test_parse_pizza_file(self):
        owl = parse_owl(Path(test_owl_pizza).as_uri())
        self.assertEqual(EXPECTED_PIZZA_NODES, set(owl.nodes()))
        self.assertEqual(EXPECTED_PIZZA_EDGES, set(owl.edges()))

    @mock_parse_owl_rdf
    @mock_parse_owl_xml
    def test_parse_pizza_url(self, m1, m2):
        owl = parse_owl(pizza_iri)
        self.assertEqual(pizza_iri, owl.graph['IRI'])
        self.assertEqual(EXPECTED_PIZZA_NODES, set(owl.nodes()))
        self.assertEqual(EXPECTED_PIZZA_EDGES, set(owl.edges()))

    def test_parse_wine_file(self):
        owl = parse_owl(Path(test_owl_wine).as_uri())

        for node in sorted(wine_classes):
            self.assertIn(node, owl)

        for node in sorted(wine_individuals):
            self.assertIn(node, owl)

        for u, v in sorted(wine_subclasses):
            self.assertIn(u, owl)
            self.assertIn(v, owl.edge[u])

        for u, v in sorted(wine_membership):
            self.assertIn(u, owl)
            self.assertIn(v, owl.edge[u])

    @mock_parse_owl_rdf
    @mock_parse_owl_xml
    def test_ado_local(self, mock1, mock2):
        ado_path = Path(test_owl_ado).as_uri()
        owl = parse_owl(ado_path)

        self.assertLessEqual(ado_expected_nodes_subset, set(owl.nodes_iter()))
        self.assertLessEqual(ado_expected_edges_subset, set(owl.edges_iter()))


if __name__ == '__main__':
    unittest.main()
