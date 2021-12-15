from flask import request, g
from flask_json import json_response
from tools.token_tools import create_token
from tools.logging import logger
import bcrypt


def handle_request():
    logger.debug("Login Handle Request")
    # use data here to auth the user

    username = request.form["username"]
    if not username:
        return json_response(status=404, message="Missing username.")
    # "sub" is used by pyJwt as the owner of the token
    user = {"sub": username}

    password = request.form["password"]
    if not password:
        return json_response(status=404, message="Missing password.")

    cursor = g.DB_CONN.cursor()
    try:
        # Pad with leading zeros up to 8 characters.
        cursor.execute(f"select lpad(user_id::varchar({str(g.USER_ID_LENGTH)}), {str(g.USER_ID_LENGTH)}" +
                       f", '0'), username, password from users where username = '{username}';")
    except:
        print("Database read error. Sending response.")
        return json_response(data={"message": "Error occured while reading from database."}, status=500)

    row = cursor.fetchone()
    if row is not None:
        if bcrypt.checkpw(bytes(password, "utf-8"), bytes(row[2], "utf-8")) == True:
            print(f"Login by user '{username}'. Sending Token.")
            return json_response(token=create_token(user), authenticated=True)
        else:
            print("Incorrect password. Sending response.")
            return json_response(status=401, message="Incorrect password.", authenticated=False)
    else:
        print(f"Username '{username}' does not exist. Sending response.")
        return json_response(status=404, message=f"Username '{username}' does not exist.", authenticated=False)
