import pyotp

def generate_otp():
    otp = pyotp.TOTP(pyotp.random_base32()).now()
    expiration = 300
    return otp, expiration