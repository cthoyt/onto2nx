# !/usr/bin/env python
#  -*- coding: UTF-8 -*-


"""
ONTOSPY
Copyright (c) 2013-2016 __Michele Pasin__ <http://www.michelepasin.org>. All rights reserved.

Run it from the command line:

>>> python ontospy.py -h

More info in the README file.

"""

from __future__ import print_function

import sys, os, time, optparse

try:
    import urllib2
except ImportError:
    import urllib.request as urllib2

import rdflib
from rdflib.plugins.stores.sparqlstore import SPARQLStore


from .utils import *
from .loader import RDFLoader
from .entities import *
from .queryHelper import QueryHelper


class Ontospy(object):  # Graph
    """
    Object that scan an rdf graph for schema definitions (aka 'ontologies')

    In [1]: import ontospy

    In [2]: g = ontospy.Ontospy("foaf.ttl")
    Loaded 3478 triples
    Ontologies found: 1
    [etc...]

    """

    def __init__(self, uri_or_path=None, text=None, file_obj=None, rdf_format="", verbose=True, hide_base_schemas=True):
        """
        Load the graph in memory, then setup all necessary attributes.
        """
        super(Ontospy, self).__init__()

        self.rdfgraph = None
        self.sources = None
        self.queryHelper = None
        self.ontologies = []
        self.classes = []
        self.namespaces = []
        self.properties = []
        self.annotationProperties = []
        self.objectProperties = []
        self.datatypeProperties = []
        self.skosConcepts = []
        self.toplayer = []
        self.toplayerProperties = []
        self.toplayerSkosConcepts = []
        self.OWLTHING = OntoClass(rdflib.OWL.Thing, rdflib.OWL.Class, self.namespaces)

        # finally:
        if uri_or_path or text or file_obj:
            self.load(uri_or_path, text, file_obj, rdf_format, verbose, hide_base_schemas)


    def load(self, uri_or_path=None, text=None, file_obj=None, rdf_format="", verbose=False, hide_base_schemas=True):
        loader = RDFLoader()
        loader.load(uri_or_path, text, file_obj, rdf_format, verbose)
        self.rdfgraph = loader.rdfgraph
        self.sources = loader.sources_valid
        self.queryHelper = QueryHelper(self.rdfgraph)
        self.namespaces = sorted(self.rdfgraph.namespaces())
        # extract entities
        self._scan(verbose=verbose, hide_base_schemas=hide_base_schemas)

    def serialize(self, format="turtle"):
        """ Shortcut that outputs the graph
        Valid options are: xml, n3, turtle, nt, pretty-xml [trix not working out of the box]
        """
        return self.rdfgraph.serialize(format=format)


    def sparql(self, stringa):
        """ wrapper around a sparql query """
        qres = self.rdfgraph.query(stringa)
        return list(qres)


    def __repr__(self):
        if self.rdfgraph:
            return "<Ontospy Graph (%d triples)>" % (len(self.rdfgraph))
        else:
            return "<Ontospy object created but not initialized (use the `load` method to load an rdf schema)>"



    # ------------
    # === main method === #
    # ------------

    def _scan(self, verbose=False, hide_base_schemas=True):
        """
        scan a source of RDF triples
        build all the objects to deal with the ontology/ies pythonically

        """
        if verbose:
            printDebug("Scanning entities...", "green")
            printDebug("----------", "comment")

        self.__extractOntologies()
        if verbose: printDebug("Ontologies.........: %d" % len(self.ontologies), "comment")

        self.__extractClasses(hide_base_schemas)
        if verbose: printDebug("Classes............: %d" % len(self.classes), "comment")

        self.__extractProperties()
        if verbose: printDebug("Properties.........: %d" % len(self.properties), "comment")
        if verbose: printDebug("..annotation.......: %d" % len(self.annotationProperties), "comment")
        if verbose: printDebug("..datatype.........: %d" % len(self.datatypeProperties), "comment")
        if verbose: printDebug("..object...........: %d" % len(self.objectProperties), "comment")

        self.__extractSkosConcepts()
        if verbose: printDebug("Concepts (SKOS)....: %d" % len(self.skosConcepts), "comment")

        self.__computeTopLayer()

        self.__computeInferredProperties()

        if verbose: printDebug("----------", "comment")


    def stats(self):
        """ shotcut to pull out useful info for a graph 

        2016-08-18 the try/except is a dirty solution to a problem
        emerging with counting graph lenght on cached Graph objects..
        TODO: investigate what's going on..
        """
        out = []
        try:
            out += [("Triples", len(self.rdfgraph))]
        except:
            pass
        out += [("Classes", len(self.classes))]
        out += [("Properties", len(self.properties))]
        out += [("Annotation Properties", len(self.annotationProperties))]
        out += [("Object Properties", len(self.objectProperties))]
        out += [("Datatype Properties", len(self.datatypeProperties))]
        out += [("Skos Concepts", len(self.skosConcepts))]
        # out += [("Individuals", len(self.instances))]
        return out

        

    def __extractOntologies(self, exclude_BNodes = False, return_string=False):
        """
        returns Ontology class instances

        [ a owl:Ontology ;
            vann:preferredNamespacePrefix "bsym" ;
            vann:preferredNamespaceUri "http://bsym.bloomberg.com/sym/" ],
        """
        out = []

        qres = self.queryHelper.getOntology()

        if qres:
            # NOTE: SPARQL returns a list of rdflib.query.ResultRow (~ tuples..)

            for candidate in qres:
                if isBlankNode(candidate[0]):
                    if exclude_BNodes:
                        continue
                    else:
                        checkDC_ID = [x for x in self.rdfgraph.objects(candidate[0], rdflib.namespace.DC.identifier)]
                        if checkDC_ID:
                            out += [Ontology(checkDC_ID[0], namespaces=self.namespaces),]
                        else:
                            vannprop = rdflib.URIRef("http://purl.org/vocab/vann/preferredNamespaceUri")
                            vannpref = rdflib.URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix")
                            checkDC_ID = [x for x in self.rdfgraph.objects(candidate[0], vannprop)]
                            if checkDC_ID:
                                checkDC_prefix = [x for x in self.rdfgraph.objects(candidate[0], vannpref)]
                                if checkDC_prefix:
                                    out += [Ontology(checkDC_ID[0],
                                                     namespaces=self.namespaces,
                                                     prefPrefix=checkDC_prefix[0])]
                                else:
                                    out += [Ontology(checkDC_ID[0], namespaces=self.namespaces)]

                else:
                    out += [Ontology(candidate[0], namespaces=self.namespaces)]


        else:
            pass
            # printDebug("No owl:Ontologies found")

        #finally... add all annotations/triples
        self.ontologies = out
        for onto in self.ontologies:
            onto.triples = self.queryHelper.entityTriples(onto.uri)
            onto._buildGraph() # force construction of mini graph



    ##################
    #
    #  METHODS for MANIPULATING RDFS/OWL CLASSES
    #
    #  RDFS:class vs OWL:class cf. http://www.w3.org/TR/owl-ref/ section 3.1
    #
    ##################


    def __extractClasses(self, hide_base_schemas=True):
        """
        2015-06-04: removed sparql 1.1 queries
        2015-05-25: optimized via sparql queries in order to remove BNodes
        2015-05-09: new attempt

        Note: queryHelper.getAllClasses() returns a list of tuples,
        (class, classRDFtype)
        so in some cases there are duplicates if a class is both RDFS.CLass and OWL.Class
        In this case we keep only OWL.Class as it is more informative.
        """


        self.classes = [] # @todo: keep adding?

        qres = self.queryHelper.getAllClasses(hide_base_schemas=hide_base_schemas)

        for class_tuple in qres:
            
            _uri = class_tuple[0]
            try:
                _type = class_tuple[1]
            except:
                _type= ""

            test_existing_cl = self.getClass(uri=_uri)
            if not test_existing_cl:
                # create it
                self.classes += [OntoClass(_uri, _type, self.namespaces)]
            else:
                # if OWL.Class over RDFS.Class - update it
                if _type == rdflib.OWL.Class:
                    test_existing_cl.rdftype = rdflib.OWL.Class



        #add more data
        for aClass in self.classes:

            aClass.triples = self.queryHelper.entityTriples(aClass.uri)
            aClass._buildGraph() # force construction of mini graph

            aClass.queryHelper = self.queryHelper

            # attach to an ontology
            for uri in aClass.getValuesForProperty(rdflib.RDFS.isDefinedBy):
                onto = self.getOntology(str(uri))
                if onto:
                    onto.classes += [aClass]
                    aClass.ontology = onto

            # add direct Supers
            directSupers = self.queryHelper.getClassDirectSupers(aClass.uri)

            for x in directSupers:
                superclass = self.getClass(uri=x[0])
                if superclass:
                    aClass._parents.append(superclass)

                    # add inverse relationships (= direct subs for superclass)
                    if aClass not in superclass.children():
                         superclass._children.append(aClass)



    def __extractProperties(self):
        """
        2015-06-04: removed sparql 1.1 queries
        2015-06-03: analogous to get classes

        # instantiate properties making sure duplicates are pruned
        # but the most specific rdftype is kept
        # eg OWL:ObjectProperty over RDF:property

        """
        self.properties = [] # @todo: keep adding?
        self.annotationProperties = []
        self.objectProperties = []
        self.datatypeProperties = []

        qres = self.queryHelper.getAllProperties()

        for candidate in qres:

            test_existing_prop = self.getProperty(uri=candidate[0])
            if not test_existing_prop:
                # create it
                self.properties += [OntoProperty(candidate[0], candidate[1], self.namespaces)]
            else:
                # update it
                if candidate[1] and (test_existing_prop.rdftype == rdflib.RDF.Property):
                    test_existing_prop.rdftype = inferMainPropertyType(candidate[1])


        #add more data
        for aProp in self.properties:

            if aProp.rdftype == rdflib.OWL.DatatypeProperty:
                self.datatypeProperties += [aProp]
            elif aProp.rdftype == rdflib.OWL.AnnotationProperty:
                self.annotationProperties += [aProp]
            elif aProp.rdftype == rdflib.OWL.ObjectProperty:
                self.objectProperties += [aProp]
            else:
                pass

            aProp.triples = self.queryHelper.entityTriples(aProp.uri)
            aProp._buildGraph() # force construction of mini graph

            # attach to an ontology [2015-06-15: no property type distinction yet]
            for uri in aProp.getValuesForProperty(rdflib.RDFS.isDefinedBy):
                onto = self.getOntology(str(uri))
                if onto:
                    onto.properties += [aProp]
                    aProp.ontology = onto



            self.__buildDomainRanges(aProp)

            # add direct Supers
            directSupers = self.queryHelper.getPropDirectSupers(aProp.uri)

            for x in directSupers:
                superprop = self.getProperty(uri=x[0])
                if superprop:
                    aProp._parents.append(superprop)

                    # add inverse relationships (= direct subs for superprop)
                    if aProp not in superprop.children():
                         superprop._children.append(aProp)



    def __buildDomainRanges(self, aProp):
        """
        extract domain/range details and add to Python objects
        """
        domains = aProp.rdfgraph.objects(None, rdflib.RDFS.domain)
        ranges =  aProp.rdfgraph.objects(None, rdflib.RDFS.range)

        for x in domains:
            if not isBlankNode(x):
                aClass = self.getClass(uri=str(x))
                if aClass:
                    aProp.domains += [aClass]
                    aClass.domain_of += [aProp]
                else:
                    aProp.domains += [x]  # edge case: it's not an OntoClass instance?

        for x in ranges:
            if not isBlankNode(x):
                aClass = self.getClass(uri=str(x))
                if aClass:
                    aProp.ranges += [aClass]
                    aClass.range_of += [aProp]
                else:
                    aProp.ranges += [x]





    def __extractSkosConcepts(self):
        """
        2015-08-19: first draft
        """
        self.skosConcepts = [] # @todo: keep adding?

        qres = self.queryHelper.getSKOSInstances()

        for candidate in qres:

            test_existing_cl = self.getSkosConcept(uri=candidate[0])
            if not test_existing_cl:
                # create it
                self.skosConcepts += [OntoSKOSConcept(candidate[0], None, self.namespaces)]
            else:
                pass

        #add more data
        skos = rdflib.Namespace('http://www.w3.org/2004/02/skos/core#')

        for aConcept in self.skosConcepts:

            aConcept.rdftype = skos['Concept']
            aConcept.triples = self.queryHelper.entityTriples(aConcept.uri)
            aConcept._buildGraph() # force construction of mini graph

            aConcept.queryHelper = self.queryHelper

            # attach to an ontology
            for uri in aConcept.getValuesForProperty(rdflib.RDFS.isDefinedBy):
                onto = self.getOntology(str(uri))
                if onto:
                    onto.skosConcepts += [aConcept]
                    aConcept.ontology = onto

            # add direct Supers
            directSupers = self.queryHelper.getSKOSDirectSupers(aConcept.uri)

            for x in directSupers:
                superclass = self.getSkosConcept(uri=x[0])
                if superclass:
                    aConcept._parents.append(superclass)

                    # add inverse relationships (= direct subs for superclass)
                    if aConcept not in superclass.children():
                         superclass._children.append(aConcept)


    def __computeTopLayer(self):

        exit = []
        for c in self.classes:
            if not c.parents():
                exit += [c]
        self.toplayer = exit  # sorted(exit, key=lambda x: x.id) # doesnt work

        # properties
        exit = []
        for c in self.properties:
            if not c.parents():
                exit += [c]
        self.toplayerProperties = exit  # sorted(exit, key=lambda x: x.id) # doesnt work

        # skos
        exit = []
        for c in self.skosConcepts:
            if not c.parents():
                exit += [c]
        self.toplayerSkosConcepts = exit  # sorted(exit, key=lambda x: x.id) # doesnt work


    def __computeInferredProperties(self):
        """

        :return: attach a list of dicts to each class, detailing valid props up the subsumption tree
        """
        exit = []
        for c in self.classes:
            c.domain_of_inferred = self.getInferredPropertiesForClass(c, "domain_of")
            c.range_of_inferred = self.getInferredPropertiesForClass(c, "range_of")


    def getInferredPropertiesForClass(self, aClass, rel="domain_of"):
        """
        returns all properties valid for a class (as they have it in their domain)
        recursively ie traveling up the descendants tree
        Note: results in a list of dicts including itself
        Note [2]: all properties with no domain info are added at the top as [None, props]

        :return:
        [{<Class *http://xmlns.com/foaf/0.1/Person*>:
            [<Property *http://xmlns.com/foaf/0.1/currentProject*>,<Property *http://xmlns.com/foaf/0.1/familyName*>,
                etc....]},
        {<Class *http://www.w3.org/2003/01/geo/wgs84_pos#SpatialThing*>:
            [<Property *http://xmlns.com/foaf/0.1/based_near*>, etc...]},
            ]
        """
        _list = []

        if rel=="domain_of":
            _list.append({aClass: aClass.domain_of})
            for x in aClass.ancestors():
                if x.domain_of:
                    _list.append({x: x.domain_of})

            # add properties from Owl:Thing ie the inference layer

            topLevelProps = [p for p in self.properties if p.domains == []]
            if topLevelProps:
                _list.append({self.OWLTHING: topLevelProps})

        elif rel=="range_of":
            _list.append({aClass: aClass.range_of})
            for x in aClass.ancestors():
                if x.domain_of:
                    _list.append({x: x.range_of})

            # add properties from Owl:Thing ie the inference layer

            topLevelProps = [p for p in self.properties if p.ranges == []]
            if topLevelProps:
                _list.append({self.OWLTHING: topLevelProps})

        return _list




    # METHODS TO RETRIEVE OBJECTS



    def getClass(self, id=None, uri=None, match=None):
        """
        get the saved-class with given ID or via other methods...

        Note: it tries to guess what is being passed..

        In [1]: g.getClass(uri='http://www.w3.org/2000/01/rdf-schema#Resource')
        Out[1]: <Class *http://www.w3.org/2000/01/rdf-schema#Resource*>

        In [2]: g.getClass(10)
        Out[2]: <Class *http://purl.org/ontology/bibo/AcademicArticle*>

        In [3]: g.getClass(match="person")
        Out[3]:
        [<Class *http://purl.org/ontology/bibo/PersonalCommunicationDocument*>,
         <Class *http://purl.org/ontology/bibo/PersonalCommunication*>,
         <Class *http://xmlns.com/foaf/0.1/Person*>]

        """

        if not id and not uri and not match:
            return None

        if type(id) == type("string"):
            uri = id
            id = None
            if not uri.startswith("http://"):
                match = uri
                uri = None
        if match:
            if type(match) != type("string"):
                return []
            res = []
            if ":" in match: # qname
                for x in self.classes:
                    if match.lower() in x.qname.lower():
                        res += [x]
            else:
                for x in self.classes:
                    if match.lower() in x.uri.lower():
                        res += [x]
            return res
        else:
            for x in self.classes:
                if id and x.id == id:
                    return x
                if uri and x.uri.lower() == uri.lower():
                    return x
            return None


    def getProperty(self, id=None, uri=None, match=None):
        """
        get the saved-class with given ID or via other methods...

        Note: analogous to getClass method
        """

        if not id and not uri and not match:
            return None

        if type(id) == type("string"):
            uri = id
            id = None
            if not uri.startswith("http://"):
                match = uri
                uri = None
        if match:
            if type(match) != type("string"):
                return []
            res = []
            if ":" in match: # qname
                for x in self.properties:
                    if match.lower() in x.qname.lower():
                        res += [x]
            else:
                for x in self.properties:
                    if match.lower() in x.uri.lower():
                        res += [x]
            return res
        else:
            for x in self.properties:
                if id and x.id == id:
                    return x
                if uri and x.uri.lower() == uri.lower():
                    return x
            return None


    def getSkosConcept(self, id=None, uri=None, match=None):
        """
        get the saved skos concept with given ID or via other methods...

        Note: it tries to guess what is being passed as above
        """

        if not id and not uri and not match:
            return None

        if type(id) == type("string"):
            uri = id
            id = None
            if not uri.startswith("http://"):
                match = uri
                uri = None
        if match:
            if type(match) != type("string"):
                return []
            res = []
            if ":" in match: # qname
                for x in self.skosConcepts:
                    if match.lower() in x.qname.lower():
                        res += [x]
            else:
                for x in self.skosConcepts:
                    if match.lower() in x.uri.lower():
                        res += [x]
            return res
        else:
            for x in self.skosConcepts:
                if id and x.id == id:
                    return x
                if uri and x.uri.lower() == uri.lower():
                    return x
            return None


    def getEntity(self, id=None, uri=None, match=None):
        """
        get a generic entity with given ID or via other methods...
        """

        if not id and not uri and not match:
            return None

        if type(id) == type("string"):
            uri = id
            id = None
            if not uri.startswith("http://"):
                match = uri
                uri = None
        if match:
            if type(match) != type("string"):
                return []
            res = []
            if ":" in match: # qname
                for x in self.classes:
                    if match.lower() in x.qname.lower():
                        res += [x]
                for x in self.properties:
                    if match.lower() in x.qname.lower():
                        res += [x]
            else:
                for x in self.classes:
                    if match.lower() in x.uri.lower():
                        res += [x]
                for x in self.properties:
                    if match.lower() in x.uri.lower():
                        res += [x]
            return res
        else:
            for x in self.classes:
                if id and x.id == id:
                    return x
                if uri and x.uri.lower() == uri.lower():
                    return x
            for x in self.properties:
                if id and x.id == id:
                    return x
                if uri and x.uri.lower() == uri.lower():
                    return x
            return None



    def getOntology(self, id=None, uri=None, match=None):
        """
        get the saved-ontology with given ID or via other methods...
        """

        if not id and not uri and not match:
            return None

        if type(id) == type("string"):
            uri = id
            id = None
            if not uri.startswith("http://"):
                match = uri
                uri = None
        if match:
            if type(match) != type("string"):
                return []
            res = []
            for x in self.ontologies:
                if match.lower() in x.uri.lower():
                    res += [x]
            return res
        else:
            for x in self.ontologies:
                if id and x.id == id:
                    return x
                if uri and x.uri.lower() == uri.lower():
                    return x
            return None


    def nextClass(self, classuri):
        """Returns the next class in the list of classes. If it's the last one, returns the first one."""
        if classuri == self.classes[-1].uri:
            return self.classes[0]
        flag = False
        for x in self.classes:
            if flag == True:
                return x
            if x.uri == classuri:
                flag = True
        return None


    def nextProperty(self, propuri):
        """Returns the next property in the list of properties. If it's the last one, returns the first one."""
        if propuri == self.properties[-1].uri:
            return self.properties[0]
        flag = False
        for x in self.properties:
            if flag == True:
                return x
            if x.uri == propuri:
                flag = True
        return None

    def nextConcept(self, concepturi):
        """Returns the next skos concept in the list of concepts. If it's the last one, returns the first one."""
        if concepturi == self.skosConcepts[-1].uri:
            return self.skosConcepts[0]
        flag = False
        for x in self.skosConcepts:
            if flag == True:
                return x
            if x.uri == concepturi:
                flag = True
        return None


    def printClassTree(self, element = None, showids=False, labels=False, showtype=False):
        """
        Print nicely into stdout the class tree of an ontology

        Note: indentation is made so that ids up to 3 digits fit in, plus a space.
        [123]1--
        [1]123--
        [12]12--
        """
        TYPE_MARGIN = 11 # length for owl:class etc..

        if not element:	 # first time
            for x in self.toplayer:
                printGenericTree(x, 0, showids, labels, showtype, TYPE_MARGIN)

        else:
            printGenericTree(element, 0, showids, labels, showtype, TYPE_MARGIN)


    def printPropertyTree(self, element = None, showids=False, labels=False, showtype=False):
        """
        Print nicely into stdout the property tree of an ontology

        Note: indentation is made so that ids up to 3 digits fit in, plus a space.
        [123]1--
        [1]123--
        [12]12--
        """
        TYPE_MARGIN = 18 # length for owl:AnnotationProperty etc..

        if not element:	 # first time
            for x in self.toplayerProperties:
                printGenericTree(x, 0, showids, labels, showtype, TYPE_MARGIN)

        else:
            printGenericTree(element, 0, showids, labels, showtype, TYPE_MARGIN)


    def printSkosTree(self, element = None, showids=False, labels=False, showtype=False):
        """
        Print nicely into stdout the SKOS tree of an ontology

        Note: indentation is made so that ids up to 3 digits fit in, plus a space.
        [123]1--
        [1]123--
        [12]12--
        """
        TYPE_MARGIN = 13 # length for skos:concept

        if not element:	 # first time
            for x in self.toplayerSkosConcepts:
                printGenericTree(x, 0, showids, labels, showtype, TYPE_MARGIN)

        else:
            printGenericTree(element, 0, showids, labels, showtype, TYPE_MARGIN)




class SparqlEndpoint(Ontospy):
    """
    A remote graph accessible via a sparql endpoint
    """

    def __init__(self, source):
        """
        Init ontology object. Load the graph in memory, then setup all necessary attributes.
        """
        super(SparqlEndpoint, self).__init__(source, text=False, endpoint=True, rdf_format=None)





