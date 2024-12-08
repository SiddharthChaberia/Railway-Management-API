import mysql.connector
from mysql.connector import Error

# Database configuration
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '1234',
    'database': 'railway_management',
    'port': '3306'
}

def execute_schema(db_config, schema_file):
    try:
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            print("Successfully connected to the database.")
            with open(schema_file, "r") as schema:
                sql_script = schema.read()
            cursor = connection.cursor()
            for statement in sql_script.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            connection.commit()
            print("Schema executed successfully.")

    except Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":
    execute_schema(db_config, "schema.sql")
