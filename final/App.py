from DbConn import GetDb
import asyncio
import bcrypt
import datetime
import json
import jwt
import websockets

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


async def handler(websocket):
    async for message in websocket:
        msgAsDict = json.loads(message)
        if msgAsDict["action"] == "signup":
            print("Signup action")
            continue
        
        if msgAsDict["action"] == "login":
            print("Login entry")

            username = msgAsDict["username"]
            if not username:
                await websocket.send(json.dumps({ "data": {"message": "Missing username."}, "status": 404 }))

            password = msgAsDict["password"]
            if not password:
                await websocket.send(json.dumps({ "data": {"message": "Missing password."}, "status": 404 }))

            cursor = GLOBAL_DB_CON.cursor()
            try:
                # Pad with leading zeros up to 8 characters.
                cursor.execute(f"select lpad(user_id::varchar({str(USER_ID_LENGTH)}), {str(USER_ID_LENGTH)}" +
                            f", '0'), username, password from users where username = '{username}';")
            except:
                print("Database read error. Sending response.")
                await websocket.send(json.dumps({ "data": {"message": "Error occured while reading from database."}, "status": 500 }))

            row = cursor.fetchone()
            if row is not None:
                if bcrypt.checkpw(bytes(password, "utf-8"), bytes(row[2], "utf-8")) == True:
                    global JWT_TOKEN
                    JWT_TOKEN = jwt.encode({"user_id": row[0], "username": row[1], "timestamp": str(datetime.datetime.now())},
                                        JWT_SECRET, algorithm="HS256")
                    print(f"Login by user '{username}'. Sending Token.")
                    await websocket.send(json.dumps({ "data": {"jwt": JWT_TOKEN}, "status": 404 }))
                else:
                    print("Incorrect password. Sending response.")
                    await websocket.send(json.dumps({ "data": {"message": "Incorrect password."}, "status": 404 }))
            else:
                print(f"Username '{username}' does not exist. Sending response.")
                await websocket.send(json.dumps({ "data": {"message": f"Username '{username}' does not exist."}, "status": 404 }))
            continue

        if msgAsDict["action"] == "logout":
            print("Logout action")
            continue

        if msgAsDict["action"] == "getBookList":
            print("GetBookList action")
            continue

        if msgAsDict["action"] == "buyBook":
            print("BuyBook action")
            continue

        else:
            print("Unknown action")


async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
