import psycopg2
import yaml

def get_db():
    yml_filename = 'connection.yml'
    try:
        yml_conn = {}
        with open(yml_filename, 'r') as yml_file:
            yml_conn = yaml.safe_load(yml_file)

        return psycopg2.connect(host=yml_conn["host"], dbname=yml_conn["dbname"], user=yml_conn["user"], password=yml_conn["password"])
    except:
        error = f"Unable to read {yml_filename}.\n" + \
            "Please add the file with connection data in JSON format:\n" + \
            "{\"host\":, \"dbname\":, \"user\":, \"password\":}"
        raise Exception(error)
