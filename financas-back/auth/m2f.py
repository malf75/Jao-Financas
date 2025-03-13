import pyotp
import segno
import base64
import io
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from setup.settings import KEY

key = base64.b64decode(KEY)

def m2f(email):
    try:
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

        cipher = AES.new(key, AES.MODE_CBC)
        iv = cipher.iv
        encrypted = cipher.encrypt(pad(secret.encode(), AES.block_size))
        secret_encoded = base64.b64encode(iv + encrypted).decode()
        return secret_encoded, qr_base64
    except Exception as e:
        return {"message":f"Erro ao gerar o totp: {e}"}
    
def m2f_verify(secret, otp):
    try:
        data = base64.b64decode(secret)
        iv, encrypted = data[:16], data[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        secret_decoded = unpad(cipher.decrypt(encrypted), AES.block_size).decode()
        
        totp = pyotp.TOTP(secret_decoded)
        valido = totp.verify(otp)
        return valido
    except Exception as e:
        return {"message":f"Erro ao verificar OTP: {e}"}