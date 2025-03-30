#!/bin/env python
from .common import NTQuery, SAMPLEGRAPH, quicktest
from rdflib import URIRef
from ..namespace import PT, P, MT
from collections import namedtuple
import pprint
import csv
import sys

query_sample_data = """
    # SELECT *
    SELECT ?uri, ?site_name, ?sample_name,

           {{#location}}
           ?long, ?lat,
           {{/location}}

           {{#element}}
           mt:{{element}} as
           {{/element}}
           ?element,
           ?value, ?unitid, ?unit, ?detlim

    FROM <{{& graph}}>

    WHERE {
       ?main_site rdfs:label ?m_site_name .
       ?main_site a pt:Site  .

       {{#site}}
       FILTER (?m_site_name = "{{site}}"@ru)
       {{/site}}

       ?main_site ^pt:location* ?site .
       ?site rdfs:label ?site_name .
       ?site a pt:Site  .
       ?uri pt:location ?site .
       ?uri a pt:Sample .
       ?uri rdfs:label ?sample_name .

       {{#location}}
       ?uri wgs:location ?loc .
       ?loc a wgs:Point .
       ?loc wgs:lat ?lat .
       ?loc wgs:long ?long .
       {{/location}}

       ?uri pt:measurement ?m .
       ?m a pt:Measurement .
       {{#element}}
       ?m mt:element mt:{{element}} .
       {{/element}}
       {{^element}}
       ?m mt:element ?element .
       {{/element}}
       { ?m pt:value ?value .
         ?m pt:unit ?unitid .
         BIND(0 AS ?detlim) .
       } UNION {
         ?m pt:value ?dl .
         ?dl a pt:DetectionLimit .
         ?dl pt:unit ?unitid .
         ?dl pt:value ?value .
         BIND(1 AS ?detlim) .
       } .
       OPTIONAL {
          ?unitid rdfs:label ?unit .
       }
    }
    """

query_sample_data_with_coords = """
    select ?slab ?el ?val ?unit ?lat ?long
    FROM <{graph}>
    where {
      ?s a pt:Sample .
      { ?s pt:location pi:Харанцы . } union { ?s pt:location pi:Хужир . }
      ?s wgs:location ?loc .
      ?s rdfs:label ?slab .
      ?loc  a wgs:Point .
      ?loc wgs:lat ?lat .
      ?loc wgs:long ?long .
      ?s pt:measurement ?m .
      ?m a pt:Measurement .
      ?m pt:unit ?unit .
      # ?unit rdfs:label ?unitlab .
      ?m pt:value ?val .
      ?m mt:element ?el .
    }
"""


def pollution_data(query, context):
    context["debug"] = True
    qs = NTQuery(query, SAMPLEGRAPH, context=context)
    # qs.print()
    return qs.results()


# quicktest("""
#     SELECT *
#     FROM <{graph}>
#     WHERE {
#         <http://crust.irk.ru/ontology/pollution/1.0/AGS-0110> a pt:Sample .
#         <http://crust.irk.ru/ontology/pollution/1.0/AGS-0110> pt:measurement ?m .
#         ?m mt:element <http://www.daml.org/2003/01/periodictable/PeriodicTable#Ga> .
#         # ?m mt:element ?el .
#         ?m pt:value ?value .
#     }
# """, SAMPLEGRAPH)

# quicktest(query_sample_data, SAMPLEGRAPH, site="Бураевская площадь",
#          element = MT.Ga.n3(), debug=True)


def adjustcontext(site, context):
    if context is None:
        if site is None:
            raise ValueError("both site and context are None")
        context = {"site": site}

    if "site" not in context:
        raise ValueError("site(s) must be supplied")

    site = context["site"]
    if not isinstance(site, (list, tuple)):
        sites = [site]
    context["sites"] = sites
    return context

def u(s):
    if s.startswith("http"):
        return URIRef(s)
    return s


def g(headers, row, default=0.0):
    for h in headers:
        if h in row:
            yield row[h]
        else:
            yield default


def fr(row):
    for e in row:
        # print(e, type(e))
        if isinstance(e, URIRef):
            yield e.fragment
        else:
            yield e

def simplify(val):
    if isinstance(val, URIRef):
        fragment = val.fragment
        if fragment:
            return simplify(fragment)
        _split = val.rsplit("/", 1)
        _ns, fragment = _split
        return simplify(fragment)
    if val.startswith("http"):
        return simplify(URIRef(val))
    try:
        return int(val)
    except ValueError:
        pass
    try:
        return float(val)
    except ValueError:
        pass
    return val

def simple(context):
    context = adjustcontext(None, context)
    sim = context.get("simplify", False)
    fields = None
    _id=0
    for row in pollution_data(query_sample_data, context):
        if fields is None:
            fields = row._fields
        if sim:
            row=[simplify(v) for v in row]
        row = {fields[i]:row[i] for i in range(len(fields))}
        row["id"]=_id
        _id+=1
        yield row

def samples(site=None, context=None):
    context = adjustcontext(site, context)
    tbl = {}
    headers = set(['sample', 'site'])

    #    for row in pollution_data(query_sample_data,
    #                              "Бураевская площадь", None):

    for row in pollution_data(query_sample_data, context):
        sample = u(row.uri)
        element = u(row.element)
        headers.add(element)
        s = tbl.setdefault(sample, {
            "sample": row.sample_name,
            "site": row.site_name
        })
        try:
            s[element] = float(row.value)
        except ValueError:
            s[element] = 0.0
        # Row(uri='http://crust.irk.ru/ontology/pollution/1.0/2464-1', site_name='Ивановский', sample_name='2464-1', element='http://www.daml.org/2003/01/periodictable/PeriodicTable#V', value='4.2999999999999998224', unitid='http://crust.irk.ru/ontology/pollution/terms/1.0/PPM', unit='мг/кг')

    h = fr(headers)
    # wr.writerow(headers)
    yield h
    for sample, row in tbl.items():
        yield g(headers, row)


if __name__ == "__main__":
    gen = samples(sys.argv[1])
    with open(sys.argv[2], "w") as o:
        wr = csv.writer(o, quotechar='"', quoting=csv.QUOTE_STRINGS)
        for row in gen:
            wr.writerow(row)
