from django.conf import settings
from django.shortcuts import render
import google.generativeai as genai

genai.configure(api_key=settings.GOOGLE_API_KEY) 

def index(request):
    return render(request, 'index.html')

def get_trip_info(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            contents=[
                "You are a helpful travel guide assistant.",
                prompt
            ],
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1000,
            }
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

def travel_ai(request):
    if "chat_history" not in request.session:
        request.session["chat_history"] = []

    if request.method == "POST":
        prompt = request.POST.get("query")
        if prompt:
            # Add user message to chat history
            request.session["chat_history"].append({"role": "user", "content": prompt})

            # Get AI response
            ai_response = get_trip_info(prompt)
            request.session["chat_history"].append({"role": "ai", "content": ai_response})

            request.session.modified = True  # Mark session as changed

    return render(request, "travel_info.html", {"chat_history": request.session.get("chat_history", [])})
