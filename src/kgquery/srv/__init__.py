from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from ..ext import samples, simple

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("context")


class Samples(Resource):

    def get(self):
        return {"error": "OK"}

    def post(self):
        context = request.get_json()
        print(context)
        if context.get("format", None) is None:
            rc = samples(context=context)
            ser = [[i for i in row] for row in rc]
            return ser
        frm = context["format"]
        if frm=="simple":
            rc = simple(context=context)
            return list(rc)


api.add_resource(Samples, '/api/1.0/samples')
