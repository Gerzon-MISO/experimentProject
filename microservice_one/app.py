from flask import Flask
import ssl


app = Flask(__name__)
ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH, cafile='./ca.crt')
ssl_context.load_cert_chain(certfile='./ca.crt', keyfile='./ca.key', password=None)
ssl_context.verify_mode = ssl.CERT_REQUIRED


@app.route("/")
def greeting():
    return "hello, I'm Microservice One"


if __name__ == '__main__':
    app.run(port=1338, debug=True, ssl_context=ssl_context)
