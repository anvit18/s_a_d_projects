import pyodbc
from faker import Faker

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

# Create instances of Faker
fake = Faker()

# Number of records to insert
num_records = 10

# Insert data into FILM table
for _ in range(num_records):
    title = fake.catch_phrase()
    cursor.execute("INSERT INTO FILM (TITLE) VALUES (?)", title)

# Commit the transaction
conn.commit()

# Retrieve FILM_IDs for FILM_ACTOR table
cursor.execute("SELECT FILM_ID FROM FILM")
film_ids = [row[0] for row in cursor.fetchall()]

# Insert data into FILM_ACTOR table
for film_id in film_ids:
    actor_name = fake.name()
    cursor.execute("INSERT INTO FILM_ACTOR (FILM_ID, ACTOR_NAME) VALUES (?, ?)", film_id, actor_name)

# Commit the transaction
conn.commit()

# Close the connection
cursor.close()
conn.close()

print("Data populated successfully.")