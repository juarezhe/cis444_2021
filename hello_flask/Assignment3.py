from flask import Flask, render_template, request
from flask_json import FlaskJSON, json_response
from BookstoreCon import GetDb
import jwt
import bcrypt

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


# Default endpoint.
@app.route("/", methods=["GET"])
def Index():
    return render_template("index.html")


#---------------------------Start Item APIs-------------------------------#
# Accepts one or more books for adding to the database.
#
# Returns the successfulness of the database add.
# @app.route("/addBooks", methods=["POST"])
# def AddBooks():
    # TODO: This is a bit grand for the project, but would simplify
    # adding books to the database.
    # cursor = GLOBAL_DB_CON.cursor()

    # TODO: For each book, do an insert.
    # Build JSON message while iterating for return later.
    # cursor.execute("insert into books values (nextval('books_book_id_seq'::regclass),'" +
    #               request.form["book_title"] + "','" + request.form["book_price"] + "');")
    # Finally, commit the database changes.
    # cursor.commit()
    # return  # json_response(data=message)


# Returns a list of all books in the database.
@ app.route("/fetchBookList", methods=["GET"])
def FetchBookList():
    # TODO: Add books to the database.
    cursor = GLOBAL_DB_CON.cursor()
    cursor.execute("select * from books;")

    count = 0
    message = "{books:{"
    while 1:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            if count > 0:
                message += ","
            message += "{title:" + row[1] + ",price:" + row[2] + "}"
            count += 1
    message += "}\}"

    print("Sending list of books.")
    return json_response(data=message)
#----------------------------End Item APIs--------------------------------#


#--------------------------Start Token APIs-------------------------------#
@ app.route("/logout", methods=["GET"])
def Logout():
    global JWT_TOKEN
    JWT_TOKEN = None
    print("User logged out. Sending updated token.")
    return json_response(data={"message": "User logged out."})


# Accepts a web token.
#
# Returns message indicating successfulness of token validation.
@ app.route("/validateToken", methods=["POST"])
def ValidateToken():
    global JWT_TOKEN, JWT_SECRET

    # If the token is still None, it hasn"t been set. Don"t attempt to
    # validate.
    if JWT_TOKEN is None:
        print("Token does not exist. Sending error message.")
        return json_response(data={"message": "User is not logged in."}, status=404)
    else:
        fromServer = jwt.decode(JWT_TOKEN, JWT_SECRET, algorithms=["HS256"])
        fromRequest = jwt.decode(
            request.form["jwt"], JWT_SECRET, algorithms=["HS256"])

        if fromServer == fromRequest:
            print("Tokens match. Sending success message.")
            return json_response(data={"message": "User successfully validated."})
        else:
            print("Tokens do not match. Sending error message.")
            return json_response(data={"message": "User is not logged in."}, status=404)
#---------------------------End Token APIs--------------------------------#


#-------------------------Start Account APIs------------------------------#
# Accepts username and password for authentication against database.
#
# Returns message indicating successfulness of authentication process.
@app.route("/login", methods=["POST"])
def Login():
    # TODO: Record login attempts?
    cursor = GLOBAL_DB_CON.cursor()
    cursor.execute("select * from users where username = '" +
                   request.form["username"] + "';")
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
                {"userId": row[0]}, JWT_SECRET, algorithm="HS256")
            return json_response(
                data={"jwt": JWT_TOKEN})
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
    cursor.execute("select * from users where username = '" +
                   request.form["username"] + "';")

    if cursor.fetchone() is None:
        saltedPass = bcrypt.hashpw(
            bytes(request.form["password"], "utf-8"), bcrypt.gensalt(8))
        cursor.execute("insert into users values (nextval('users_user_id_seq'::regclass),'" +
                       request.form["username"] + "','" + saltedPass.decode("utf-8") + "'); commit;")
        print("Created user " + request.form["username"] + ".")
        return json_response(data={"message": "User created successfully."})
    else:
        print("Username '" + request.form["username"] +
              "' already in use. Sending error message.")
        return json_response(data={"message": "Username '" +
                                   request.form["username"] + "' already in use."}, status=404)
#---------------------------End Account APIs------------------------------#


app.run(host="0.0.0.0", port=80)
