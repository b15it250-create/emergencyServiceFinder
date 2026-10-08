import os
import requests
from dotenv import load_dotenv

load_dotenv()

def geocode_location(place):
    user_agent = os.getenv("NOMINATIM_USER_AGENT","ResQNearAI-Hackathon-Demo")
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q":place,"format":"json","limit":1},
            headers={"User-Agent":user_agent},
            timeout=20
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return {
            "lat": float(data[0]["lat"]),
            "lon": float(data[0]["lon"]),
            "display_name": data[0]["display_name"]
        }
    except Exception:
        return None

def fetch_osm_services(lat, lon, radius_km=10):
    enabled = os.getenv("ENABLE_ONLINE_OSM_LOOKUP","true").lower() == "true"
    if not enabled:
        return []

    overpass_url = os.getenv("OVERPASS_URL","https://overpass-api.de/api/interpreter")
    radius_m = int(radius_km * 1000)

    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
      node["amenity"="police"](around:{radius_m},{lat},{lon});
      way["amenity"="police"](around:{radius_m},{lat},{lon});
      node["amenity"="fire_station"](around:{radius_m},{lat},{lon});
      way["amenity"="fire_station"](around:{radius_m},{lat},{lon});
      node["healthcare"="blood_donation"](around:{radius_m},{lat},{lon});
      way["healthcare"="blood_donation"](around:{radius_m},{lat},{lon});
      node["emergency"="ambulance_station"](around:{radius_m},{lat},{lon});
      way["emergency"="ambulance_station"](around:{radius_m},{lat},{lon});
    );
    out center tags;
    """

    try:
        r = requests.post(
            overpass_url,
            data={"data":query},
            timeout=30
        )
        r.raise_for_status()
        elements = r.json().get("elements", [])
    except Exception:
        return []

    results = []

    for item in elements:
        tags = item.get("tags", {})
        lat_v = item.get("lat") or item.get("center", {}).get("lat")
        lon_v = item.get("lon") or item.get("center", {}).get("lon")

        if lat_v is None or lon_v is None:
            continue

        amenity = tags.get("amenity","")
        emergency = tags.get("emergency","")
        healthcare = tags.get("healthcare","")

        if amenity == "hospital":
            category = "Hospital"
        elif amenity == "police":
            category = "Police"
        elif amenity == "fire_station":
            category = "Fire Station"
        elif emergency == "ambulance_station":
            category = "Ambulance"
        elif healthcare == "blood_donation":
            category = "Blood Bank"
        else:
            category = "Other"

        phone = (
            tags.get("contact:phone")
            or tags.get("phone")
            or tags.get("contact:mobile")
            or ""
        )

        address_parts = [
            tags.get("addr:housenumber",""),
            tags.get("addr:street",""),
            tags.get("addr:suburb",""),
            tags.get("addr:city","")
        ]

        address = " ".join([x for x in address_parts if x]).strip()
        if not address:
            address = tags.get("description","OpenStreetMap location")

        results.append({
            "name": tags.get("name", f"Unnamed {category}"),
            "category": category,
            "address": address,
            "area": tags.get("addr:suburb",""),
            "phone": phone,
            "alternate_phone": "",
            "lat": float(lat_v),
            "lon": float(lon_v),
            "open_24x7": 1 if tags.get("opening_hours") == "24/7" else 0,
            "verified": 0,
            "source": "OpenStreetMap"
        })

    return results

SYSTEM_PROMPT = """
You are ResQNear AI, an emergency-service navigation assistant.
Give concise, safety-first guidance. For immediate danger, tell the user
to contact the local emergency number and move to safety when appropriate.
Do not invent phone numbers or claim that an unverified listing is verified.
"""

def rule_based_answer(question, emergency_number):
    q = question.lower()

    if "fire" in q:
        return f"If there is an active fire, call emergency services immediately ({emergency_number} where applicable), evacuate safely, stay low in smoke, and do not re-enter the building."
    if "accident" in q or "injury" in q:
        return f"For a serious accident, call emergency services ({emergency_number} where applicable), share the exact location, number of injured people, and any immediate hazards."
    if "police" in q:
        return f"For an immediate safety threat, contact emergency services ({emergency_number} where applicable) or the nearest verified police station."
    if "hospital" in q or "ambulance" in q:
        return f"For a life-threatening medical emergency, call emergency services ({emergency_number} where applicable) and use the locator to find the nearest hospital or ambulance service."

    return f"For immediate danger, contact emergency services ({emergency_number} where applicable). Use the locator to find the nearest verified service and confirm the phone number before relying on it."

def ask_ai(question, context="", emergency_number="112"):
    key = os.getenv("GROQ_API_KEY","").strip()
    model = os.getenv("GROQ_MODEL","llama-3.1-8b-instant").strip()

    if not key:
        return rule_based_answer(question, emergency_number), "Rule-based emergency advisor"

    try:
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization":f"Bearer {key}",
                "Content-Type":"application/json"
            },
            json={
                "model":model,
                "messages":[
                    {"role":"system","content":SYSTEM_PROMPT},
                    {"role":"user","content":f"Context:\n{context}\n\nQuestion:\n{question}"}
                ],
                "temperature":0.15,
                "max_tokens":400
            },
            timeout=25
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"], f"AI mode: {model}"
    except Exception:
        return rule_based_answer(question, emergency_number), "Fallback emergency advisor"
