# -*- coding: utf-8 -*-

import logging

import os

log = logging.getLogger(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
owl_dir_path = os.path.join(dir_path, 'owl')

test_owl_pizza = os.path.join(owl_dir_path, 'pizza_onto.owl')
test_owl_wine = os.path.join(owl_dir_path, 'wine.owl')
test_owl_ado = os.path.join(owl_dir_path, 'ado.owl')

CHEBI_KEYWORD = 'CHEBI'
CELL_LINE_KEYWORD = 'CellLine'
HGNC_KEYWORD = 'HGNC'
MESH_DISEASES_KEYWORD = 'MeSHDisease'

pizza_iri = 'http://www.lesfleursdunormal.fr/static/_downloads/pizza_onto.owl'
wine_iri = 'http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine'
