from SPARQLWrapper import SPARQLWrapper, POST, JSON, CSV, RDF, RDFXML, N3, JSONLD, XML
import requests as rq
import os
from pprint import pprint
from collections import namedtuple
import chevron

try:
    del os.environ["HTTP_PROXY"]
    del os.environ["HTTPS_PROXY"]
except KeyError:
    pass
try:
    del os.environ["http_proxy"]
    del os.environ["https_proxy"]
except KeyError:
    pass

ENDPOINT = "http://ktulhu.isclan.ru:8890/sparql"
SAMPLEGRAPH = "http://localhost:8890/DAV/home/loader/rdf_sink/samples.ttl"

PREFIXES = """
    PREFIX pt: <http://crust.irk.ru/ontology/pollution/terms/1.0/>
    PREFIX p: <http://crust.irk.ru/ontology/pollution/1.0/>
    PREFIX mt: <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
    PREFIX wgs: <https://www.w3.org/2003/01/geo/wgs84_pos#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX g: <{{graph}}>

"""

QUERY = (
    PREFIXES
    + """
    select distinct ?Name
    from <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
    where {[] rdfs:label ?Name} LIMIT 100
    """
)

sparql = SPARQLWrapper(ENDPOINT)
# sparql.setCredentials("some-login", "some-password") # if required
sparql.setMethod(POST)  # this is the crucial option
sparql.setReturnFormat(JSON)
# sparql.setReturnFormat(XML)

# sparql.setQuery(QUERY)

# results = sparql.query()
# print(results.response.read().decode('utf-8'))
# results.print_results()


def conv(results):
    binds = results["results"]["bindings"]
    for e in binds:
        yield {k: v["value"] for k, v in e.items()}


class Query:

    _prefixes_ = PREFIXES
    _endpoint_ = ENDPOINT

    def __init__(self, query, graphIRI, context, endpoint=None):
        self.query = query
        self.graphIRI = graphIRI
        self.context = context
        if endpoint is None:
            endpoint = self._endpoint_
        self.endpoint = endpoint
        self.header = []

    def results(self, debug=None):
        # import pudb; pu.db

        if debug is None:
            debug = False
        debug = debug or self.context.get("debug", False)

        q = self._prefixes_ + "\n\n" + self.query
        if debug:
            # print(q)
            print("Params are:", self.graphIRI)
        context = {}
        context.update(self.context)
        context["graph"]=self.graphIRI
        if debug:
            print("Context:\n")
            pprint(context)
        q = chevron.render(q, context)
        if debug:
            print("SPARQL:\n",q)
        sparql = SPARQLWrapper(self.endpoint)
        sparql.setQuery(q)
        sparql.setMethod(POST)
        sparql.setReturnFormat(JSON)
        results = sparql.query()
        rc = results.convert()
        self.header = rc["head"]["vars"]
        return conv(rc)

    def print(self):
        pprint(list(self.results()))


class NTQuery(Query):
    def results(self, debug=False):
        gen = super().results(debug=debug)
        np = namedtuple('Row', self.header)
        for a in gen:
            yield np(**a)


def quicktest(query, graph, **args):
    q = Query(query, graph, **args)
    q.print()
