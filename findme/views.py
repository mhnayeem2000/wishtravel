import openai
from django.conf import settings
from django.shortcuts import render
import os
from dotenv import load_dotenv
from openai import OpenAI

def index(request):
    return render(request, 'index.html')


load_dotenv()  # Load .env file

client = OpenAI() 


def get_trip_info(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel guide assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def travel_ai(request):
    response = None
    if request.method == "POST":
        prompt = request.POST.get("query")
        if prompt:
            response = get_trip_info(prompt)
    
    return render(request, "travel_info.html", {"response": response})
