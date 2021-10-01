from flask import Flask
import ssl
import requests


app = Flask(__name__)


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


@app.route("/")
def greeting():
    return "hello, I'm Microservice One"


if __name__ == '__main__':
    app.run(port=1338, debug=True, ssl_context=ssl_context)
