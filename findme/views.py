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

    # Sort by length to replace longer cities first
    for city in sorted(city_list, key=len, reverse=True):
        slug = city.lower().replace(" ", "-")

        # If already linked, skip
        if f'/city-info/{slug}' in text:
            continue

        # Updated regex to match whole word only using word boundaries (\b)
        pattern = rf'\b{re.escape(city)}\b'

        link = (
            f'<a href="/city-info/{slug}/" '
            f'class="badge rounded-pill bg-primary text-white text-decoration-none me-1">'
            f' ⚲ {city} ✅ </a>'
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
                "parts": [  # This is the one-time system prompt
                    """
                    You are a professional and friendly travel assistant Named "WishTravel" .gretting them by your name first, make your name bold and then give a new line after that help him. The user may ask general or specific travel questions.

                    If they provide no location, season, or budget dont mention it that they dont provide it,just  assume  best and most visiting places :
                    - They are traveling from New York or London
                    - They want a moderate-budget, fun trip
                    - They prefer 5-7 day trips

                    Always give answers in Markdown format, with:
                    ✅ Emoji for each section
                    ✅ Bold section titles
                    ✅ Skimmable layout (no long paragraphs)
                    ✅ Bullet points for attractions, hotels, and tips
                    ✅ Optional day-wise itinerary when applicable
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

        ai_reply = highlight_city_links(ai_reply)
        request.session["chat_history"].append({"role": "model", "content": ai_reply})
        request.session.modified = True

    return render(request, "travel_info.html", {
        "chat_history": request.session.get("chat_history", []),
    })


@csrf_exempt
def clear_chat(request):
    request.session.flush()
    return redirect("travel_ai")
