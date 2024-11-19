# from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from chatbot_v2 import send_message
from django.shortcuts import redirect
import plotly.io as pio

# Create your views here.
def index(request):
    return render(request,"index.html")
from django.shortcuts import render


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