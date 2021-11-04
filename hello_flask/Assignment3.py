from flask import Flask, render_template, request
from flask_json import FlaskJSON, json_response
from BookstoreConn import GetDb
import bcrypt
import json
import jwt
import datetime

app = Flask(__name__)
FlaskJSON(app)

GLOBAL_DB_CON = GetDb()
BOOK_ID_LENGTH = 8
USER_ID_LENGTH = 8
JWT_TOKEN = None
JWT_SECRET = None
try:
    with open("secret.txt", "r") as f:
        JWT_SECRET = f.read()
except:
    JWT_SECRET = "clean glove favored starlet bamboo puppet detection crispy gumball imprison quiet collected"


def ValidateToken(token):
    print("ValidateToken() entry")

    # If the token is still None, it hasn"t been set. Don"t attempt to
    # validate.
    if JWT_TOKEN is None:
        return False
    else:
        fromClient = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        fromServer = jwt.decode(JWT_TOKEN, JWT_SECRET, algorithms=["HS256"])
        return fromClient == fromServer


# Default endpoint.
@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def Index():
    print("Index() entry")

    return render_template("index.html")


#--------------------------Start Token APIs-------------------------------#
@ app.route("/logout", methods=["GET"])
def Logout():
    print("Logout() entry")

    if ValidateToken(request.args.get("jwt")):
        # TODO: Remove token from list of valid, active tokens?
        global JWT_TOKEN
        JWT_TOKEN = None
        print("User logged out. Sending response.")
        return json_response(data={"message": "User logged out."})
    else:
        print("User not logged in. Sending response.")
        return json_response(data={"message": "Already logged out."})
#---------------------------End Token APIs--------------------------------#


#---------------------------Start Item APIs-------------------------------#
# Accepts a JWT and a book ID. Upon successful validation of the JWT,
# creates a record of the purchase.
#
# Returns the successfulness of the database add.
@app.route("/buyBook", methods=["GET"])
def BuyBook():
    print("BuyBook() entry")

    token = request.args.get("jwt")
    if not token:
        print("Missing token. Sending response.")
        return json_response(data={"message": "Missing token."}, status=404)

    if not ValidateToken(token):
        print("Invalid token. Sending response.")
        return json_response(data={"message": "User is not logged in."}, status=404)

    decodedToken = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    cursor = GLOBAL_DB_CON.cursor()
    try:
        cursor.execute(f"insert into purchases values (nextval('purchases_transaction_seq'::regclass),'" +
                       f"{str(decodedToken['user_id'])}','{str(request.args.get('book_id'))}','" +
                       f"{str(datetime.datetime.now())}'); commit;")
        print("Purchase success. Sending response.")
        return json_response(data={"message": "Book bought successfully."})
    except:
        print("Database write error. Sending response.")
        return json_response(data={"message": "Error occured while writing to database."}, status=500)


# Returns a list of all books in the database.
@ app.route("/getBookList", methods=["GET"])
def GetBookList():
    print("GetBookList() entry")

    if not ValidateToken(request.args.get("jwt")):
        print("Invalid token. Sending response.")
        return json_response(data={"message": "User is not logged in."}, status=404)

    cursor = GLOBAL_DB_CON.cursor()
    try:
        cursor.execute(f"select lpad(book_id::varchar({str(BOOK_ID_LENGTH)}), " +
                       f"{str(BOOK_ID_LENGTH)}, '0'), title, price from books;")
    except:
        print("Database read error. Sending response.")
        return json_response(data={"message": "Error occured while reading from database."}, status=500)

    count = 0
    message = '{"books":['
    while 1:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            if count > 0:
                message += ","
            message += '{"book_id":"' + row[0] + '","title":"' + \
                row[1] + '","price":' + str(row[2]) + "}"
            count += 1
    message += "]}"

    print("Valid token. Sending list of books.")
    return json_response(data=json.loads(message))
#----------------------------End Item APIs--------------------------------#


#-------------------------Start Account APIs------------------------------#
# Accepts username and password for authentication against database.
#
# Returns message indicating successfulness of authentication process.
@app.route("/login", methods=["POST"])
def Login():
    print("Login() entry")

    username = request.form["username"]
    if not username:
        return json_response(data={"message": "Missing username."}, status=404)

    password = request.form["password"]
    if not password:
        return json_response(data={"message": "Missing password."}, status=404)

    cursor = GLOBAL_DB_CON.cursor()
    try:
        # Pad with leading zeros up to 8 characters.
        cursor.execute(f"select lpad(user_id::varchar({str(USER_ID_LENGTH)}), {str(USER_ID_LENGTH)}" +
                       f", '0'), username, password from users where username = '{username}';")
    except:
        print("Database read error. Sending response.")
        return json_response(data={"message": "Error occured while reading from database."}, status=500)

    row = cursor.fetchone()
    if row is not None:
        if bcrypt.checkpw(bytes(password, "utf-8"), bytes(row[2], "utf-8")) == True:
            global JWT_TOKEN
            JWT_TOKEN = jwt.encode({"user_id": row[0], "username": row[1], "timestamp": str(datetime.datetime.now())},
                                   JWT_SECRET, algorithm="HS256")
            print(f"Login by user '{username}'. Sending Token.")
            return json_response(data={"jwt": JWT_TOKEN})
        else:
            print("Incorrect password. Sending response.")
            return json_response(data={"message": "Incorrect password."}, status=404)
    else:
        print(f"Username '{username}' does not exist. Sending response.")
        return json_response(data={"message": f"Username '{username}' does not exist."}, status=404)


# Accepts username and password for adding to the database.
#
# Returns message indicating successfulness of user creation.
@app.route("/signup", methods=["POST"])
def Signup():
    print("Signup() entry")

    username = request.form["username"]
    if not username:
        return json_response(data={"message": "Missing username."}, status=404)

    password = request.form["password"]
    if not password:
        return json_response(data={"message": "Missing password."}, status=404)

    cursor = GLOBAL_DB_CON.cursor()
    try:
        cursor.execute(f"select * from users where username = '{username}';")
    except:
        return json_response(data={"message": "Error occured while reading from database."}, status=500)

    if cursor.fetchone() is None:
        saltedPass = bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt(8))
        try:
            cursor.execute(f"insert into users values (nextval('users_user_id_seq'::regclass),'" +
                           f"{username}','{saltedPass.decode('utf-8')}'); commit;")
            print(f"Created user '{username}'.")
            return json_response(data={"message": f"User '{username}' created successfully."})
        except:
            print("Database error occurre. Sending response.")
            return json_response(data={"message": "Error occured while writing to database."}, status=500)
    else:
        print(f"Username '{username}' already in use. Sending response.")
        return json_response(data={"message": f"Username '{username}' already in use."}, status=404)
#---------------------------End Account APIs------------------------------#


app.run(host="0.0.0.0", port=80)
