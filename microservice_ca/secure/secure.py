from OpenSSL.crypto import TYPE_RSA, TYPE_DSA


class Secure:
    def __init__(self, config_file):
        self.ConfigFile = config_file
        cert_config = self.ParseConfig()
        if cert_config['CERT'].get('KeyType') == 'RSA':
            self.KeyType = TYPE_RSA
        elif cert_config['CERT'].get('KeyType') == 'DSA':
            self.KeyType = TYPE_DSA
        self.CsrFile = cert_config['CSR'].get('OldCsrFile')
        self.OldCsrFileType = cert_config['CSR'].get('OldCsrFileType')
        self.BitLength = cert_config['CERT'].get('BitLength')
        self.digestType = cert_config['CERT'].get('digestType')
        self.CertDir = cert_config['CERT'].get('CertDir')
        self.set_notBefore = cert_config['CSR'].get('validfrom')
        self.set_notAfter = cert_config['CSR'].get('validto')
        self.OldPrivateKey = cert_config['REUSE'].get('OldPrivateKey')
        self.OldPrivateKeyType = cert_config['REUSE'].get('OldPrivateKeyType')
        self.Certificate = cert_config['REUSE'].get('Certificate')
        self.validfrom = cert_config['CERT'].get('validfrom')
        self.validto = cert_config['CERT'].get('validto')