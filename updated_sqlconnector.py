import mysql.connector
from mysql.connector import Error

def connect_to_database(host_name, user_name, user_password, db_name):
    print("-------------------------------------------")
    """
    Establish a connection to the MySQL database.

    Parameters:
        host_name (str): Hostname or IP address of the MySQL server.
        user_name (str): Username for the MySQL database.
        user_password (str): Password for the MySQL database.
        db_name (str): Name of the database to connect to.

    Returns:
        connection: A MySQL connection object if successful, None otherwise.
    """
    connection = None
    try:
        if not host_name or not user_name or not user_password or not db_name:
            raise ValueError("All input fields (host, username, password, and database) must be provided.")
        
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Database connection successful!")
    except ValueError as ve:
        print(f"Input Error: {ve}")
    except Error as e:
        if e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied: Invalid username or password.")
        elif e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        elif e.errno == mysql.connector.errorcode.CR_UNKNOWN_HOST:
            print("Unknown host: Please check the hostname.")
        else:
            print(f"Database connection failed: {e}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
    return connection

def main():
    """
    Main function to interact with the user and connect to the database.
    """
    print("Welcome to the Database Connection Program!")
    
    # Get user input with validation
    host = input("Enter the hostname: ").strip()
    user = input("Enter the username: ").strip()
    password = input("Enter the password: ").strip()
    database = input("Enter the database name: ").strip()
    
    # Try connecting to the database
    connection = connect_to_database(host, user, password, database)
    
    # Ensure the connection is closed if it was successful
    if connection:
        print("Closing the database connection.")
        connection.close()

if __name__ == "__main__":
    main()



# Hi

# Your account number is: 1033780

# Your new database is now ready to use.

# To connect to your database use these details;

# Host: sql3.freesqldatabase.com
# Database name: sql3746399
# Database user: sql3746399
# Database password: W3jpkLgNTU
# Port number: 3306