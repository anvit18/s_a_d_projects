import pyodbc

# Database connection details
server = 'your_server_name'
database = 'your_database_name'
username = 'your_username'
password = 'your_password'

# Create a connection to the database
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=' + server + ';'
                      'DATABASE=' + database + ';'
                      'UID=' + username + ';'
                      'PWD=' + password)

cursor = conn.cursor()

# SQL commands to create the tables
create_film_table = '''
CREATE TABLE FILM (
    FILM_ID INT IDENTITY(1,1) PRIMARY KEY,
    TITLE VARCHAR(255) NOT NULL
);
'''

create_film_actor_table = '''
CREATE TABLE FILM_ACTOR (
    FILM_ACTOR_ID INT IDENTITY(1,1) PRIMARY KEY,
    FILM_ID INT NOT NULL,
    ACTOR_NAME VARCHAR(255) NOT NULL,
    CONSTRAINT FK_FILM_ACTOR_FILM FOREIGN KEY (FILM_ID) REFERENCES FILM(FILM_ID),
    CONSTRAINT UQ_FILM_ACTOR_FILM UNIQUE (FILM_ID)
);
'''

# Execute the SQL commands
cursor.execute(create_film_table)
cursor.execute(create_film_actor_table)

# Commit the transaction
conn.commit()

# Close the connection
cursor.close()
conn.close()

print("Tables created successfully.")