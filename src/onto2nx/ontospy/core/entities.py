# !/usr/bin/env python
#  -*- coding: UTF-8 -*-

from __future__ import print_function

import rdflib
from itertools import count
# http://stackoverflow.com/questions/8628123/counting-instances-of-a-class
from colorama import Fore, Back, Style




from .utils import *


class RDF_Entity(object):
    """
    Pythonic representation of an RDF resource - normally not instantiated but used for
    inheritance purposes

    <triples> : a structure like this:
    [(rdflib.term.URIRef(u'http://xmlns.com/foaf/0.1/OnlineChatAccount'),
      rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#comment'),
      rdflib.term.Literal(u'An online chat account.')),
     (rdflib.term.URIRef(u'http://xmlns.com/foaf/0.1/OnlineChatAccount'),
      rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#subClassOf')]

    """

    _ids = count(0)

    def __repr__(self):
        return "<OntoSpy: RDF_Entity object for uri *%s*>" % (self.uri)

    def __init__(self, uri, rdftype=None, namespaces = None):
        """
        Init ontology object. Load the graph in memory, then setup all necessary attributes.
        """
        self.id = next(self._ids)

        self.uri = uri # rdflib.Uriref
        self.qname = self.__buildQname(namespaces)
        self.locale	 = inferURILocalSymbol(self.uri)[0]
        self.slug	 = None
        self.rdftype = rdftype
        self.triples = None
        self.rdfgraph = rdflib.Graph()
        self.namespaces = namespaces

        self._children = []
        self._parents = []
        # self.siblings = []

    def serialize(self, format="turtle"):
        """ xml, n3, turtle, nt, pretty-xml, trix are built in"""
        if self.triples:
            if not self.rdfgraph:
                self._buildGraph()
            return self.rdfgraph.serialize(format=format)
        else:
            return None

    def printSerialize(self, format="turtle"):
        printDebug("\n" + self.serialize(format))

    def printTriples(self):
        """ display triples """
        printDebug(Style.BRIGHT + self.uri + Style.RESET_ALL)
        for x in self.triples:
            printDebug(Fore.MAGENTA + "=> " + unicode(x[1]))
            printDebug(Fore.GREEN + ".... " + unicode(x[2]) + Fore.RESET)
        print("")

    def __buildQname(self, namespaces):
        """ extracts a qualified name for a uri """
        return uri2niceString(self.uri, namespaces)

    def _buildGraph(self):
        """
        transforms the triples list into a proper rdflib graph
        (which can be used later for querying)
        """
        for n in self.namespaces:
            self.rdfgraph.bind(n[0], rdflib.Namespace(n[1]))
        if self.triples:
            for terzetto in self.triples:
                self.rdfgraph.add(terzetto)

    # methods added to RDF_Entity even though they apply only to some subs

    def ancestors(self, cl=None, noduplicates=True):
        """ returns all ancestors in the taxonomy """
        if not cl:
            cl = self
        if cl.parents():
            bag = []
            for x in cl.parents():
                if x.uri != cl.uri: # avoid circular relationships
                    bag += [x] + self.ancestors(x, noduplicates)
                else:
                    bag += [x]
            # finally:
            if noduplicates:
                return remove_duplicates(bag)
            else:
                return bag
        else:
            return []


    def descendants(self, cl=None, noduplicates=True):
        """ returns all descendants in the taxonomy """
        if not cl:
            cl = self
        if cl.children():
            bag = []
            for x in cl.children():
                if x.uri != cl.uri: # avoid circular relationships
                    bag += [x] + self.descendants(x, noduplicates)
                else:
                    bag += [x]
            # finally:
            if noduplicates:
                return remove_duplicates(bag)
            else:
                return bag
        else:
            return []


    def parents(self):
        """wrapper around property"""
        return self._parents

    def children(self):
        """wrapper around property"""
        return self._children

    def getValuesForProperty(self, aPropURIRef):
        """
        generic way to extract some prop value eg
            In [11]: c.getValuesForProperty(rdflib.RDF.type)
            Out[11]:
            [rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#Class'),
             rdflib.term.URIRef(u'http://www.w3.org/2000/01/rdf-schema#Class')]
        """
        return list(self.rdfgraph.objects(None, aPropURIRef))


    def bestLabel(self, prefLanguage="en", qname_allowed=True, quotes=True):
        """
        facility for extrating the best available label for an entity

        ..This checks RFDS.label, SKOS.prefLabel and finally the qname local component
        """

        test = self.getValuesForProperty(rdflib.RDFS.label)
        out = ""

        if test:
            out = firstEnglishStringInList(test)
        else:
            test = self.getValuesForProperty(rdflib.namespace.SKOS.prefLabel)
            if test:
                out = firstEnglishStringInList(test)
            else:
                if qname_allowed:
                    out = self.locale

        if quotes and out:
            return addQuotes(out)
        else:
            return out

    def bestDescription(self, prefLanguage="en"):
        """
        facility for extrating the best available description for an entity

        ..This checks RFDS.label, SKOS.prefLabel and finally the qname local component
        """

        test_preds = [rdflib.RDFS.comment, rdflib.namespace.DCTERMS.description, rdflib.namespace.DC.description, rdflib.namespace.SKOS.definition ]

        for pred in test_preds:
            test = self.getValuesForProperty(pred)
            if test:
                return addQuotes(firstEnglishStringInList(test))
        return ""



class Ontology(RDF_Entity):
    """
    Pythonic representation of an OWL ontology
    """

    def __repr__(self):
        return "<OntoSpy: Ontology object for uri *%s*>" % (self.uri)


    def __init__(self, uri, rdftype=None, namespaces=None, prefPrefix=""):
        """
        Init ontology object. Load the graph in memory, then setup all necessary attributes.
        """
        super(Ontology, self).__init__(uri, rdftype, namespaces)
        # self.uri = uri # rdflib.Uriref
        self.prefix = prefPrefix
        self.slug = "ontology-" + slugify(self.qname)
        self.classes = []
        self.properties = []
        self.skosConcepts = []

    def annotations(self, qname=True):
        """
        wrapper that returns all triples for an onto.
        By default resources URIs are transformed into qnames
        """
        if qname:
            return sorted([(uri2niceString(x, self.namespaces)), (uri2niceString(y, self.namespaces)), z] for x, y, z in self.triples)
        else:
            return sorted(self.triples)

    def describe(self):
        """ shotcut to pull out useful info for interactive use """
        # self.printGenericTree()
        self.printTriples()
        self.stats()


    def stats(self):
        """ shotcut to pull out useful info for interactive use """
        printDebug("Classes.....: %d" % len(self.classes))
        printDebug("Properties..: %d" % len(self.properties))




class OntoClass(RDF_Entity):
    """
    Python representation of a generic class within an ontology.
    Includes methods for representing and querying RDFS/OWL classes


    domain_of_inferred: a list of dict
            [{<Class *http://xmlns.com/foaf/0.1/Person*>:
            [<Property *http://xmlns.com/foaf/0.1/currentProject*>,<Property *http://xmlns.com/foaf/0.1/familyName*>,
                etc....]},
        {<Class *http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing*>:
            [<Property *http://xmlns.com/foaf/0.1/based_near*>, etc...]},
            ]
    """

    def __init__(self, uri, rdftype=None, namespaces=None):
        """
        ...
        """
        super(OntoClass, self).__init__(uri, rdftype, namespaces)
        self.slug = "class-" + slugify(self.qname)
        
        self.domain_of = []
        self.range_of = []
        self.domain_of_inferred = []
        self.range_of_inferred = []
        self.ontology = None
        self.queryHelper = None	 # the original graph the class derives from

    def __repr__(self):
        return "<Class *%s*>" % ( self.uri)

    def instances(self):  # = all instances
        return self.all()

    def all(self):
        out = []
        if self.queryHelper:
            qres = self.queryHelper.getClassInstances(self.uri)
            out = [x[0] for x in qres]
        return out

    def count(self):
        if self.queryHelper:
            return self.queryHelper.getClassInstancesCount(self.uri)
        else:
            return 0


    def printStats(self):
        """ shotcut to pull out useful info for interactive use """
        printDebug("----------------")
        printDebug("Parents......: %d" % len(self.parents()))
        printDebug("Children.....: %d" % len(self.children()))
        printDebug("Ancestors....: %d" % len(self.ancestors()))
        printDebug("Descendants..: %d" % len(self.descendants()))
        printDebug("Domain of....: %d" % len(self.domain_of))
        printDebug("Range of.....: %d" % len(self.range_of))
        printDebug("Instances....: %d" % self.count())
        printDebug("----------------")

    def printGenericTree(self):
        printGenericTree(self)

    def describe(self):
        """ shotcut to pull out useful info for interactive use """
        self.printTriples()
        self.printStats()
        # self.printGenericTree()





class OntoProperty(RDF_Entity):
    """
    Python representation of a generic RDF/OWL property.

    rdftype is one of:
    rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#ObjectProperty')
    rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#DatatypeProperty')
    rdflib.term.URIRef(u'http://www.w3.org/2002/07/owl#AnnotationProperty')
    rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')

    """

    def __init__(self, uri, rdftype=None, namespaces=None):
        """
        ...
        """
        super(OntoProperty, self).__init__(uri, rdftype, namespaces)

        self.slug = "prop-" + slugify(self.qname)
        self.rdftype = inferMainPropertyType(rdftype)

        self.domains = []
        self.ranges = []
        self.ontology = None

    def __repr__(self):
        return "<Property *%s*>" % ( self.uri)


    def printGenericTree(self):
        printGenericTree(self)


    def printStats(self):
        """ shotcut to pull out useful info for interactive use """
        printDebug("----------------")
        printDebug("Parents......: %d" % len(self.parents()))
        printDebug("Children.....: %d" % len(self.children()))
        printDebug("Ancestors....: %d" % len(self.ancestors()))
        printDebug("Descendants..: %d" % len(self.descendants()))
        printDebug("Has Domain...: %d" % len(self.domains))
        printDebug("Has Range....: %d" % len(self.ranges))
        printDebug("----------------")


    def describe(self):
        """ shotcut to pull out useful info for interactive use """
        self.printTriples()
        self.printStats()
        # self.printGenericTree()






class OntoSKOSConcept(RDF_Entity):
    """
    Python representation of a generic SKOS concept within an ontology.
    @todo: complete methods..

    """

    def __init__(self, uri, rdftype=None, namespaces=None):
        """
        ...
        """
        super(OntoSKOSConcept, self).__init__(uri, rdftype, namespaces)
        self.slug = "concept-" + slugify(self.qname)
        self.instance_of = []
        self.ontology = None
        self.queryHelper = None	 # the original graph the class derives from

    def __repr__(self):
        return "<SKOS Concept *%s*>" % ( self.uri)



    def printStats(self):
        """ shotcut to pull out useful info for interactive use """
        printDebug("----------------")
        printDebug("Parents......: %d" % len(self.parents()))
        printDebug("Children.....: %d" % len(self.children()))
        printDebug("Ancestors....: %d" % len(self.ancestors()))
        printDebug("Descendants..: %d" % len(self.descendants()))
        printDebug("----------------")

    def printGenericTree(self):
        printGenericTree(self)

    def describe(self):
        """ shotcut to pull out useful info for interactive use """
        self.printTriples()
        self.printStats()
        self.printGenericTree()

















