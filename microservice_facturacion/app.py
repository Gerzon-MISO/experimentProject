#from  microservice_facturacion import create_app
from flask_restful import Resource, Api
from flask import Flask, request
import requests
import json
from faker import Faker
from random import randrange
import random
import ssl, http.client
import sys
import json
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

app = Flask(__name__)
api=Api(app)
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


class Facturacion(Resource):
    def get(self):

        payload = {'identificacion': request.json['identificacion']}
        json_data = json.dumps(payload)
        headers = {'Content-type': 'application/json'}
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.load_cert_chain(certfile='./certificates/ca.pem')
        connection = http.client.HTTPSConnection('127.0.0.1', port=1338, context=context)
        connection.request('GET', '/paciente', json_data, headers)
        try:
            respuesta = connection.getresponse()
        except Exception:
            return 'Certificado no valido'
        content = respuesta.read()
        print(content)

        #content = requests.get('http://127.0.0.1:1338/paciente', json=payload)

        servicios=["cirugia", "examenes", "imagenes", "inyectologia", "medicina interna", "neurologia","traumatologia","hematologia","infectologia"]

        paciente = json.loads(content.decode())
        idFactura = fake.uuid4()
        nombrePaciente = paciente['nombre']
        direccion = paciente['direccion']
        total = fake.pricetag()

        servicioPaciente={}
        listaServicio=[]
        for ser in range(1,randrange(1,10)):
            servicioPaciente = {"idServ" : ser, "servicio":random.choice(list(servicios)), "valor": fake.pricetag()}        
            listaServicio.append(servicioPaciente)
        
        return {"id" : idFactura, "identificacion":request.json['identificacion'], "nombrePaciente": nombrePaciente, "direccion": direccion, "total": total, "servicios":listaServicio}

api.add_resource(Facturacion, '/facturacion')

if __name__ == '__main__':
    try: 
        app.run(port=6000, debug=True, ssl_context=ssl_context)

    except Exception:
        print ("Certificado no valido")
