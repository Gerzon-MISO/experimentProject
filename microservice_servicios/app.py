from flask_restful import Resource, Api
from flask import Flask, request
import requests
import json
from faker import Faker
from random import randrange
import random
import ssl
import http.client

app = Flask(__name__)
api = Api(app)
fake = Faker()


def write_file(name_file, content_file):
    text_file = open("./certificates/%s" % name_file, "w")
    text_file.write(content_file)
    text_file.close()


def get_certificate():
    response = requests.get('http://127.0.0.1:1340/certification')
    certificate = response.json()
    write_file('ca.crt', certificate['crt'])
    write_file('ca.key', certificate['key'])
    write_file('ca.pem', certificate['pem'])


# set ssl_context
get_certificate()
ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile='./certificates/ca.crt')
ssl_context.load_cert_chain(certfile='./certificates/ca.crt', keyfile='./certificates/ca.key', password=None)
ssl_context.verify_mode = ssl.CERT_REQUIRED


class Services(Resource):

    def get(self):
        payload = {"identificacion": request.json['identificacion']}
        json_data = json.dumps(payload)
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.load_cert_chain(certfile='./certificates/ca.pem')
        connection = http.client.HTTPSConnection('127.0.0.1', port=1338, context=context)
        connection.request(method="GET", url='/paciente', body=json_data, headers={'Content-type': 'application/json'})
        response = connection.getresponse()
        paciente = response.read()
        my_json = paciente.decode('utf8').replace("'", '"')
        data = json.loads(my_json)

        servicios = ["cirugia", "examenes", "imagenes", "inyectologia", "medicina interna", "neurologia","traumatologia","hematologia","infectologia"]
        lista_servicios = []

        for ser in range(1, randrange(1, 10)):
            servicio_paciente = {"idServ": ser, "servicio": random.choice(list(servicios))}
            lista_servicios.append(servicio_paciente)
        
        return {"paciente": data["identificacion"],  "servicios": lista_servicios}


api.add_resource(Services, '/servicios')

if __name__ == '__main__':
    app.run(port=1337, debug=True, ssl_context=ssl_context)
