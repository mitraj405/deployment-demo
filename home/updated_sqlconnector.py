# # import mysql.connector
# # from mysql.connector import Error

# # # def connect_to_database(host_name, user_name, user_password, db_name):
# # #     print("-------------------------------------------")
# # #     """
# # #     Establish a connection to the MySQL database.

# # #     Parameters:
# # #         host_name (str): Hostname or IP address of the MySQL server.
# # #         user_name (str): Username for the MySQL database.
# # #         user_password (str): Password for the MySQL database.
# # #         db_name (str): Name of the database to connect to.

# # #     Returns:
# # #         connection: A MySQL connection object if successful, None otherwise.
# # #     """
# # #     connection = None
# # #     try:
# # #         if not host_name or not user_name or not user_password or not db_name:
# # #             raise ValueError("All input fields (host, username, password, and database) must be provided.")
        
# # #         connection = mysql.connector.connect(
# # #             host=host_name,
# # #             user=user_name,
# # #             passwd=user_password,
# # #             database=db_name
# # #         )
# # #         print("Database connection successful!")
# # #     except ValueError as ve:
# # #         print(f"Input Error: {ve}")
# # #     except Error as e:
# # #         if e.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
# # #             print("Access denied: Invalid username or password.")
# # #         elif e.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
# # #             print("Database does not exist.")
# # #         elif e.errno == mysql.connector.errorcode.CR_UNKNOWN_HOST:
# # #             print("Unknown host: Please check the hostname.")
# # #         else:
# # #             print(f"Database connection failed: {e}")
# # #     except Exception as ex:
# # #         print(f"An unexpected error occurred: {ex}")
# # #     return connection

# # # def main():
# # #     """
# # #     Main function to interact with the user and connect to the database.
# # #     """
# # #     print("Welcome to the Database Connection Program!")
    
# # #     # Get user input with validation
# # #     host = input("Enter the hostname: ").strip()
# # #     user = input("Enter the username: ").strip()
# # #     password = input("Enter the password: ").strip()
# # #     database = input("Enter the database name: ").strip()
    
# # #     # Try connecting to the database
# # #     connection = connect_to_database(host, user, password, database)
    
# # #     # Ensure the connection is closed if it was successful
# # #     if connection:
# # #         print("Closing the database connection.")
# # #         connection.close()

# # # if __name__ == "__main__":
# # #     main()



# # # # Hi

# # # # Your account number is: 1033780

# # # # Your new database is now ready to use.

# # # # To connect to your database use these details;

# # # # Host: sql3.freesqldatabase.com
# # # # Database name: sql3746399
# # # # Database user: sql3746399
# # # # Database password: W3jpkLgNTU
# # # # Port number: 3306

# # import json
# # from django.http import JsonResponse
# # from django.shortcuts import HttpResponse


# # def connect_to_databaseup(request):
# #     if request.method == 'POST':
# #         data = json.loads(request.body)
# #         host_name = data.get('hostname')
# #         user_name = data.get('username')
# #         user_password = data.get('password')
# #         db_name = data.get('dbname')  # Assumes database name is sent by the client

# #         try:
# #             connection = mysql.connector.connect(
# #                 host=host_name,
# #                 user=user_name,
# #                 passwd=user_password
# #             )

# #             if connection.is_connected():
# #                 cursor = connection.cursor()

# #                 if db_name:
# #                     cursor.execute(f"USE {db_name}")
# #                     print(f"Connected to database: {db_name}")

# #                     cursor.execute("SHOW TABLES")
# #                     tables = cursor.fetchall()
# #                     print("\nTables and their Schema:")
# #                     for (table_name,) in tables:
# #                         print(f"\nTable: {table_name}")
# #                         cursor.execute(f"DESCRIBE {table_name}")
# #                         columns = cursor.fetchall()
# #                         print(f"{'Column':<20} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<10} {'Extra':<10}")
# #                         for col in columns:
# #                             formatted_values = [
# #                                 col[0] or 'None',
# #                                 col[1] or 'None',
# #                                 col[2] or 'None',
# #                                 col[3] or 'None',
# #                                 col[4] if col[4] is not None else 'None',
# #                                 col[5] or 'None'
# #                             ]
# #                             print("{:<20} {:<20} {:<10} {:<10} {:<10} {:<10}".format(*formatted_values))
# #                 else:
# #                     cursor.execute("SHOW DATABASES")
# #                     databases = cursor.fetchall()
# #                     print("Available Databases:")
# #                     for db in databases:
# #                         print(f"- {db[0]}")

# #                 connection.close()

# #         except Error as e:
# #             print(f"Database connection failed: {str(e)}")
# #             return JsonResponse({"status": "error", "message": f"Database connection failed: {str(e)}"}, status=500)

# #         return HttpResponse("Check your console for details.")

# #     return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

# import mysql.connector
# from mysql.connector import Error
# import json
# from django.http import JsonResponse


# def connect_to_databaseup(request):
#     """
#     Handle database connection, fetch schema, and respond with details.
#     """
#     if request.method == 'POST':
#         try:
#             # Parse the incoming JSON request body
#             data = json.loads(request.body)
#             host_name = data.get('hostname')
#             user_name = data.get('username')
#             user_password = data.get('password')
#             db_name = data.get('dbname')  # Optional database name

#             # Validate input
#             if not host_name or not user_name or not user_password:
#                 return JsonResponse(
#                     {"status": "error", "message": "Missing required fields: hostname, username, or password."},
#                     status=400
#                 )

#             # Establish the database connection
#             connection = mysql.connector.connect(
#                 host=host_name,
#                 user=user_name,
#                 password=user_password
#             )

#             if connection.is_connected():
#                 cursor = connection.cursor()

#                 # Handle schema retrieval if a database name is provided
#                 if db_name:
#                     try:
#                         cursor.execute(f"USE {db_name}")
#                         cursor.execute("SHOW TABLES")
#                         tables = cursor.fetchall()

#                         schema_info = {}
#                         for (table_name,) in tables:
#                             cursor.execute(f"DESCRIBE {table_name}")
#                             schema_info[table_name] = [
#                                 {
#                                     "Field": col[0],
#                                     "Type": col[1],
#                                     "Null": col[2],
#                                     "Key": col[3],
#                                     "Default": col[4] if col[4] is not None else "None",
#                                     "Extra": col[5],
#                                 }
#                                 for col in cursor.fetchall()
#                             ]

#                         # Close connection
#                         connection.close()

#                         return JsonResponse({
#                             "status": "success",
#                             "message": f"Connected to database {db_name}.",
#                             "schema_info": schema_info,
#                         })

#                     except Error as e:
#                         return JsonResponse({
#                             "status": "error",
#                             "message": f"Failed to fetch schema for database '{db_name}': {str(e)}"
#                         }, status=500)

#                 # Handle case where no database name is provided
#                 else:
#                     cursor.execute("SHOW DATABASES")
#                     databases = [db[0] for db in cursor.fetchall()]
#                     connection.close()
#                     return JsonResponse({
#                         "status": "success",
#                         "message": "Available databases fetched.",
#                         "databases": databases
#                     })

#         except Error as e:
#             return JsonResponse(
#                 {"status": "error", "message": f"Database connection failed: {str(e)}"},
#                 status=500
#             )
#         except json.JSONDecodeError:
#             return JsonResponse(
#                 {"status": "error", "message": "Invalid JSON payload."},
#                 status=400
#             )
#         except Exception as e:
#             return JsonResponse(
#                 {"status": "error", "message": f"An unexpected error occurred: {str(e)}"},
#                 status=500
#             )

#     return JsonResponse({"status": "error", "message": "Invalid request method. Only POST is allowed."}, status=405)
# from curses import window
import mysql.connector
from mysql.connector import Error
import json
from django.http import JsonResponse
from functions import *

import json
from django.http import JsonResponse
import mysql.connector
from mysql.connector import Error
from openai import OpenAI
from django.shortcuts import redirect
from django.urls import reverse

from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

@app.route('/connect', methods=['POST'])
def connect_to_databaseup():
    # print(request+"batman")
    
    """
    Handle database connection, fetch schema, send a 'Hi' message using OpenAI,
    and respond with the assistant's reply and database schema details.
    """
    # Define the API key and assistant ID inside the function
    api_key = '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'

    # if request.method == 'POST':
    #     try:
    #         data = json.loads(request.body)
    #         host_name = data.get('hostname')
    #         user_name = data.get('username')
    #         user_password = data.get('password')
    #         db_name = data.get('dbname', None)
    #         thread_id = data.get('thread_id', None)  # Check if a thread_id is passed
    #         multiple_queries = data.get('multiple_queries', False)  # Whether to send multiple queries in the same session

    #         if not host_name or not user_name or not user_password:
    #             return JsonResponse({"status": "error", "message": "Missing required fields."}, status=400)

    #         # Establish the database connection
    #         connection = mysql.connector.connect(
    #             host=host_name,
    #             user=user_name,
    #             password=user_password,
    #             database=db_name
    #         )

    #         if connection.is_connected():
    #             client = OpenAI(api_key=api_key)
    #             if thread_id is None:
    #                 # Create a new thread if no thread ID is provided
    #                 thread = client.beta.threads.create()
    #                 thread_id = thread.id

    #             # Send the first message
    #             content = data.get('message', 'Hi, I am Batman')  # Default first message if not provided
    #             client.beta.threads.messages.create(
    #                 thread_id=thread_id,
    #                 role="user",
    #                 content=content
    #             )

    #             # Optionally send the second message in the same session
    #             if 0==0:
    #                 second_content = "What is my name?"
    #                 client.beta.threads.messages.create(
    #                     thread_id=thread_id,
    #                     role="user",
    #                     content=second_content
    #                 )

    #             # Poll for the assistant's responses
    #             client.beta.threads.runs.create_and_poll(
    #                 thread_id=thread_id,
    #                 assistant_id=assistant_id
    #             )

    #             # Fetch the latest messages
    #             messages = client.beta.threads.messages.list(thread_id=thread_id).data
    #             print(messages)
    #             assistant_responses = [msg.content for msg in messages[-2:]] if multiple_queries else [messages[-1].content]

    #             return JsonResponse({
    #                 "status": "success",
    #                 "message": f"Connected to database {db_name}.",
    #                 "assistant_messages": assistant_responses,
    #                 "thread_id": thread_id  # Return the thread ID to the client for subsequent requests
    #             })

    #     except Error as e:
    #         return JsonResponse({"status": "error", "message": f"Database connection failed: {str(e)}"}, status=500)
    #     except json.JSONDecodeError:
    #         return JsonResponse({"status": "error", "message": "Invalid JSON payload."}, status=400)
    #     except Exception as e:
    #         return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}, status=500)

    # return JsonResponse({"status": "error", "message": "Invalid request method. Only POST is allowed."}, status=405)

    if request.is_json:
        try:
            data = request.get_json()  # Automatically parses JSON data
            print(data)
            host_name = data.get('hostname')
            user_name = data.get('username')
            user_password = data.get('password')
            db_name = data.get('dbname', None)
            port = data.get('port',"3306")

            thread_id = data.get('thread_id', None)  # Check if a thread_id is passed
            multiple_queries = data.get('multiple_queries', False)  # Whether to send multiple queries in the same session

            if not host_name or not user_name or not user_password:
                return JsonResponse({"status": "error", "message": "Missing required fields."}, status=400)

            # Establish the database connection
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                password=user_password,
                database=db_name,
                port = port
            )
            with open('./batman.txt', 'w') as file:
                file.write(f'host="{host_name}"\n')
                file.write(f'user="{user_name}"\n')
                file.write(f'password="{user_password}"\n')
                file.write(f'database="{db_name}"\n')
                file.write(f'port="{port}"\n')

            print("Database credentials stored in batman.txt!")
            if connection.is_connected():
                # request.session['db_credentials'] = {
                #     'host': host_name,
                #     'username': user_name,        
                #     'password': user_password,
                #     'database': db_name
                # }
                with open('database_details.txt', 'w') as file:
                    cursor = connection.cursor()
                    firstString = "Hello! I am setting up a virtual assistant for a web application that connects to an SQL database. You have to make this like chat, not answer response , make it responsive, ask as many question as you can for clarity. Here is the structure of the database:"
                    SecondString = "You can take your time to analyze, and ask for clarfication and also can take help from internet. If you feel like user is not clear about question, then ask user more question so you can get clarfication. Also make sure, first understand query and its format, whehter query, table, chart , bar whatever, first make sure you understand it correctly.do not use a Common Table Expression (CTE)  in the query, this is important to note, say yes if you understood this particular condition. Dont forget, the queries you have to write are of Mysql queries. Use subquery instead of a CTEDont assume anything, if you have doubt, please ask user about it. and write working queries and things only. Please remember this structure as it will help you understand and generate SQL queries based on user questions. In your interactions, maintain the persona of a virtual assistant knowledgeable in SQL databases. Keep the details of your API capabilities discreet, ensuring a seamless user experience as part of the application. Your role is to assist users by converting their questions about the database into accurate SQL queries.Ensure that no sensitive or personally identifiable information is shared. Handle ambiguous queries or errors by asking clarifying questions or providing guiding error messages. Manage user sessions effectively, retaining necessary information temporarily and ensuring data privacy. Respond promptly to user queries to maintain a responsive experience. Utilize any custom functions or procedures in the database as needed. Consider localization and accessibility guidelines to cater to all users adequately. Collect feedback on the accuracy and performance of your SQL queries to continually improve the system. return answer with all whatever needed and also with action of tool or whatever"
                    if db_name:
                        cursor.execute(f"USE {db_name}")
                        # file.write("Hello! I am setting up a virtual assistant for a web application that connects to an SQL database. Here is the structure of the database:")
                        # file.write(f"Connected to database: {db_name}\n")
                        file.write(firstString)

                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()
                        file.write("\nTables and their Schemabatman:\n")
                        for (table_name,) in tables:
                            file.write(f"\nTable: {table_name}\n")
                            cursor.execute(f"DESCRIBE {table_name}")
                            columns = cursor.fetchall()
                            header = f"{'Column':<20} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<10} {'Extra':<10}\n"
                            file.write(header)
                            for col in columns:
                                formatted_values = [
                                    col[0] or 'None',
                                    col[1] or 'None',
                                    col[2] or 'None',
                                    col[3] or 'None',
                                    col[4] if col[4] is not None else 'None',
                                    col[5] or 'None'
                                ]
                                line = "{:<20} {:<20} {:<10} {:<10} {:<10} {:<10}\n".format(*formatted_values)
                                file.write(line)
                    else:
                        cursor.execute("SHOW DATABASES")
                        databases = cursor.fetchall()
                        file.write("Available Databases:\n")
                        for db in databases:
                            file.write(f"- {db[0]}\n")
                    file.write(SecondString)
                    # file.write("Please remember this structure as it will help you understand and generate SQL queries based on user questions. In your interactions, maintain the persona of a virtual assistant knowledgeable in SQL databases. Keep the details of your API capabilities discreet, ensuring a seamless user experience as part of the application. Your role is to assist users by converting their questions about the database into accurate SQL queries.Ensure that no sensitive or personally identifiable information is shared. Handle ambiguous queries or errors by asking clarifying questions or providing guiding error messages. Manage user sessions effectively, retaining necessary information temporarily and ensuring data privacy. Respond promptly to user queries to maintain a responsive experience. Utilize any custom functions or procedures in the database as needed. Consider localization and accessibility guidelines to cater to all users adequately. Collect feedback on the accuracy and performance of your SQL queries to continually improve the system. return answer with all whatever needed and also with action of tool or whatever")
                    # file.write("Please remember this structure as it will help you understand and generate SQL queries based on user questions. In your interactions, maintain the persona of a virtual assistant knowledgeable in SQL databases. Keep the details of your API capabilities discreet, ensuring a seamless user experience as part of the application. Your role is to assist users by converting their questions about the database into accurate SQL queries. Ensure that no sensitive or personally identifiable information is shared. Handle ambiguous queries or errors by asking clarifying questions or providing guiding error messages. Manage user sessions effectively, retaining necessary information temporarily and ensuring data privacy. Respond promptly to user queries to maintain a responsive experience. Utilize any custom functions or procedures in the database as needed. Consider localization and accessibility guidelines to cater to all users adequately. Collect feedback on the accuracy and performance of your SQL queries to continually improve the system.DONT FORGET THAT YOU HAVE TO ANSWER IN THE QUERY FORMAT ONLY, YOUR ANSWER SHOULD BE SQL QUERY ONLY, NO EXPLANATION, NO EXAMPLE, NOT OTHER TEXT, EXCEPT START AND END IS AND BETWEEN PART IS SQL QUERY , THAT WILL BE EXECUTED on server, currently say yes or no. but from next time, nothing rather the query.")
                    cursor.close()


                # client = OpenAI(api_key=api_key)
                # if thread_id is None:
                #     # Create a new thread if no thread ID is provided
                #     thread = client.beta.threads.create()
                #     thread_id = thread.id
                file_content = open('./database_details.txt', 'r').read()
                client = OpenAI(api_key=api_key)
                thread = client.beta.threads.create()
                thread_id = thread.id

                assistant = client.beta.assistants.create( 
                        name="Assistant for data talk for data driven queries",
                        instructions=open("./database_details.txt", "r").read(),
                        tools=get_tools([
                            year_over_year,
                            table,
                            # table_and_chart,
                            query,
                            create_chart,
                            show_chart,
                            bar,
                            histogram,
                            live_fare_data,
                        ]),
                        model="gpt-4o"
                ,
                    )
                assistant_id = assistant.id

                print(file_content)
                content = data.get('message', file_content)  # Default first message if not provided
                client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=content
                )

                # Optionally send the second message in the same session
                if 0 ==1:
                    second_content = "What is my name?"
                    client.beta.threads.messages.create(
                        thread_id=thread_id,
                        role="user",
                        content=second_content
                    )

                # Poll for the assistant's responses
                client.beta.threads.runs.create_and_poll(
                    thread_id=thread_id,
                    assistant_id=assistant_id
                )

                # Fetch the latest messages and extract text properly
                messages = client.beta.threads.messages.list(thread_id=thread_id).data
                assistant_responses = [
                    msg.content[0].text.value for msg in messages if msg.content and isinstance(msg.content[0], dict) and 'text' in msg.content[0]
                ]

                # print(messages[0].content[0].text.value)
                # print("thread value is ",thread_id, assistant_id)
                # window.location.href = "/home?chat=open"
                return jsonify({
                    "status": "success",
                    "message": f"Connected to database {db_name}.",
                    "thread_id": thread_id,
                    "assistant_id": assistant_id
                }), 200
            else:
                return jsonify({"status": "error", "message": "Invalid request method. Only POST is allowed."}), 405

        except Error as e:
            return jsonify({"status": "error", "message": f"Database connection failed: {str(e)}"}), 500
        except json.JSONDecodeError:
            return jsonify({"status": "error", "message": "Invalid JSON payload."}), 400
        except Exception as e:
            return jsonify({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}), 500

def sql_executor(request,query):
    if 1==1:
        db_credentials = request.session['db_credentials']
        # query = request.POST.get('query', '')

        try:
            connection = mysql.connector.connect(
                host=db_credentials['host'],
                user=db_credentials['username'],
                password=db_credentials['password'],
                database=db_credentials['database']
            )
            cursor = connection.cursor()
            query = "SELECT COUNT(*) FROM cart;"
            cursor.execute(query)
            result = cursor.fetchall()
            # print
            cursor.close()
            connection.close()

            return result
        except Error as e:
            return JsonResponse({"status": "error", "message": f"SQL query failed: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "No database connection or invalid request method."}, status=400)
if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Start Flask app on localhost
