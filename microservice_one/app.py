from flask import Flask,request
from flask_restful import Resource,Api
import enum
import ssl
import random
import requests
from faker import Faker


app = Flask(__name__)
api=Api(app)

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


class Paciente(Resource):
    def get(self):
        fake = Faker()
        id = fake.random_int(1, 9999)
        nombre = fake.unique.name()
        fechaNacimiento = str(fake.date())
        direccion = fake.address()
        Epss = ["Sanitas", "Sura", "Coomeva", "Famisanar", "Compensar", "Cafam", "Cafesalud"]
        Eps = random.choice(list(Epss))

        return {"id": id, "identificacion": request.json['identificacion'], "nombre": nombre,
                "fechaNacimiento": fechaNacimiento, "direccion": direccion, "Eps": Eps}

api.add_resource(Paciente, '/paciente')


if __name__ == '__main__':
    app.run(port=1338, debug=True, ssl_context=ssl_context)
