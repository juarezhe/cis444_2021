from flask import g
from flask_json import json_response
from tools.token_tools import create_token
from tools.logging import logger
import json


def handle_request():
    logger.debug("Get Books Handle Request")

    cursor = g.DB_CONN.cursor()
    try:
        cursor.execute(f"select lpad(book_id::varchar({str(g.BOOK_ID_LENGTH)}), " +
                       f"{str(g.BOOK_ID_LENGTH)}, '0'), title, price from books;")
    except:
        print("Database read error. Sending response.")
        return json_response(data={"message": "Error occured while reading from database."}, status=500)

    count = 0
    bookList = '{"books":['
    while 1:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            if count > 0:
                bookList += ","
            bookList += '{"book_id":"' + row[0] + '","title":"' + \
                row[1] + '","price":' + str(row[2]) + "}"
            count += 1
    bookList += "]}"

    return json_response(token=create_token(g.jwt_data), books=json.loads(bookList))
