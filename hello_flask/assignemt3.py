from flask import Flask, render_template, request
from flask_json import FlaskJSON, json_response
from bookstore_con import get_db
import jwt
import bcrypt

app = Flask(__name__)
FlaskJSON(app)

global_db_con = get_db()
JWT_SECRET = "Test"
JWT_TOKEN = None


def getBooks():
    cur = global_db_con.cursor()
    cur.execute("select * from books;")
    message = '{'
    while 1:
        row = cur.fetchone()
        if row is None:
            print("Error: no books exist yet")
            break
        else:
            message += row
    message += '}'
    print(message)
    return


def getToken():
    token = request.args.get('jwt')
    print(token)
    if token is None:
        return False
    return token


def tokenIsValid():
    token = getToken()
    if token == False:
        print("Token does not exist.")
        return False
    # TODO: Some kind of test for the token
    print(json_response(output=jwt.decode(
        token, JWT_SECRET, algorithms=["HS256"])))
    return True


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/fetchToken', methods=['GET'])
def fetchToken():
    global JWT_TOKEN
    if JWT_TOKEN is None:
        return index()
    return json_response(jwt=JWT_TOKEN)


@app.route('/login', methods=['POST'])
def login():
    cur = global_db_con.cursor()
    form_salted = bcrypt.hashpw(
        bytes(request.form['login_pass'], 'utf-8'), bcrypt.gensalt(8))
    cur.execute("select * from users where username = '" +
                request.form['login_user'] + "';")
    row = cur.fetchone()
    if row is None:
        print('Error: username "' +
              request.form['login_user'] + '" does not exist.')
    else:
        if bcrypt.checkpw(form_salted, bytes(row[2], 'utf-8')) == 'false':
            print('Error: passwords do not match')
        else:
            print('Login by user ' + request.form['login_user'])
            global JWT_TOKEN, JWT_SECRET
            JWT_TOKEN = jwt.encode(
                {"userId": row[0]}, JWT_SECRET, algorithm="HS256")
    return index()


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


app.run(host='0.0.0.0', port=80)
