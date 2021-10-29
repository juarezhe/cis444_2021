from flask import Flask, render_template, request
from flask_json import FlaskJSON, json_response
from BookstoreCon import GetDb
import bcrypt
import json
import jwt
import datetime

app = Flask(__name__)
FlaskJSON(app)

GLOBAL_DB_CON = GetDb()
JWT_TOKEN = None
JWT_SECRET = None
try:
    with open("secret.txt", "r") as f:
        JWT_SECRET = f.read()
except:
    JWT_SECRET = "clean glove favored starlet bamboo puppet detection crispy gumball imprison quiet collected"


def ValidateToken(token):
    global JWT_TOKEN, JWT_SECRET

    # If the token is still None, it hasn"t been set. Don"t attempt to
    # validate.
    if JWT_TOKEN is None:
        print("No token stored in server.")
        return False
    else:
        fromServer = jwt.decode(JWT_TOKEN, JWT_SECRET, algorithms=["HS256"])
        fromRequest = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        if fromServer == fromRequest:
            print("Valid token.")
            return True
        else:
            print("Tokens do not match.")
            return False


# Default endpoint.
@app.route("/", methods=["GET"])
def Index():
    return render_template("index.html")


#--------------------------Start Token APIs-------------------------------#
@ app.route("/logout", methods=["GET"])
def Logout():
    global JWT_TOKEN
    JWT_TOKEN = None
    print("User logged out. Sending success message.")
    return json_response(data={"message": "User logged out."})
#---------------------------End Token APIs--------------------------------#


#---------------------------Start Item APIs-------------------------------#
# Accepts a user ID and a book ID and creates a record of the purchase.
#
# Returns the successfulness of the database add.
@app.route("/buyBook", methods=["POST"])
def BuyBook():
    global JWT_SECRET
    decodedToken = jwt.decode(request.form["jwt"], JWT_SECRET, algorithms=["HS256"])
    cursor = GLOBAL_DB_CON.cursor()

    try:
        cursor.execute("insert into purchases values (nextval('purchases_transaction_seq'::regclass),'" +
                    str(decodedToken["user_id"]) + "','" + str(request.form["book_id"]) + "','" + str(datetime.datetime.now()) + "'); commit;")
        print("Purchase success. Sending message.")
        return json_response(data={"message": "Book bought successfully."})
    except:
        return json_response(data={"message": "Error occured while writing to database."}, status=500)


# Returns a list of all books in the database.
@ app.route("/getBookList", methods=["POST"])
def GetBookList():
    if ValidateToken(request.form["jwt"]):
        cursor = GLOBAL_DB_CON.cursor()
        try:
            cursor.execute("select * from books;")
        except:
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
                message += '{"book_id":' + str(row[0]) + ',"title":"' + row[1] + \
                    '","price":' + str(row[2]) + "}"
                count += 1
        message += "]}"

        print("Valid user. Sending list of books.")
        return json_response(data=json.loads(message))
    else:
        print("Invalid token. Sending error message.")
        return json_response(data={"message": "User is not logged in."}, status=404)
#----------------------------End Item APIs--------------------------------#


#-------------------------Start Account APIs------------------------------#
# Accepts username and password for authentication against database.
#
# Returns message indicating successfulness of authentication process.
@app.route("/login", methods=["POST"])
def Login():
    cursor = GLOBAL_DB_CON.cursor()
    try:
        cursor.execute("select * from users where username = '" +
                    request.form["username"] + "';")
    except:
        return json_response(data={"message": "Error occured while reading from database."}, status=500)
    row = cursor.fetchone()

    if row is None:
        print("Username '" + request.form["username"] +
              "' does not exist. Sending error message.")
        return json_response(data={"message": "Username '" +
                                   request.form["username"] + "' does not exist."}, status=404)
    else:
        if bcrypt.checkpw(bytes(request.form["password"], "utf-8"), bytes(row[2], "utf-8")) == True:
            print("Login by user '" + request.form["username"] + "'.")
            global JWT_TOKEN, JWT_SECRET
            JWT_TOKEN = jwt.encode(
                {"user_id": row[0]}, JWT_SECRET, algorithm="HS256")
            return json_response(data={"jwt": JWT_TOKEN})
        else:
            print("Incorrect password. Sending error message.")
            return json_response(
                data={"message": "Incorrect password."}, status=404)


# Accepts username and password for adding to the database.
#
# Returns message indicating successfulness of user creation.
@app.route("/signup", methods=["POST"])
def Signup():
    cursor = GLOBAL_DB_CON.cursor()
    try:
        cursor.execute("select * from users where username = '" +
                    request.form["username"] + "';")
    except:
        return json_response(data={"message": "Error occured while reading from database."}, status=500)

    if cursor.fetchone() is None:
        saltedPass = bcrypt.hashpw(
            bytes(request.form["password"], "utf-8"), bcrypt.gensalt(8))
        try:
            cursor.execute("insert into users values (nextval('users_user_id_seq'::regclass),'" +
                        request.form["username"] + "','" + saltedPass.decode("utf-8") + "'); commit;")
            print("Created user " + request.form["username"] + ".")
            return json_response(data={"message": "User created successfully."})
        except:
            return json_response(data={"message": "Error occured while writing to database."}, status=500)
    else:
        print("Username '" + request.form["username"] +
              "' already in use. Sending error message.")
        return json_response(data={"message": "Username '" +
                                   request.form["username"] + "' already in use."}, status=404)
#---------------------------End Account APIs------------------------------#


app.run(host="0.0.0.0", port=80)
