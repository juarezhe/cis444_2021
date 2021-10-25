from flask import Flask, render_template, request
from flask_json import FlaskJSON
from bookstore_con import get_db

import bcrypt

app = Flask(__name__)
FlaskJSON(app)

global_db_con = get_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:text>', methods=['GET', 'POST'])
def all_routes(text):
    if text == 'login':
        cur = global_db_con.cursor()
        form_salted = bcrypt.hashpw(
            bytes(request.form['login_pass'], 'utf-8'), bcrypt.gensalt(8))
        cur.execute("select password from users where username = '" +
                    request.form['login_user'] + "';")
        fetch = cur.fetchone()
        if fetch is None:
            print('Error - username "' +
                  request.form['login_user'] + '" does not exist.')
        else:
            if bcrypt.checkpw(form_salted, bytes(fetch[0], 'utf-8')) == 'false':
                print('Error - passwords do not match')
            else:
                print('Login by user ' + request.form['login_user'])

    if text == 'signup':
        cur = global_db_con.cursor()
        cur.execute("select username from users where username = '" +
                    request.form['signup_user'] + "';")
        if cur.fetchone() is None:
            salted = bcrypt.hashpw(
                bytes(request.form['signup_pass'], 'utf-8'), bcrypt.gensalt(8))
            cur.execute("insert into users values (nextval('users_user_id_seq'::regclass),'" +
                        request.form['signup_user'] + "','" + salted.decode("utf-8") + "');commit;")
            print('Created user ' + request.form['signup_user'])
        else:
            print('Error - username "' +
                  request.form['signup_user'] + '" already in use.')

    return index()

# For deleting user account
# delete from users where user_id = 0;


app.run(host='0.0.0.0', port=80)
