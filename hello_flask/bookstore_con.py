import psycopg2


def get_db():
    return psycopg2.connect(host="localhost", dbname="bookstore", user="user_auth", password="k*g7hu+M*?WSxk7F")


def get_db_instance():
    db = get_db()
    cur = db.cursor()

    return db, cur
