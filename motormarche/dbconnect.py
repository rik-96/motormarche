import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

def connection():
    conn = MySQLdb.connect(host = "localhost",
                           user = "root",
                           passwd = '"slashrockstillnow96"',
                           db = "rahulblog")
    c = conn.cursor()

    return c, conn
