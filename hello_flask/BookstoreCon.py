import psycopg2


def GetDb():
    return psycopg2.connect(host="localhost", dbname="bookstore", user="user_auth", password="k*g7hu+M*?WSxk7F")
