import mysql.connector
from mysql.connector import Error

################################################################
def mysql_start(host,database,user,password):
    try:
        connection = mysql.connector.connect(host=host,
                                             database=database,
                                             user= user,
                                             password=password,
                                             allow_local_infile = True,
                                             autocommit=True
                                             )
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version", db_Info)
            cursor = connection.cursor()
            print("\nCursor initiated. Use 'cursor.execute(QUERY)' to perform a query in the MYSQL database :)")

    except Error as e:
        print("Error while connecting to MySQL :( ", e)

    return [connection,cursor]

#################################################################
def create_table_generalinfo_db(cursor,tablename):
    sqltable = "CREATE TABLE " + tablename + " (number INT NOT NULL, url VARCHAR(255) NOT NULL, `search input` VARCHAR(255) NOT NULL," \
                                                         "  `google maps name` VARCHAR(255) NOT NULL, id VARCHAR(255) NOT NULL, " \
                                                         "category VARCHAR(255) NOT NULL, address VARCHAR(1000) NOT NULL, " \
                                                         "score VARCHAR(255) NOT NULL, reviews VARCHAR(255) NOT NULL, " \
                                                         "expense VARCHAR(255) NOT NULL, `extra info` VARCHAR(60000) NOT NULL, " \
                                                         "maandag VARCHAR(255) NOT NULL, dinsdag VARCHAR(255) NOT NULL, " \
                                                         "woensdag VARCHAR(255) NOT NULL, donderdag VARCHAR(255) NOT NULL, " \
                                                         "vrijdag VARCHAR(255) NOT NULL, zaterdag VARCHAR(255) NOT NULL, " \
                                                         "zondag VARCHAR(255) NOT NULL, PRIMARY KEY (url));"

    cursor.execute(sqltable)
    pass

#################################################################
def create_table_popinfo_db(cursor,tablename):
    sqltable = "CREATE TABLE " + tablename + " (number INT NOT NULL, url VARCHAR(255) NOT NULL, `search input` VARCHAR(255) NOT NULL," \
                                                         "`google maps name` VARCHAR(255) NOT NULL,id VARCHAR(255) NOT NULL," \
                                                         "`hours in day` VARCHAR(255) NOT NULL, `percentage busy` VARCHAR(255) NOT NULL," \
                                                         "`hour list` VARCHAR(255) NOT NULL, `day list` VARCHAR(255) NOT NULL, PRIMARY KEY (url,`hour list`,`day list`));"

    cursor.execute(sqltable)
    pass


################################################################
def upload_to_db(cursor,file,sqltable):

    query = "LOAD DATA LOCAL INFILE "+ "'" + file + "'" + "IGNORE INTO TABLE " + sqltable + \
            " FIELDS TERMINATED BY \',\'" + " OPTIONALLY ENCLOSED BY '\"'" +  " LINES TERMINATED BY '\\n'"+ " IGNORE 1 ROWS;"
    cursor.execute(query)
    print("\nAdded table successfully to MYSQL database!")
##################################################################