# Theatre Management System

A menu-driven Python application for managing a movie theatre, including movies, showtimes, tickets, food orders, staff, and reports. The system uses a MySQL database for persistent storage.

## Features
- **Movie Management**: Add and view movies.
- **Showtime Management**: Add and view showtimes, with seat allocation.
- **Ticket Management**: Book and view tickets for showtimes.
- **Food Management**: Place food orders and view available food items.
- **Staff Management**: View and add staff members.
- **Reports**: View movie statistics, daily revenue, and staff schedules.

## Requirements
- Python 3.7+
- MySQL Server
- Python packages:
  - `mysql-connector-python`
  - `pandas`

## Setup Instructions

1. **Install Python dependencies:**
   ```bash
   pip install mysql-connector-python pandas
   ```

2. **Set up MySQL:**
   - Ensure MySQL server is running.
   - Update the database credentials in `theatre_management.py` if needed:
     ```python
     DB_CONFIG = {
         'host': 'localhost',
         'user': 'root',
         'password': '12345',
         'database': 'theatre_db'
     }
     ```

3. **Run the application:**
   ```bash
   python theatre_management.py
   ```
   - On first run, the program will create the database and tables if they do not exist, and insert initial data if the tables are empty.
   - On subsequent runs, it will use the existing data.

## Usage
- The program displays a main menu with options for managing movies, showtimes, tickets, food, staff, and reports.
- Navigate using the number keys and follow the prompts.
- Data is stored persistently in the MySQL database.

## Notes
- Make sure your MySQL user has privileges to create databases and tables.
- If you change the database name or credentials, update the `DB_CONFIG` dictionary accordingly.

## License
This project is for educational purposes.
