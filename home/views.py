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
from updated_sqlconnector import connect_to_databaseup
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
        return connect_to_databaseup(request)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

def home(request):
    chat_open = request.GET.get('chat', '') == 'open'
    thread_id = request.GET.get('thread_id', None)
    context = {
        'chat_open': chat_open,
        'thread_id': thread_id
    }
    return render(request, 'home.html', context)


def chat_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse the JSON body
        user_message = data.get('message', '')
        thread_id = data.get('threadId')  # Extract the thread_id from the request data

        chat_param = data.get('chatType') 
        print(chat_param,"---------------------------------")
        if(chat_param != "open"):
            thread_id = None
        print(request)
        print("---------------------------------")
        print(request.get_full_path())
        print(request.build_absolute_uri())
        print("USER", user_message)
        message_type, usage_data, response = send_message(user_message,thread_id)
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