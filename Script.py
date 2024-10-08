import pyodbc
import random
from faker import Faker

# Initialize Faker for generating random data
fake = Faker()

# Connect to the MS SQL database
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};'
                      'SERVER=your_server_name;'
                      'DATABASE=your_database_name;'
                      'UID=your_username;'
                      'PWD=your_password')

cursor = conn.cursor()

# Function to insert data into the database
def insert_data():
    # Insert data into COUNTRY
    for _ in range(10):
        cursor.execute("""
        INSERT INTO COUNTRY (COUNTRY, LAST_UPDATE)
        VALUES (?, GETDATE())
        """, fake.country())
    
    # Insert data into CITY
    cursor.execute("SELECT COUNTRY_ID FROM COUNTRY")
    country_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(10):
        cursor.execute("""
        INSERT INTO CITY (CITY, COUNTRY_ID, LAST_UPDATE)
        VALUES (?, ?, GETDATE())
        """, fake.city(), random.choice(country_ids))
    
    # Insert data into ADDRESS
    cursor.execute("SELECT CITY_ID FROM CITY")
    city_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(20):
        cursor.execute("""
        INSERT INTO ADDRESS (ADDRESS, ADDRESS2, DISTRICT, CITY_ID, POSTAL_CODE, PHONE, LAST_UPDATE)
        VALUES (?, ?, ?, ?, ?, ?, GETDATE())
        """, fake.street_address(), fake.secondary_address(), fake.state(), random.choice(city_ids), fake.postcode(), fake.phone_number())
    
    # Insert data into STORE
    cursor.execute("SELECT ADDRESS_ID FROM ADDRESS")
    address_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(10):
        cursor.execute("""
        INSERT INTO STORE (ADDRESS_ID, LAST_UPDATE)
        VALUES (?, GETDATE())
        """, random.choice(address_ids))
    
    # Insert data into LANGUAGE
    for _ in range(5):
        cursor.execute("""
        INSERT INTO LANGUAGE (NAME, LAST_UPDATE)
        VALUES (?, GETDATE())
        """, fake.language_name())
    
    # Insert data into CATEGORY
    for _ in range(5):
        cursor.execute("""
        INSERT INTO CATEGORY (NAME, LAST_UPDATE)
        VALUES (?, GETDATE())
        """, fake.word())
    
    # Insert data into FILM
    cursor.execute("SELECT LANGUAGE_ID FROM LANGUAGE")
    language_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(100):
        cursor.execute("""
        INSERT INTO FILM (TITLE, DESCRIPTION, RELEASE_YEAR, LANGUAGE_ID, ORIGINAL_LANGUAGE_ID, RENTAL_DURATION, RENTAL_RATE, LENGTH, REPLACEMENT_COST, RATING, SPECIAL_FEATURES, LAST_UPDATE)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """, fake.sentence(), fake.text(), fake.year(), random.choice(language_ids), random.choice(language_ids), random.randint(1, 10), round(random.uniform(1, 5), 2), random.randint(60, 180), round(random.uniform(10, 30), 2), fake.word(), fake.word())
    
    # Insert data into ACTOR
    for _ in range(50):
        cursor.execute("""
        INSERT INTO ACTOR (FIRST_NAME, LAST_NAME, LAST_UPDATE)
        VALUES (?, ?, GETDATE())
        """, fake.first_name(), fake.last_name())
    
    # Insert data into FILM_ACTOR
    cursor.execute("SELECT FILM_ID FROM FILM")
    film_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT ACTOR_ID FROM ACTOR")
    actor_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(200):
        cursor.execute("""
        INSERT INTO FILM_ACTOR (FILM_ID, ACTOR_ID, LAST_UPDATE)
        VALUES (?, ?, GETDATE())
        """, random.choice(film_ids), random.choice(actor_ids))
    
    # Insert data into FILM_CATEGORY
    cursor.execute("SELECT CATEGORY_ID FROM CATEGORY")
    category_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(100):
        cursor.execute("""
        INSERT INTO FILM_CATEGORY (FILM_ID, CATEGORY_ID, LAST_UPDATE)
        VALUES (?, ?, GETDATE())
        """, random.choice(film_ids), random.choice(category_ids))
    
    # Insert data into INVENTORY
    cursor.execute("SELECT STORE_ID FROM STORE")
    store_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(200):
        cursor.execute("""
        INSERT INTO INVENTORY (FILM_ID, STORE_ID, LAST_UPDATE)
        VALUES (?, ?, GETDATE())
        """, random.choice(film_ids), random.choice(store_ids))
    
    # Insert data into CUSTOMER
    for _ in range(100):
        cursor.execute("""
        INSERT INTO CUSTOMER (STORE_ID, FIRST_NAME, LAST_NAME, EMAIL, ADDRESS_ID, ACTIVE, CREATE_DATE, LAST_UPDATE)
        VALUES (?, ?, ?, ?, ?, ?, GETDATE(), GETDATE())
        """, random.choice(store_ids), fake.first_name(), fake.last_name(), fake.email(), random.choice(address_ids), random.choice([0, 1]))
    
    # Insert data into STAFF
    for _ in range(10):
        cursor.execute("""
        INSERT INTO STAFF (FIRST_NAME, LAST_NAME, ADDRESS_ID, EMAIL, STORE_ID, ACTIVE, USERNAME, PASSWORD, LAST_UPDATE)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
        """, fake.first_name(), fake.last_name(), random.choice(address_ids), fake.email(), random.choice(store_ids), random.choice([0, 1]), fake.user_name(), fake.password())
    
    # Insert data into RENTAL
    cursor.execute("SELECT CUSTOMER_ID FROM CUSTOMER")
    customer_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT INVENTORY_ID FROM INVENTORY")
    inventory_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT STAFF_ID FROM STAFF")
    staff_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(200):
        cursor.execute("""
        INSERT INTO RENTAL (RENTAL_DATE, INVENTORY_ID, CUSTOMER_ID, RETURN_DATE, STAFF_ID, LAST_UPDATE)
        VALUES (GETDATE(), ?, ?, DATEADD(day, ?, GETDATE()), ?, GETDATE())
        """, random.choice(inventory_ids), random.choice(customer_ids), random.randint(1, 30), random.choice(staff_ids))
    
    # Insert data into PAYMENT
    cursor.execute("SELECT RENTAL_ID FROM RENTAL")
    rental_ids = [row[0] for row in cursor.fetchall()]
    
    for _ in range(300):
        cursor.execute("""
        INSERT INTO PAYMENT (CUSTOMER_ID, STAFF_ID, RENTAL_ID, AMOUNT, PAYMENT_DATE, LAST_UPDATE)
        VALUES (?, ?, ?, ?, GETDATE(), GETDATE())
        """, random.choice(customer_ids), random.choice(staff_ids), random.choice(rental_ids), round(random.uniform(1, 100), 2))
    
    # Commit the transaction
    conn.commit()

# Run the data insertion function
insert_data()

# Close the database connection
conn.close()
