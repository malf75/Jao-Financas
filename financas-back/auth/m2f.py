import pyotp
import segno
import base64
import io

def m2f(email):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)

    issuer_name = "Jao Financas"
    user_email = email
    uri = totp.provisioning_uri(user_email, issuer_name=issuer_name)
    qr = segno.make(uri)

    byte_io = io.BytesIO()
    qr.save(byte_io, kind="png")
    qr_data = byte_io.getvalue()

    qr_base64 = base64.b64encode(qr_data).decode("utf-8")
    return secret, qr_base64

def m2f_verify(secret, otp): 
    totp = pyotp.TOTP(secret)
    valido = totp.verify(otp)
    return valido