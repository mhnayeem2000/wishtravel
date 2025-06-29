from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import re
import os

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

def index(request):
    return render(request, 'index.html')
def highlight_city_links(text):
    try:
        with open('city.csv', mode='r', encoding='utf-8') as file:
            city_list = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        city_list = ['Sydney', 'Melbourne', 'Perth']

    for city in sorted(city_list, key=len, reverse=True):
        slug = city.lower().replace(" ", "-")

        # Skip if already linked
        if f'/city-info/{slug}' in text:
            continue

        pattern = rf'\b{re.escape(city)}\b'

        link = (
            f'<a href="/city-info/{slug}/" '
            f'class="city-chip">📍 {city} ✅ <i class="bi bi-chat-left-text"> </a>'
        )


        text = re.sub(pattern, link, text)

    return text



def travel_ai(request):
    if "chat_history" not in request.session:
        request.session["chat_history"] = []

    if request.method == "POST":
        user_input = request.POST.get("query")

        # Append only user's message to history
        request.session["chat_history"].append({"role": "user", "content": user_input})

        # Prepare full message list for Gemini
        gemini_messages = [
            {
                "role": "model",
                "parts": [
                    """
        You are **WishTravel**, a professional and friendly AI travel assistant.

        When a user asks for help, first greet them by your name (e.g., "Hello! I'm **WishTravel**, your travel assistant.") and then begin planning the trip.

        If the user doesn't mention destination, season, or budget, assume:
        - Departure from Bangladesh
        - Moderate-budget
        - 5–7 day trip
        - Fun and culturally rich

        🎯 Your goals:
        - Suggest **real places**: hotels, restaurants, landmarks, cafés, neighborhoods
        - Give **detailed, day-wise itinerary** for 5–7 days
        - Mention **real restaurant names** for lunch and dinner (e.g., "Joe's Pizza", "Becco", etc.)
        - Include **specific hotels** for staying (e.g., "Rove Downtown", "Premier Inn")
        - Mention **popular parks, malls, museums, or districts** if applicable

        📋 Format rules:
        - Use **Markdown** (headings, bold, bullet lists)
        - Add ✅ emoji for each section
        - Add Emoji for each Suggestion (e.g., 🏨 for hotels, 🍽️ for food , for park )
        - Use clear section headers: **Destination**, **Things to Do**, **Hotels**, **Food**, **Day-wise Itinerary**, **Travel Tips**
        - Use inline links or badges for cities if mentioned (e.g., ⚲ Dubai ✅)

        Avoid generic phrases — use real examples from the travel industry.

        Keep your tone warm, helpful, and friendly.
                    """
                ]
            }
        ]


        # Add previous chat turns
        for msg in request.session["chat_history"]:
            gemini_messages.append({
                "role": msg["role"],
                "parts": [msg["content"]]
            })

        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(
                contents=gemini_messages,
                generation_config={"temperature": 0.7, "max_output_tokens": 2000},
            )
            ai_reply = response.text
        except Exception as e:
            ai_reply = f"Error: {e}"

        ai_reply = response.text
        ai_reply = highlight_city_links(ai_reply)  # injects HTML, then passes through markdownify

        request.session["chat_history"].append({"role": "model", "content": ai_reply})
        request.session.modified = True

    return render(request, "travel_info.html", {
        "chat_history": request.session.get("chat_history", []),
    })


@csrf_exempt
def clear_chat(request):
    request.session.flush()
    return redirect("travel_ai")
