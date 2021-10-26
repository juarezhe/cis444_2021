from flask import Flask, render_template, request
from flask_json import FlaskJSON, json_response
from bookstore_con import get_db
import jwt
import bcrypt

app = Flask(__name__)
FlaskJSON(app)

global_db_con = get_db()
JWT_TOKEN = None
JWT_SECRET = None
with open("secret.txt", "r") as f:
    JWT_SECRET = f.read()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


#---------------------------Start Item APIs-------------------------------#
# Accepts aone or more books for adding to the database.
#
# Returns the successfulness of the database add.
@app.route('/addBooks', methods=['POST'])
def addBooks():
    cur = global_db_con.cursor()
    cur.execute("select * from books;")
    message = '{'
    while 1:
        row = cur.fetchone()
        if row is None:
            break
        else:
            message += row
    message += '}'
    print(message)
    return json_response(data=message)


# Returns the entire list of all books in the database.
@app.route('/fetchBookList', methods=['GET'])
def fetchBookList():
    cur = global_db_con.cursor()
    cur.execute("select * from books;")
    message = '{'
    while 1:
        row = cur.fetchone()
        if row is None:
            break
        else:
            message += row
    message += '}'
    print(message)
    return json_response(data=message)
#----------------------------End Item APIs--------------------------------#


#--------------------------Start Token APIs-------------------------------#
# Returns a web token if a valid one exists. Otherwise, returns an error
# message.
@app.route('/fetchToken', methods=['GET'])
def fetchToken():
    global JWT_TOKEN
    if JWT_TOKEN is None:
        print("Token does not exist. Sending error message.")
        return json_response(data={"Error": "No token stored in server."})
    return json_response(jwt=JWT_TOKEN)


# Accepts a web token.
#
# Returns the successfulness of the token comparison. On success, returns
# the same web token? On failure, returns an error message.
@app.route('/validateToken', methods=['POST'])
def validateToken():
    global JWT_TOKEN, JWT_SECRET

    # If the token is still None, it hasn't been set. Don't attempt to
    # validate.
    if JWT_TOKEN is None:
        print("Token does not exist. Sending error message.")
        return json_response(data={"Error": "No token stored in server."})

    local_decode = jwt.decode(JWT_TOKEN, JWT_SECRET, algorithms=["HS256"])
    post_decode = jwt.decode(
        request.form['jwt'], JWT_SECRET, algorithms=["HS256"])
    if local_decode == post_decode:
        print("Tokens match. Sending success message.")
        return json_response(data=request.form)

    print("Tokens do not match. Sending error message.")
    return json_response(data={"Error": "Tokens do not match."})
#---------------------------End Token APIs--------------------------------#


#-------------------------Start Account APIs------------------------------#
# Accepts a username and password for authentication against database.
#
# Returns successfulness of authentication. On success, returns a web
# token? On failure, returns an error message.
@app.route('/login', methods=['POST'])
def login():
    cur = global_db_con.cursor()
    form_salted = bcrypt.hashpw(
        bytes(request.form['login_pass'], 'utf-8'), bcrypt.gensalt(8))
    cur.execute("select * from users where username = '" +
                request.form['login_user'] + "';")
    row = cur.fetchone()
    if row is None:
        print('Username "' + request.form['login_user'] +
              '" does not exist. Sending error message.')
        return json_response(data={"Error": "Username '" + request.form['login_user'] + "' does not exist."})
    else:
        if bcrypt.checkpw(form_salted, bytes(row[2], 'utf-8')) == 'false':
            print('Passwords do not match. Sending error message.')
            return json_response(data={"Error": "Passwords do not match."})
        else:
            print('Login by user ' + request.form['login_user'])
            global JWT_TOKEN, JWT_SECRET
            JWT_TOKEN = jwt.encode(
                {"userId": row[0]}, JWT_SECRET, algorithm="HS256")
            # TODO: This should be a valid message.
            # Potentially return the token itself in this message.
            # return json_response(data={"Error": "Unknown error."})
    return json_response(data={"Error": "Unknown error."}) # TODO: Remove this when above is addressed.


@app.route('/signup', methods=['POST'])
def signup():
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
        print('Error: username "' +
              request.form['signup_user'] + '" already in use.')
    return index()
#---------------------------End Account APIs------------------------------#


app.run(host='0.0.0.0', port=80)
