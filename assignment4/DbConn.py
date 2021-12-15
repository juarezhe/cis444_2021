import json
import psycopg2


def GetDb():
    fileName = "connection.txt"
    try:
        with open(fileName, "r") as file:
            text = file.read()
        parsed = json.loads(text)
        return psycopg2.connect(host=parsed["host"], dbname=parsed["dbname"], user=parsed["user"], password=parsed["password"])
    except:
        error = f"Unable to read {fileName}.\n" + \
            "Please add the file with connection data in JSON format:\n" + \
            "{\"host\":, \"dbname\":, \"user\":, \"password\":}"
        raise Exception(error)
