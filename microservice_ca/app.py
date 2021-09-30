from datetime import datetime, timedelta
import yaml
from flask import Flask
from OpenSSL import crypto
from OpenSSL.crypto import TYPE_RSA, X509Req
from six import b


def parse_config():
    with open(config_file) as config:
        try:
            cert_config_yaml = yaml.safe_load(config)
        except Exception as config_exception:
            print("Failed to read Configuration %s" % config_exception)
    return cert_config_yaml


app = Flask(__name__)
config_file = "config.yaml"
cert_config = parse_config()
key_type = TYPE_RSA
bit_length = cert_config['CERT'].get('BitLength')
digest_type = cert_config['CERT'].get('digestType')


def create_key():
    key = crypto.PKey()
    key.generate_key(key_type, bit_length)
    return key


def create_csr(ca_key):
    csr = X509Req()
    csr.get_subject().commonName = cert_config['CSR'].get('commonName')
    csr.get_subject().stateOrProvinceName = cert_config['CSR'].get('stateOrProvinceName')
    csr.get_subject().localityName = cert_config['CSR'].get('localityName')
    csr.get_subject().organizationName = cert_config['CSR'].get('organizationName')
    csr.get_subject().organizationalUnitName = cert_config['CSR'].get('organizationalUnitName')
    csr.get_subject().emailAddress = cert_config['CSR'].get('emailAddress')
    csr.get_subject().countryName = cert_config['CSR'].get('countryName')
    csr.set_pubkey(ca_key)
    csr.sign(ca_key, digest_type)
    return csr


def create_crt(ca_csr, ca_key):
    cert = crypto.X509()
    cert.get_subject().commonName = ca_csr.get_subject().commonName
    cert.get_subject().stateOrProvinceName = ca_csr.get_subject().stateOrProvinceName
    cert.get_subject().localityName = ca_csr.get_subject().localityName
    cert.get_subject().organizationName = ca_csr.get_subject().organizationName
    cert.get_subject().organizationalUnitName = ca_csr.get_subject().organizationalUnitName
    cert.get_subject().emailAddress = ca_csr.get_subject().emailAddress
    cert.get_subject().countryName = ca_csr.get_subject().countryName
    cert.set_notBefore(b(datetime.now().strftime("%Y%m%d%H%M%SZ")))
    cert.set_notAfter(b((datetime.now() + timedelta(days=365)).strftime("%Y%m%d%H%M%SZ")))
    cert.set_pubkey(ca_key)
    cert.sign(ca_key, digest_type)
    return cert


@app.route("/certification")
def get():
    ca_key = create_key()
    ca_csr = create_csr(ca_key)
    ca_crt = create_crt(ca_csr, ca_key)
    crt = crypto.dump_certificate(crypto.FILETYPE_PEM, ca_crt).decode("utf-8")
    key = crypto.dump_privatekey(crypto.FILETYPE_PEM, ca_key).decode("utf-8")
    return {"crt": crt, "key": key, "pem": crt + key}, 200


if __name__ == '__main__':
    app.run(port=1340, debug=True)
