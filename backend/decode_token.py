import jwt
from decouple import config

token = config('JWT_TOKEN', cast=str)
# Decode the token without verifying the signature
decoded = jwt.decode(token, options={"verify_signature": False})
print(decoded)