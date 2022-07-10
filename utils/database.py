#from . import config_file

import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        return None


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

def main():
    database = r"./stats.db"

    sql_create_players_table = """ CREATE TABLE IF NOT EXISTS players (
                                        id integer PRIMARY KEY,
                                        discord_id integer NOT NULL,
                                        wins integer DEFAULT 0 NOT NULL,
                                        kills integer DEFAULT 0 NOT NULL,
                                        died integer DEFAULT 0 NOT NULL,
                                        plays integer DEFAULT 0 NOT NULL
                                    ); """

    # create a database connection
    conn = sqlite3.connect(database)

    # create tables
    if conn is not None:
        # create table
        create_table(conn, sql_create_players_table)

    else:
        print("Error! cannot create the database connection.")
        print(conn)

def create_record(conn, data):
    sql = ''' INSERT INTO players(discord_id, wins, kills, died, plays)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()


def update_stats(conn, stats):
    sql = ''' UPDATE players
              SET wins = ? ,
                  kills = ? ,
                  died = ? ,
                  plays = ?
              WHERE discord_id = ?'''
    cur = conn.cursor()
    a = cur.execute(sql, stats)
    conn.commit()
    return a

def select_player(conn, discord_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE discord_id=?", (discord_id,))

    return cur.fetchall()



if __name__ == '__main__':
    main()
