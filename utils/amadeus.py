import requests
from django.conf import settings

def get_amadeus_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    payload = {
        'grant_type': 'client_credentials',
        'client_id': settings.AMADEUS_API_KEY,
        'client_secret': settings.AMADEUS_API_SECRET,
    }
    response = requests.post(url, data=payload)
    return response.json().get('access_token')

def get_hotels(city_code):
    token = get_amadeus_access_token()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://test.api.amadeus.com/v2/shopping/hotel-offers?cityCode={city_code}"
    response = requests.get(url, headers=headers)
    return response.json()

def get_city_code(city_name):
    token = get_amadeus_access_token()
    headers = { "Authorization": f"Bearer {token}" }
    url = f"https://test.api.amadeus.com/v1/reference-data/locations?keyword={city_name}&subType=CITY"
    response = requests.get(url, headers=headers)
    data = response.json()
    try:
        return data['data'][0]['iataCode']  # e.g., 'PAR' for Paris
    except (KeyError, IndexError):
        return None
