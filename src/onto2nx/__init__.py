# -*- coding: utf-8 -*-

"""A package for parsing ontologies in the OWL and OBO format into NetworkX graphs."""

from .aba import aba_onto2nx
from .api import parse_owl
from .owl_rdf import parse_owl_rdf
from .owl_xml import OWLParser, parse_owl_xml

__version__ = '0.1.1-dev'

__title__ = 'onto2nx'
__description__ = "A package for parsing ontologies in the OWL and OBO format into NetworkX graphs"
__url__ = 'https://github.com/cthoyt/onto2nx'

__author__ = 'Charles Tapley Hoyt and Aliaksandr Masny'
__email__ = 'cthoyt@gmail.com'

__license__ = 'GPL 3.0 License'
__copyright__ = 'Copyright (c) 2016-2018 Charles Tapley Hoyt'
