import MySQLdb

host = "localhost"
user = "root"
password = "258147"
db = "films_polls"


def connect():
    con = MySQLdb.connect(host=host, user=user, passwd=password, db=db, charset="utf8")
    return con