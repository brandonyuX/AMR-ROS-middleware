import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_table(conn, insert_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(insert_table_sql)
    except Error as e:
        print(e)

def main():
    database = 'database.db'

    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS user (
                                        id integer PRIMARY KEY,
                                        username text NOT NULL UNIQUE,
                                        password text NOT NULL
                                    ); """

   

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_projects_table)

    else:
        print("Error! cannot create the database connection.")

def insert():
    database = 'database.db'

    sql_create_projects_table = """ INSERT INTO user(username,password) VALUES ('admin','$2b$12$nQxUUXjveFJaoH5SZpWBG.8kJ0AtxCyJy34VzeQcLcNh64MnI0Xry')
     """

   

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        insert_table(conn, sql_create_projects_table)

    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    insert()