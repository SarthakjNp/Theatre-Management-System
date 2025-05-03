import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, timedelta
import os
import random

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': 'theatre_db'
}

# Database connection helper
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Create database if it doesn't exist
def create_database():
    try:
        # Connect without specifying database
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if DB_CONFIG['database'] not in databases:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"Database '{DB_CONFIG['database']}' created successfully")
        else:
            print(f"Database '{DB_CONFIG['database']}' already exists")
        
        cursor.close()
        conn.close()
    except Error as e:
        print(f"Error checking/creating database: {e}")

# Database Schema Creation (DDL)
def create_database_schema():
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        # Check if tables exist
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        tables_to_create = {
            'Movie': '''
            CREATE TABLE IF NOT EXISTS Movie (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                genre VARCHAR(100) NOT NULL,
                duration INT NOT NULL,
                language VARCHAR(50) NOT NULL
            )
            ''',
            'Auditorium': '''
            CREATE TABLE IF NOT EXISTS Auditorium (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                capacity INT NOT NULL
            )
            ''',
            'Showtime': '''
            CREATE TABLE IF NOT EXISTS Showtime (
                id INT AUTO_INCREMENT PRIMARY KEY,
                movie_id INT NOT NULL,
                audi_id INT NOT NULL,
                datetime DATETIME NOT NULL,
                FOREIGN KEY (movie_id) REFERENCES Movie(id),
                FOREIGN KEY (audi_id) REFERENCES Auditorium(id)
            )
            ''',
            'Ticket': '''
            CREATE TABLE IF NOT EXISTS Ticket (
                id INT AUTO_INCREMENT PRIMARY KEY,
                showtime_id INT NOT NULL,
                seat_no INT NOT NULL,
                status VARCHAR(20) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (showtime_id) REFERENCES Showtime(id)
            )
            ''',
            'FoodItem': '''
            CREATE TABLE IF NOT EXISTS FoodItem (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL
            )
            ''',
            'FoodOrder': '''
            CREATE TABLE IF NOT EXISTS FoodOrder (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                item_id INT NOT NULL,
                quantity INT NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (item_id) REFERENCES FoodItem(id)
            )
            ''',
            'Staff': '''
            CREATE TABLE IF NOT EXISTS Staff (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                role VARCHAR(50) NOT NULL,
                shift VARCHAR(20) NOT NULL
            )
            '''
        }
        
        # Create tables that don't exist
        for table_name, create_query in tables_to_create.items():
            if table_name not in existing_tables:
                cursor.execute(create_query)
                print(f"Table '{table_name}' created successfully")
        
        conn.commit()
        print("Database schema checked/created successfully!")
    except Error as e:
        print(f"Error creating schema: {e}")
    finally:
        cursor.close()
        conn.close()

# Initial Data Insertion
def insert_initial_data():
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        # Check if tables have data
        tables_to_check = ['Auditorium', 'Staff', 'FoodItem']
        should_insert = False
        
        for table in tables_to_check:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count == 0:
                should_insert = True
                break
        
        if should_insert:
            # Insert Auditoriums
            auditoriums = [
                ('Main Hall', 150),
                ('Silver Screen', 120),
                ('Mini Theater', 100)
            ]
            cursor.executemany('INSERT INTO Auditorium (name, capacity) VALUES (%s, %s)', auditoriums)
            
            # Insert Staff
            staff = [
                ('John Doe', 'Janitor', 'morning'),
                ('Jane Smith', 'Janitor', 'afternoon'),
                ('Mike Johnson', 'Janitor', 'night'),
                ('Sarah Wilson', 'Janitor', 'morning'),
                ('Tom Brown', 'Cashier', 'morning'),
                ('Lisa Davis', 'Cashier', 'afternoon'),
                ('Mark Taylor', 'Cashier', 'night'),
                ('Emma White', 'Food Counter', 'morning'),
                ('David Miller', 'Food Counter', 'afternoon'),
                ('Anna Clark', 'Food Counter', 'night')
            ]
            cursor.executemany('INSERT INTO Staff (name, role, shift) VALUES (%s, %s, %s)', staff)
            
            # Insert Food Items
            food_items = [
                ('Popcorn Large', 8.99),
                ('Nachos with Cheese', 7.99),
                ('Soft Drink', 4.99),
                ('Hot Dog', 6.99),
                ('Candy Pack', 3.99)
            ]
            cursor.executemany('INSERT INTO FoodItem (name, price) VALUES (%s, %s)', food_items)
            
            conn.commit()
            print("Initial data inserted successfully!")
        else:
            print("Database already contains initial data. Skipping insertion.")
            
    except Error as e:
        print(f"Error inserting initial data: {e}")
    finally:
        cursor.close()
        conn.close()

# Movie Operations
def add_movie(title, genre, duration, language):
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        INSERT INTO Movie (title, genre, duration, language)
        VALUES (%s, %s, %s, %s)
        ''', (title, genre, duration, language))
        conn.commit()
        print(f"Movie '{title}' added successfully!")
    except Error as e:
        print(f"Error adding movie: {e}")
    finally:
        cursor.close()
        conn.close()

def view_movies():
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        movies_df = pd.read_sql_query("SELECT * FROM Movie", conn)
        return movies_df
    except Error as e:
        print(f"Error viewing movies: {e}")
        return None
    finally:
        conn.close()

# Showtime Operations
def add_showtime(movie_id, audi_id, datetime_str):
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        # Validate movie_id and audi_id exist
        cursor.execute("SELECT id FROM Movie WHERE id = %s", (movie_id,))
        if not cursor.fetchone():
            print("Error: Movie ID does not exist!")
            return
            
        cursor.execute("SELECT id, capacity FROM Auditorium WHERE id = %s", (audi_id,))
        audi = cursor.fetchone()
        if not audi:
            print("Error: Auditorium ID does not exist!")
            return
            
        # Add showtime
        cursor.execute('''
        INSERT INTO Showtime (movie_id, audi_id, datetime)
        VALUES (%s, %s, %s)
        ''', (movie_id, audi_id, datetime_str))
        
        showtime_id = cursor.lastrowid
        
        # Create available tickets for all seats
        audi_capacity = audi[1]
        tickets = [(showtime_id, seat_no, 'available', 10.0) 
                  for seat_no in range(1, audi_capacity + 1)]
        
        cursor.executemany('''
        INSERT INTO Ticket (showtime_id, seat_no, status, price)
        VALUES (%s, %s, %s, %s)
        ''', tickets)
        
        conn.commit()
        print(f"Showtime added successfully with {audi_capacity} available seats!")
    except Error as e:
        print(f"Error adding showtime: {e}")
    finally:
        cursor.close()
        conn.close()

def view_showtimes():
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        query = '''
        SELECT 
            Showtime.id,
            Movie.title,
            Auditorium.name as auditorium,
            Showtime.datetime,
            (SELECT COUNT(*) FROM Ticket 
             WHERE Ticket.showtime_id = Showtime.id 
             AND Ticket.status = 'available') as available_seats
        FROM Showtime
        JOIN Movie ON Showtime.movie_id = Movie.id
        JOIN Auditorium ON Showtime.audi_id = Auditorium.id
        '''
        showtimes_df = pd.read_sql_query(query, conn)
        return showtimes_df
    except Error as e:
        print(f"Error viewing showtimes: {e}")
        return None
    finally:
        conn.close()

# Ticket Operations
def book_ticket(showtime_id, seat_no, price):
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        # Check if ticket exists and is available
        cursor.execute('''
        SELECT id, status FROM Ticket 
        WHERE showtime_id = %s AND seat_no = %s
        ''', (showtime_id, seat_no))
        
        ticket = cursor.fetchone()
        if not ticket:
            print("Error: Invalid showtime or seat number!")
            return
        
        if ticket[1] != 'available':
            print("Error: Seat is already booked!")
            return
        
        # Book the ticket
        cursor.execute('''
        UPDATE Ticket 
        SET status = 'booked', price = %s
        WHERE showtime_id = %s AND seat_no = %s
        ''', (price, showtime_id, seat_no))
        
        conn.commit()
        print(f"Ticket booked successfully! Seat: {seat_no}, Price: ${price:.2f}")
    except Error as e:
        print(f"Error booking ticket: {e}")
    finally:
        cursor.close()
        conn.close()

def view_tickets(showtime_id):
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        query = '''
        SELECT 
            Ticket.id,
            Ticket.seat_no,
            Ticket.status,
            Ticket.price,
            Movie.title,
            Showtime.datetime
        FROM Ticket
        JOIN Showtime ON Ticket.showtime_id = Showtime.id
        JOIN Movie ON Showtime.movie_id = Movie.id
        WHERE Ticket.showtime_id = %s
        '''
        tickets_df = pd.read_sql_query(query, conn, params=[showtime_id])
        return tickets_df
    except Error as e:
        print(f"Error viewing tickets: {e}")
        return None
    finally:
        conn.close()

# Food Operations
def place_food_order(customer_id, item_id, quantity):
    conn = get_db_connection()
    if not conn:
        return
        
    cursor = conn.cursor()
    
    try:
        # Get item price
        cursor.execute('SELECT price FROM FoodItem WHERE id = %s', (item_id,))
        item = cursor.fetchone()
        
        if not item:
            print("Error: Invalid food item ID!")
            return
            
        total_price = item[0] * quantity
        
        cursor.execute('''
        INSERT INTO FoodOrder (customer_id, item_id, quantity, total_price)
        VALUES (%s, %s, %s, %s)
        ''', (customer_id, item_id, quantity, total_price))
        
        conn.commit()
        print(f"Food order placed successfully! Total: ${total_price:.2f}")
    except Error as e:
        print(f"Error placing food order: {e}")
    finally:
        cursor.close()
        conn.close()

def view_staff():
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        staff_df = pd.read_sql_query("SELECT * FROM Staff", conn)
        return staff_df
    except Error as e:
        print(f"Error viewing staff: {e}")
        return None
    finally:
        conn.close()

# Demo function to show usage of all operations
def demo_theatre_system():
    print("\n=== Theatre Management System Demo ===\n")
    
    # Create database and schema
    create_database()
    create_database_schema()
    insert_initial_data()
    
    # Add movies
    print("Adding movies...")
    add_movie("The Matrix", "Sci-Fi", 136, "English")
    add_movie("Inception", "Sci-Fi", 148, "English")
    add_movie("Parasite", "Drama", 132, "Korean")
    
    print("\nViewing all movies:")
    print(view_movies())
    
    # Add showtimes
    print("\nAdding showtimes...")
    add_showtime(1, 1, "2024-03-20 18:00:00")  # Matrix in Main Hall
    add_showtime(2, 2, "2024-03-20 19:00:00")  # Inception in Silver Screen
    
    print("\nViewing all showtimes:")
    print(view_showtimes())
    
    # Book tickets
    print("\nBooking tickets...")
    book_ticket(1, 1, 12.99)  # Book seat 1 for first showtime
    book_ticket(1, 2, 12.99)  # Book seat 2 for first showtime
    
    print("\nViewing tickets for showtime 1:")
    print(view_tickets(1))
    
    # Place food orders
    print("\nPlacing food orders...")
    place_food_order(1, 1, 2)  # 2 large popcorns
    place_food_order(1, 3, 2)  # 2 soft drinks
    
    print("\nViewing staff:")
    print(view_staff())

def display_menu():
    print("\n=== Theatre Management System ===")
    print("1. Movie Management")
    print("2. Showtime Management")
    print("3. Ticket Management")
    print("4. Food Management")
    print("5. Staff Management")
    print("6. View Reports")
    print("7. Exit")
    return input("Enter your choice (1-7): ")

def movie_menu():
    while True:
        print("\n=== Movie Management ===")
        print("1. Add New Movie")
        print("2. View All Movies")
        print("3. Back to Main Menu")
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            title = input("Enter movie title: ")
            genre = input("Enter genre: ")
            duration = int(input("Enter duration (minutes): "))
            language = input("Enter language: ")
            add_movie(title, genre, duration, language)
            
        elif choice == '2':
            movies = view_movies()
            if movies is not None:
                print("\nAll Movies:")
                print(movies)
                
        elif choice == '3':
            break
            
        else:
            print("Invalid choice. Please try again.")

def showtime_menu():
    while True:
        print("\n=== Showtime Management ===")
        print("1. Add New Showtime")
        print("2. View All Showtimes")
        print("3. Back to Main Menu")
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            # Show available movies
            movies = view_movies()
            if movies is not None:
                print("\nAvailable Movies:")
                print(movies)
                movie_id = int(input("Enter movie ID: "))
                
                # Show available auditoriums
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM Auditorium")
                    auditoriums = cursor.fetchall()
                    print("\nAvailable Auditoriums:")
                    for audi in auditoriums:
                        print(f"ID: {audi[0]}, Name: {audi[1]}, Capacity: {audi[2]}")
                    cursor.close()
                    conn.close()
                    
                audi_id = int(input("Enter auditorium ID: "))
                datetime_str = input("Enter showtime (YYYY-MM-DD HH:MM:SS): ")
                add_showtime(movie_id, audi_id, datetime_str)
                
        elif choice == '2':
            showtimes = view_showtimes()
            if showtimes is not None:
                print("\nAll Showtimes:")
                print(showtimes)
                
        elif choice == '3':
            break
            
        else:
            print("Invalid choice. Please try again.")

def ticket_menu():
    while True:
        print("\n=== Ticket Management ===")
        print("1. Book Ticket")
        print("2. View Tickets for Showtime")
        print("3. Back to Main Menu")
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            showtimes = view_showtimes()
            if showtimes is not None:
                print("\nAvailable Showtimes:")
                print(showtimes)
                showtime_id = int(input("Enter showtime ID: "))
                
                # Show available seats
                tickets = view_tickets(showtime_id)
                if tickets is not None:
                    print("\nAvailable Seats:")
                    available_seats = tickets[tickets['status'] == 'available']
                    print(available_seats[['seat_no', 'price']])
                    
                    seat_no = int(input("Enter seat number: "))
                    price = float(input("Enter ticket price: "))
                    book_ticket(showtime_id, seat_no, price)
                    
        elif choice == '2':
            showtime_id = int(input("Enter showtime ID: "))
            tickets = view_tickets(showtime_id)
            if tickets is not None:
                print("\nTickets for Showtime:")
                print(tickets)
                
        elif choice == '3':
            break
            
        else:
            print("Invalid choice. Please try again.")

def food_menu():
    while True:
        print("\n=== Food Management ===")
        print("1. Place Food Order")
        print("2. View Food Items")
        print("3. Back to Main Menu")
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            # Show available food items
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM FoodItem")
                food_items = cursor.fetchall()
                print("\nAvailable Food Items:")
                for item in food_items:
                    print(f"ID: {item[0]}, Name: {item[1]}, Price: ${item[2]:.2f}")
                cursor.close()
                conn.close()
                
                customer_id = int(input("Enter customer ID (ticket ID): "))
                item_id = int(input("Enter food item ID: "))
                quantity = int(input("Enter quantity: "))
                place_food_order(customer_id, item_id, quantity)
                
        elif choice == '2':
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM FoodItem")
                food_items = cursor.fetchall()
                print("\nFood Items:")
                for item in food_items:
                    print(f"ID: {item[0]}, Name: {item[1]}, Price: ${item[2]:.2f}")
                cursor.close()
                conn.close()
                
        elif choice == '3':
            break
            
        else:
            print("Invalid choice. Please try again.")

def staff_menu():
    while True:
        print("\n=== Staff Management ===")
        print("1. View All Staff")
        print("2. Add New Staff")
        print("3. Back to Main Menu")
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            staff = view_staff()
            if staff is not None:
                print("\nAll Staff:")
                print(staff)
                
        elif choice == '2':
            name = input("Enter staff name: ")
            role = input("Enter role: ")
            shift = input("Enter shift (morning/afternoon/night): ")
            
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO Staff (name, role, shift)
                VALUES (%s, %s, %s)
                ''', (name, role, shift))
                conn.commit()
                print(f"Staff member {name} added successfully!")
                cursor.close()
                conn.close()
                
        elif choice == '3':
            break
            
        else:
            print("Invalid choice. Please try again.")

def reports_menu():
    while True:
        print("\n=== Reports ===")
        print("1. View Movie Statistics")
        print("2. View Revenue Report")
        print("3. View Staff Schedule")
        print("4. Back to Main Menu")
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT 
                    Movie.title,
                    COUNT(Showtime.id) as total_showtimes,
                    COUNT(Ticket.id) as total_tickets_sold,
                    SUM(CASE WHEN Ticket.status = 'booked' THEN Ticket.price ELSE 0 END) as total_revenue
                FROM Movie
                LEFT JOIN Showtime ON Movie.id = Showtime.movie_id
                LEFT JOIN Ticket ON Showtime.id = Ticket.showtime_id
                GROUP BY Movie.id
                ''')
                results = cursor.fetchall()
                print("\nMovie Statistics:")
                for row in results:
                    print(f"Movie: {row[0]}")
                    print(f"Total Showtimes: {row[1]}")
                    print(f"Total Tickets Sold: {row[2]}")
                    print(f"Total Revenue: ${row[3]:.2f}")
                    print("-------------------")
                cursor.close()
                conn.close()
                
        elif choice == '2':
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT 
                    DATE(Showtime.datetime) as date,
                    SUM(CASE WHEN Ticket.status = 'booked' THEN Ticket.price ELSE 0 END) as ticket_revenue,
                    SUM(FoodOrder.total_price) as food_revenue
                FROM Showtime
                LEFT JOIN Ticket ON Showtime.id = Ticket.showtime_id
                LEFT JOIN FoodOrder ON Ticket.id = FoodOrder.customer_id
                GROUP BY DATE(Showtime.datetime)
                ''')
                results = cursor.fetchall()
                print("\nDaily Revenue Report:")
                for row in results:
                    print(f"Date: {row[0]}")
                    print(f"Ticket Revenue: ${row[1]:.2f}")
                    print(f"Food Revenue: ${row[2]:.2f}")
                    print(f"Total Revenue: ${row[1] + row[2]:.2f}")
                    print("-------------------")
                cursor.close()
                conn.close()
                
        elif choice == '3':
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT 
                    role,
                    shift,
                    COUNT(*) as staff_count
                FROM Staff
                GROUP BY role, shift
                ORDER BY role, shift
                ''')
                results = cursor.fetchall()
                print("\nStaff Schedule:")
                for row in results:
                    print(f"Role: {row[0]}")
                    print(f"Shift: {row[1]}")
                    print(f"Number of Staff: {row[2]}")
                    print("-------------------")
                cursor.close()
                conn.close()
                
        elif choice == '4':
            break
            
        else:
            print("Invalid choice. Please try again.")

def main():
    # Initialize database
    create_database()
    create_database_schema()
    insert_initial_data()
    
    while True:
        choice = display_menu()
        
        if choice == '1':
            movie_menu()
        elif choice == '2':
            showtime_menu()
        elif choice == '3':
            ticket_menu()
        elif choice == '4':
            food_menu()
        elif choice == '5':
            staff_menu()
        elif choice == '6':
            reports_menu()
        elif choice == '7':
            print("Thank you for using Theatre Management System!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 