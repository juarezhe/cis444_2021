import jwt
import datetime
from flask import  g

def create_token(token_data):
    token_data['exp'] = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=0, minutes=30)
    token_data['iat'] = datetime.datetime.now(datetime.timezone.utc)

    return jwt.encode( token_data , g.secrets['JWT'],  algorithm="HS256")
