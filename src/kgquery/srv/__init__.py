from flask import Flask, request
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

todos = {}

class Samples(Resource):
    def get(self):
        return {"error":"OK"}

    def post(self):
        return {"error":"none"}

api.add_resource(Samples, '/api/1.0/samples')

if __name__ == '__main__':
    app.run(debug=True)
