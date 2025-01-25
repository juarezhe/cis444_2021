from flask import Flask, redirect, g
from flask_json import FlaskJSON, json_response
import traceback
from db_conn import get_db
from tools.token_required import token_required
from tools.get_aws_secrets import get_secrets
from tools.logging import logger

ERROR_MSG = "Ooops.. Didn't work!"


# Create our app
app = Flask(__name__)
# add in flask json
FlaskJSON(app)


# g is flask for a global var storage
def init_new_env():
    if 'DB_CONN' not in g:
        g.DB_CONN = get_db()
    if 'BOOK_ID_LENGTH' not in g:
        g.BOOK_ID_LENGTH = 8
    if 'USER_ID_LENGTH' not in g:
        g.USER_ID_LENGTH = 8

    g.secrets = get_secrets()


# This gets executed by default by the browser if no page is specified
# So.. we redirect to the endpoint we want to load the base page
@app.route('/')  # endpoint
def index():
    return redirect('/static/index.html')


@app.route("/secure_api/<proc_name>", methods=['GET', 'POST'])
@token_required
def exec_secure_proc(proc_name):
    logger.debug(f"Secure Call to {proc_name}")

    # setup the env
    init_new_env()

    # see if we can execute it..
    resp = ""
    try:
        fn = getattr(__import__('secure_calls.'+proc_name), proc_name)
        resp = fn.handle_request()
    except Exception as err:
        ex_data = str(Exception) + '\n'
        ex_data = ex_data + str(err) + '\n'
        ex_data = ex_data + traceback.format_exc()
        logger.error(ex_data)
        return json_response(status_=500, data=ERROR_MSG)

    return resp


@app.route("/open_api/<proc_name>", methods=['GET', 'POST'])
def exec_proc(proc_name):
    logger.debug(f"Call to {proc_name}")

    # setup the env
    init_new_env()

    # see if we can execute it..
    resp = ""
    try:
        fn = getattr(__import__('open_calls.'+proc_name), proc_name)
        resp = fn.handle_request()
    except Exception as err:
        ex_data = str(Exception) + '\n'
        ex_data = ex_data + str(err) + '\n'
        ex_data = ex_data + traceback.format_exc()
        logger.error(ex_data)
        return json_response(status_=500, data=ERROR_MSG)

    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
