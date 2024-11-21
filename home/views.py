# # from django.shortcuts import render
# from django.urls import reverse
# from django.shortcuts import render, HttpResponse
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from chatbot_v2 import send_message
# from django.shortcuts import redirect
# import plotly.io as pio
# from updated_sqlconnector import connect_to_database
# import mysql.connector
# from mysql.connector import Error

# # Create your views here.
# def index(request):
#     return render(request,"index.html")
# from django.shortcuts import render
# import mysql.connector
# from mysql.connector import Error


# def company(request):
#     types = [
#         {"name": "Aviation", "url": reverse("banking")},
#         {"name": "Finance", "url": reverse("fianance")},
#         {"name": "E-commerce", "url": reverse("ecommerse")},
#     ]
#     return render(request, "company.html", {"types": types})

# def aviation(request):
#     return render(request,"aviation.html")

# def fianance(request):
#     return render(request,"finance.html")

# def banking(request):
#     return render(request,"banking.html")

# def ecommerse(request):
#     return render(request,"ecommerse.html")


# def sqlconnector(request):
#     # Render the SQL Connector form
#     return render(request, "sqlconnector.html")

# @csrf_exempt  # Disable CSRF for simplicity; remove this in production and use CSRF tokens
# def connect_to_database(request):
#     if request.method == 'POST':
#         # Parse JSON data from the POST request
#         data = json.loads(request.body)
#         host_name = data.get('hostname')
#         user_name = data.get('username')
#         user_password = data.get('password')
#         db_name = data.get('dbname')

#         try:
#             # Check for missing fields
#             if not host_name or not user_name or not user_password or not db_name:
#                 return JsonResponse({"status": "error", "message": "All fields are required!"}, status=400)

#             # Attempt to connect to the database
#             connection = mysql.connector.connect(
#                 host=host_name,
#                 user=user_name,
#                 passwd=user_password,
#                 database=db_name
#             )

#             # If connection is successful
#             if connection.is_connected():
#                 connection.close()
#                 return JsonResponse({"status": "success", "message": "Database connection successful!"})

#         except Error as e:
#             return JsonResponse({"status": "error", "message": f"Database connection failed: {str(e)}"}, status=500)

#     return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

# def home(request):
#     return render(request,"home.html")

# def chat_view(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)  # Parse the JSON body
#         user_message = data.get('message', '')
#         print("USER", user_message)
#         message_type, usage_data, response = send_message(user_message)
#         if message_type == 'chart':
#             response = pio.to_json(response)
#         if message_type == 'query':
#             response = response.to_json()
#         print("RESPONSE", response)
#         print("message_type", message_type)
#         print("usage_data", usage_data)

#         return JsonResponse({
#                 'response': response,
#                 'message_type' : message_type,
#                 'usage_data':usage_data
#                 })
#     return JsonResponse({'error': 'Invalid request'}, status=400)


# from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from chatbot_v2 import send_message
from django.shortcuts import redirect
import plotly.io as pio
from updated_sqlconnector import connect_to_database
import mysql.connector
from mysql.connector import Error

# Create your views here.
def index(request):
    return render(request,"index.html")
from django.shortcuts import render
import mysql.connector
from mysql.connector import Error


def company(request):
    types = [
        {"name": "Aviation", "url": reverse("banking")},
        {"name": "Finance", "url": reverse("fianance")},
        {"name": "E-commerce", "url": reverse("ecommerse")},
    ]
    return render(request, "company.html", {"types": types})

def aviation(request):
    return render(request,"aviation.html")

def fianance(request):
    return render(request,"finance.html")

def banking(request):
    return render(request,"banking.html")

def ecommerse(request):
    return render(request,"ecommerse.html")


def sqlconnector(request):
    # Render the SQL Connector form
    return render(request, "sqlconnector.html")
@csrf_exempt
def connect_to_database(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        host_name = data.get('hostname')
        user_name = data.get('username')
        user_password = data.get('password')
        db_name = data.get('dbname')  # Assumes database name is sent by the client

        try:
            connection = mysql.connector.connect(
                host=host_name,
                user=user_name,
                passwd=user_password
            )

            if connection.is_connected():
                cursor = connection.cursor()

                if db_name:
                    cursor.execute(f"USE {db_name}")
                    print(f"Connected to database: {db_name}")

                    cursor.execute("SHOW TABLES")
                    tables = cursor.fetchall()
                    print("\nTables and their Schema:")
                    for (table_name,) in tables:
                        print(f"\nTable: {table_name}")
                        cursor.execute(f"DESCRIBE {table_name}")
                        columns = cursor.fetchall()
                        print(f"{'Column':<20} {'Type':<20} {'Null':<10} {'Key':<10} {'Default':<10} {'Extra':<10}")
                        for col in columns:
                            formatted_values = [
                                col[0] or 'None',
                                col[1] or 'None',
                                col[2] or 'None',
                                col[3] or 'None',
                                col[4] if col[4] is not None else 'None',
                                col[5] or 'None'
                            ]
                            print("{:<20} {:<20} {:<10} {:<10} {:<10} {:<10}".format(*formatted_values))
                else:
                    cursor.execute("SHOW DATABASES")
                    databases = cursor.fetchall()
                    print("Available Databases:")
                    for db in databases:
                        print(f"- {db[0]}")

                connection.close()

        except Error as e:
            print(f"Database connection failed: {str(e)}")
            return JsonResponse({"status": "error", "message": f"Database connection failed: {str(e)}"}, status=500)

        return HttpResponse("Check your console for details.")

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


def home(request):
    return render(request,"home.html")

def chat_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse the JSON body
        user_message = data.get('message', '')
        print("USER", user_message)
        message_type, usage_data, response = send_message(user_message)
        if message_type == 'chart':
            response = pio.to_json(response)
        if message_type == 'query':
            response = response.to_json()
        print("RESPONSE", response)
        print("message_type", message_type)
        print("usage_data", usage_data)

        return JsonResponse({
                'response': response,
                'message_type' : message_type,
                'usage_data':usage_data
                })
    return JsonResponse({'error': 'Invalid request'}, status=400)