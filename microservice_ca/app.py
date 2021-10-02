from datetime import datetime, timedelta
import yaml
from flask import Flask
from OpenSSL import crypto
from OpenSSL.crypto import TYPE_RSA, X509Req
from six import b
import random
import sys


def parse_config():
    with open(config_file) as config:
        try:
            cert_config_yaml = yaml.safe_load(config)
        except Exception as config_exception:
            print("Failed to read Configuration %s" % config_exception)
    return cert_config_yaml


def get_key_root():
    with open('certificates/ca_root.key', 'rb') as key_file:
        key_data = key_file.read()
    return crypto.load_privatekey(crypto.FILETYPE_PEM, key_data)


def get_crt_root():
    with open('certificates/ca_root.crt', 'rb') as key_file:
        key_data = key_file.read()
    return crypto.load_certificate(crypto.FILETYPE_PEM, key_data)


def load_root_data_ca():
    key_root = get_key_root()
    crt_root = get_crt_root()
    return key_root, crt_root


app = Flask(__name__)
config_file = "config.yaml"
cert_config = parse_config()
key_type = TYPE_RSA
bit_length = cert_config['CERT'].get('BitLength')
digest_type = cert_config['CERT'].get('digestType')
ca_key_root, ca_crt_root = load_root_data_ca()


def create_key():
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, bit_length)
    return key


def create_csr(key):
    csr = X509Req()
    csr.get_subject().commonName = cert_config['CSR'].get('commonName')
    csr.get_subject().stateOrProvinceName = cert_config['CSR'].get('stateOrProvinceName')
    csr.get_subject().localityName = cert_config['CSR'].get('localityName')
    csr.get_subject().organizationName = cert_config['CSR'].get('organizationName')
    csr.get_subject().organizationalUnitName = cert_config['CSR'].get('organizationalUnitName')
    csr.get_subject().emailAddress = cert_config['CSR'].get('emailAddress')
    csr.get_subject().countryName = cert_config['CSR'].get('countryName')
    csr.set_pubkey(key)
    csr.sign(key, digest_type)
    return csr


def create_crt(client_csr):
    crt = crypto.X509()
    crt.set_subject(client_csr.get_subject())
    crt.set_serial_number(random.randint(0, sys.maxsize))
    crt.set_notBefore(b(datetime.now().strftime("%Y%m%d%H%M%SZ")))
    crt.set_notAfter(b((datetime.now() + timedelta(days=1024)).strftime("%Y%m%d%H%M%SZ")))
    crt.set_issuer(ca_crt_root.get_subject())
    crt.set_pubkey(client_csr.get_pubkey())
    crt.sign(ca_key_root, digest_type)
    return crt


@app.route("/certification")
def gen_cert():
    client_key = create_key()
    client_csr = create_csr(client_key)
    client_crt = create_crt(client_csr)
    cert = crypto.dump_certificate(crypto.FILETYPE_PEM, client_crt).decode("utf-8")
    key = crypto.dump_privatekey(crypto.FILETYPE_PEM, client_key).decode("utf-8")
    print(cert)
    print(key)
    return {
        "crt": crypto.dump_certificate(crypto.FILETYPE_PEM, ca_crt_root).decode("utf-8"),
        "key": crypto.dump_privatekey(crypto.FILETYPE_PEM, ca_key_root).decode("utf-8"),
        "pem": cert + key
    }


if __name__ == '__main__':
    app.run(port=1340, debug=True)
