from OpenSSL import crypto, SSL

CERT = "ssl/client-certs/bad-atat.mil.crt"
CRL = "ssl/client-certs/client-ca.der.crl"

def format_decimal_serial(ser):
    return hex(ser)[2:].swapcase().encode()

def get_serial_number(fyle):
    with open(fyle, "r") as cert_file:
        parsed = crypto.load_certificate(crypto.FILETYPE_PEM, cert_file.read())
        decimal =  parsed.get_serial_number()
        return format_decimal_serial(decimal)

def get_crl_serials(fyle):
    with open(fyle, "rb") as crl_file:
        parsed = crypto.load_crl(crypto.FILETYPE_ASN1, crl_file.read())
        return [rev.get_serial() for rev in parsed.get_revoked()]

def test_cert_blacklist():
    serial_no = get_serial_number(CERT)
    blacklist = get_crl_serials(CRL)
    assert serial_no in blacklist

