from SPARQLWrapper import SPARQLWrapper, POST, JSON, CSV, RDF, RDFXML, N3, JSONLD, XML
import requests as rq
import os
from pprint import pprint
from collections import namedtuple
import chevron
from rdflib import Graph

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
    {{#graph}}
    PREFIX g: <{{graph}}>
    {{/graph}}
    {{^graph}}
    PREFIX g: <{{src}}>
    {{/graph}}

"""

QUERY = (
    PREFIXES
    + """
    select distinct ?Name
    from <http://www.daml.org/2003/01/periodictable/PeriodicTable#>
    where {[] rdfs:label ?Name} LIMIT 100
    """
)

def conv(results):
    binds = results["results"]["bindings"]
    for e in binds:
        yield {k: v["value"] for k, v in e.items()}

def convrows(rows):
    for row in rows:
        print(row)
        yield row

def lineprint(s):
    import io
    with io.StringIO(s) as i:
        n = 1
        for l in i:
            print("{:3}: {}".format(n,l), end="")
            n += 1

class Query:

    _prefixes_ = PREFIXES
    _endpoint_ = ENDPOINT

    def __init__(self, query, graphIRI, context):
        self.query = query
        self.graphIRI = graphIRI
        self.context = context
        if "endpoint" not in context:
            context["endpoint"] = self._endpoint_
        self.endpoint = context["endpoint"]
        self.header = []

    def results(self, debug=False):
        # import pudb

        debug = debug or self.context.get("debug", False)

        q = self._prefixes_ + "\n\n" + self.query
        if debug:
            # print(q)
            print("Params are:", self.graphIRI)
        context = {}
        context.update(self.context)
        src = context.get("src", None)
        if not src:
            context["graph"]=self.graphIRI
        if debug:
            print("Context:\n")
            pprint(context)
        if isinstance(src, Graph):
            context["~~graph"] = src
            context["src"] = "local-file"
        q = chevron.render(q, context)
        if debug:
            print("SPARQL:")
            lineprint(q)
            print()
        if src:
            if isinstance(src, str):
                G=Graph()
                G.parse(src)
            else:
                G = src
                # pudb
            rc = G.query(q)
            print("+++++")
            for r in rc:
                print(":", r)
            quit()
            return rc
            return convrows(rc)
        else:
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
        print([g for g in gen])
        for a in gen:
            yield np(**a)


def quicktest(query, context):
    graph = context.get("graph", None)
    q = Query(query, graph, context)
    q.print()
