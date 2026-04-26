import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

allowed_origins = [
    "https://final-year-project-rho-green.vercel.app",
    "http://localhost:3000",
]

CORS(
    app,
    resources={r"/*": {"origins": allowed_origins}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

DATA_FILE = Path(__file__).with_name("users.json")
trips = []

BUDGET_MULTIPLIERS = {
    "low": 0.75,
    "medium": 1.0,
    "high": 1.8,
}

BUDGET_LABELS = {
    "low": "Budget",
    "medium": "Comfort",
    "high": "Premium",
}

DESTINATION_ALIASES = {
    "mysuru": "mysore",
    "bengaluru": "bangalore",
    "bombay": "mumbai",
    "delhi ncr": "delhi",
    "new delhi": "delhi",
    "hubballi": "hubli",
}

WIKIPEDIA_TITLES = {
    "goa travel": "Goa",
    "baga beach goa": "Baga, Goa",
    "fort aguada goa": "Fort Aguada",
    "basilica of bom jesus goa": "Basilica of Bom Jesus",
    "jaipur travel": "Jaipur",
    "amber fort jaipur": "Amer Fort",
    "hawa mahal jaipur": "Hawa Mahal",
    "city palace jaipur": "City Palace, Jaipur",
    "manali travel": "Manali, Himachal Pradesh",
    "solang valley manali": "Solang Valley",
    "hadimba temple manali": "Hidimba Devi Temple",
    "old manali": "Manali, Himachal Pradesh",
    "dharwad travel": "Dharwad",
    "dharwad fort": "Dharwad",
    "sadhankeri park dharwad": "Sadhankeri",
    "delhi travel": "Delhi",
    "red fort delhi": "Red Fort",
    "india gate delhi": "India Gate",
    "qutub minar delhi": "Qutb Minar",
    "mumbai travel": "Mumbai",
    "gateway of india mumbai": "Gateway of India",
    "marine drive mumbai": "Marine Drive, Mumbai",
    "elephanta caves mumbai": "Elephanta Caves",
    "bangalore travel": "Bangalore",
    "lalbagh botanical garden bangalore": "Lal Bagh",
    "bangalore palace": "Bangalore Palace",
    "cubbon park bangalore": "Cubbon Park",
    "ahmedabad travel": "Ahmedabad",
    "sabarmati ashram ahmedabad": "Sabarmati Ashram",
    "adalaj stepwell ahmedabad": "Adalaj Stepwell",
    "kankaria lake ahmedabad": "Kankaria Lake",
    "mysore travel": "Mysore",
    "mysuru travel": "Mysore",
    "mysore palace": "Mysore Palace",
    "chamundi hills mysore": "Chamundi Hills",
    "brindavan gardens mysore": "Brindavan Gardens",
    "hubli travel": "Hubli",
    "unkal lake hubli": "Unkal Lake",
    "nrupatunga betta hubli": "Nrupatunga Betta",
    "chandramouleshwara temple hubli": "Chandramouleshwara Temple, Hubli",
    "punjab travel": "Punjab, India",
    "golden temple amritsar": "Golden Temple",
    "jallianwala bagh amritsar": "Jallianwala Bagh",
    "wagah border": "Wagah",
}

PHOTO_LIBRARY = {
    "goa travel": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "baga beach goa": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=80",
    "fort aguada goa": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=80",
    "basilica of bom jesus goa": "https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?auto=format&fit=crop&w=1200&q=80",
    "jaipur travel": "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&w=1200&q=80",
    "amber fort jaipur": "https://images.unsplash.com/photo-1599661046289-e31897846e41?auto=format&fit=crop&w=1200&q=80",
    "hawa mahal jaipur": "https://images.unsplash.com/photo-1599661046827-dacde6976549?auto=format&fit=crop&w=1200&q=80",
    "city palace jaipur": "https://images.unsplash.com/photo-1548013146-72479768bada?auto=format&fit=crop&w=1200&q=80",
    "mysore travel": "https://commons.wikimedia.org/wiki/Special:FilePath/Mysore%20palace%2C%20karnataka.jpg",
    "mysuru travel": "https://commons.wikimedia.org/wiki/Special:FilePath/Mysore%20palace%2C%20karnataka.jpg",
    "mysore palace": "https://commons.wikimedia.org/wiki/Special:FilePath/Mysore%20palace%2C%20karnataka.jpg",
    "chamundi hills mysore": "https://commons.wikimedia.org/wiki/Special:FilePath/Chamundi%20Hills%20%285285108365%29.jpg",
    "brindavan gardens mysore": "https://commons.wikimedia.org/wiki/Special:FilePath/Brindavan%20Gardens%20%2810327386854%29.jpg",
    "manali travel": "https://images.unsplash.com/photo-1521295121783-8a321d551ad2?auto=format&fit=crop&w=1200&q=80",
    "solang valley manali": "https://images.unsplash.com/photo-1518002054494-3a6f94352e9d?auto=format&fit=crop&w=1200&q=80",
    "hadimba temple manali": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=1200&q=80",
    "old manali": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1200&q=80",
    "dharwad travel": "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?auto=format&fit=crop&w=1200&q=80",
    "dharwad fort": "https://images.unsplash.com/photo-1516483638261-f4dbaf036963?auto=format&fit=crop&w=1200&q=80",
    "sadhankeri park dharwad": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=80",
    "delhi travel": "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=1200&q=80",
    "red fort delhi": "https://images.unsplash.com/photo-1597040663342-45b6af3d91a5?auto=format&fit=crop&w=1200&q=80",
    "india gate delhi": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80",
    "qutub minar delhi": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=1200&q=80",
    "mumbai travel": "https://images.unsplash.com/photo-1526481280695-3c4691f9d1c6?auto=format&fit=crop&w=1200&q=80",
    "gateway of india mumbai": "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?auto=format&fit=crop&w=1200&q=80",
    "marine drive mumbai": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=80",
    "elephanta caves mumbai": "https://images.unsplash.com/photo-1514222134-b57cbb8ce073?auto=format&fit=crop&w=1200&q=80",
    "bangalore travel": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=1200&q=80",
    "lalbagh botanical garden bangalore": "https://images.unsplash.com/photo-1588416499018-d0dd514db4b7?auto=format&fit=crop&w=1200&q=80",
    "bangalore palace": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?auto=format&fit=crop&w=1200&q=80",
    "cubbon park bangalore": "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?auto=format&fit=crop&w=1200&q=80",
    "punjab travel": "https://images.unsplash.com/photo-1585136917238-5d6fc4b7e9df?auto=format&fit=crop&w=1200&q=80",
    "golden temple amritsar": "https://images.unsplash.com/photo-1585136917238-5d6fc4b7e9df?auto=format&fit=crop&w=1200&q=80",
    "jallianwala bagh amritsar": "https://images.unsplash.com/photo-1561361058-c24cecae35ca?auto=format&fit=crop&w=1200&q=80",
    "wagah border": "https://images.unsplash.com/photo-1514222134-b57cbb8ce073?auto=format&fit=crop&w=1200&q=80",
    "default": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?auto=format&fit=crop&w=1200&q=80",
}

PHOTO_CACHE = {}


def wikipedia_image_url(query):
    normalized_query = str(query or "").strip().lower()
    title = WIKIPEDIA_TITLES.get(normalized_query)

    if not title:
        return None

    if title in PHOTO_CACHE:
        return PHOTO_CACHE[title]

    endpoint = (
        "https://en.wikipedia.org/api/rest_v1/page/summary/"
        f"{quote(title.replace(' ', '_'))}"
    )

    try:
        request = Request(
            endpoint,
            headers={
                "Accept": "application/json",
                "User-Agent": "TravelBuddy/1.0 (travel planner project)",
            },
        )
        with urlopen(request, timeout=4) as response:
            payload = json.loads(response.read().decode("utf-8"))

        image_url = (
            payload.get("originalimage", {}).get("source")
            or payload.get("thumbnail", {}).get("source")
        )
        PHOTO_CACHE[title] = image_url
        return image_url
    except Exception:
        PHOTO_CACHE[title] = None
        return None


def photo_url(query):
    normalized_query = str(query or "").strip().lower()
    wikipedia_photo = wikipedia_image_url(normalized_query)

    if wikipedia_photo:
        return wikipedia_photo

    if normalized_query in PHOTO_LIBRARY:
        return PHOTO_LIBRARY[normalized_query]

    # Give unknown cities/places a stable but distinct fallback image per query
    return f"https://picsum.photos/seed/{quote(normalized_query or 'travel-buddy')}/1200/800"

DESTINATION_DATA = {
    "goa": {
        "hotels": [
            {"name": "Calangute Beach Stay", "base_price": 2200},
            {"name": "Anjuna Coast Resort", "base_price": 3200},
            {"name": "Panjim Harbor Hotel", "base_price": 4200},
            {"name": "Candolim Sunset Suites", "base_price": 5200},
            {"name": "Morjim Palm Retreat", "base_price": 6200},
        ],
        "restaurants": [
            "Fisherman's Wharf",
            "Pousada by the Beach",
            "Mum's Kitchen",
            "Gunpowder Goa",
            "Thalassa",
        ],
        "activities": [
            "Relax at the beach and enjoy a sunset walk",
            "Visit a Portuguese heritage street and local cafes",
            "Take an evening cruise with live music",
            "Explore flea markets and coastal viewpoints",
            "Keep one half-day for water sports or a quiet beach hop",
        ],
        "famous_places": [
            {"name": "Baga Beach", "description": "Popular beach with water sports.", "image": photo_url("Baga Beach Goa"), "best_time": "Late afternoon", "visit_time": "2-3 hours"},
            {"name": "Fort Aguada", "description": "Historic fort with sea views.", "image": photo_url("Fort Aguada Goa"), "best_time": "Sunset", "visit_time": "1-2 hours"},
            {"name": "Basilica of Bom Jesus", "description": "UNESCO World Heritage church.", "image": photo_url("Basilica of Bom Jesus Goa"), "best_time": "Morning", "visit_time": "1 hour"}
        ],
        "transport": [
            "Rent a scooter or bike for local travel.",
            "Taxis and auto-rickshaws are widely available.",
            "Public buses connect major beaches and towns."
        ],
    },
    "jaipur": {
        "hotels": [
            {"name": "Pink City Haveli", "base_price": 2100},
            {"name": "Amber Courtyard Inn", "base_price": 3000},
            {"name": "Raj Mahal Residency", "base_price": 4100},
            {"name": "City Palace View Hotel", "base_price": 5200},
            {"name": "Nahargarh Heritage Retreat", "base_price": 6400},
        ],
        "restaurants": [
            "Spice Court",
            "Rawat Mishthan Bhandar",
            "Bar Palladio",
            "Laxmi Misthan Bhandar",
            "Tapri Central",
        ],
        "activities": [
            "Start with Amber Fort and city viewpoints",
            "Explore bazaars for handicrafts and textiles",
            "Spend the evening at a rooftop restaurant",
            "Visit heritage courtyards and photo spots",
            "Keep one block for shopping and local sweets",
        ],
        "famous_places": [
            {"name": "Amber Fort", "description": "Majestic fort with city views.", "image": photo_url("Amber Fort Jaipur"), "best_time": "Morning", "visit_time": "2-3 hours"},
            {"name": "Hawa Mahal", "description": "Iconic palace with unique windows.", "image": photo_url("Hawa Mahal Jaipur"), "best_time": "Sunrise", "visit_time": "45-60 mins"},
            {"name": "City Palace", "description": "Royal residence and museum.", "image": photo_url("City Palace Jaipur"), "best_time": "Late morning", "visit_time": "1-2 hours"}
        ],
        "transport": [
            "Auto-rickshaws and cabs are common.",
            "City buses connect major attractions.",
            "Cycle rickshaws for short distances."
        ],
    },
    "manali": {
        "hotels": [
            {"name": "Pine Trail Lodge", "base_price": 2000},
            {"name": "Old Manali Valley Stay", "base_price": 3100},
            {"name": "Snow Peak Retreat", "base_price": 4300},
            {"name": "Beas River Resort", "base_price": 5600},
            {"name": "Solang Heights Hotel", "base_price": 6900},
        ],
        "restaurants": [
            "Johnson's Cafe",
            "Cafe 1947",
            "The Lazy Dog",
            "Chopsticks Manali",
            "Drifters' Cafe",
        ],
        "activities": [
            "Visit mountain viewpoints and pine trails",
            "Explore Old Manali cafes and local shops",
            "Keep the evening for a bonfire-style dinner",
            "Add a scenic river walk and slow photography stop",
            "Reserve time for nearby adventure activities",
        ],
        "famous_places": [
            {"name": "Solang Valley", "description": "Adventure sports and snow.", "image": photo_url("Solang Valley Manali"), "best_time": "Morning", "visit_time": "Half day"},
            {"name": "Hadimba Temple", "description": "Ancient temple in cedar forest.", "image": photo_url("Hadimba Temple Manali"), "best_time": "Morning", "visit_time": "1 hour"},
            {"name": "Old Manali", "description": "Charming village with cafes.", "image": photo_url("Old Manali"), "best_time": "Evening", "visit_time": "2-3 hours"}
        ],
        "transport": [
            "Taxis and private cars for sightseeing.",
            "Local buses to nearby towns.",
            "Bike rentals for adventure."
        ],
    },
    "dharwad": {
        "hotels": [
            {"name": "Dharwad Comfort Inn", "base_price": 1800},
            {"name": "Hubli-Dharwad Residency", "base_price": 2600},
            {"name": "Kittur Heritage Stay", "base_price": 3600},
            {"name": "Green Campus Hotel", "base_price": 4300},
            {"name": "North Karnataka Retreat", "base_price": 5200},
        ],
        "restaurants": [
            "Dharwad Tiffin Corner",
            "North Karnataka Oota House",
            "Basaveshwar Khanavali",
            "Campus Cafe",
            "Malnad Spice Table",
        ],
        "activities": [
            "Visit local heritage spots and explore calm neighborhood streets",
            "Spend time in green campus areas and try popular Dharwad snacks",
            "Wrap up the day with a relaxed evening at a well-known local cafe",
            "Explore bookstores, markets, and everyday city culture",
            "Keep one half-day for nearby viewpoints or a local food trail",
        ],
        "famous_places": [
            {"name": "Dharwad Fort", "description": "Historic fort in the city.", "image": photo_url("Dharwad Fort"), "best_time": "Morning", "visit_time": "1 hour"},
            {"name": "Sadhankeri Park", "description": "Popular park with lake.", "image": photo_url("Sadhankeri Park Dharwad"), "best_time": "Evening", "visit_time": "1-2 hours"}
        ],
        "transport": [
            "Auto-rickshaws and city buses.",
            "Cabs for intercity travel."
        ],
    },
    "delhi": {
        "hotels": [
            {"name": "Connaught Comfort Hotel", "base_price": 2400},
            {"name": "Karol Bagh Residency", "base_price": 3200},
            {"name": "India Gate View Stay", "base_price": 4500},
            {"name": "Aerocity Metro Suites", "base_price": 5600},
            {"name": "Capital Luxe Hotel", "base_price": 7200},
        ],
        "restaurants": [
            "Saravana Bhavan",
            "Karim's",
            "Indian Accent",
            "Cafe Lota",
            "Bukhara",
        ],
        "activities": [
            "Start with a major monument and a walk through a historic district",
            "Visit markets for street food and shopping",
            "Plan an evening around lights, food, and city views",
            "Explore museums or cultural centers in the afternoon",
            "Keep one slot for old and new city contrast photography",
        ],
        "famous_places": [
            {"name": "Red Fort", "description": "Iconic Mughal fort.", "image": photo_url("Red Fort Delhi"), "best_time": "Morning", "visit_time": "2 hours"},
            {"name": "India Gate", "description": "War memorial and park.", "image": photo_url("India Gate Delhi"), "best_time": "Evening", "visit_time": "45 mins"},
            {"name": "Qutub Minar", "description": "Tallest brick minaret.", "image": photo_url("Qutub Minar Delhi"), "best_time": "Morning", "visit_time": "1-2 hours"}
        ],
        "transport": [
            "Delhi Metro for fast travel.",
            "Auto-rickshaws and cabs.",
            "City buses for budget travel."
        ],
    },
    "mumbai": {
        "hotels": [
            {"name": "Marine Drive Stay", "base_price": 2500},
            {"name": "Colaba Harbor Inn", "base_price": 3500},
            {"name": "Bandra City Suites", "base_price": 4700},
            {"name": "Juhu Palm Residency", "base_price": 5900},
            {"name": "Skyline Bay Hotel", "base_price": 7600},
        ],
        "restaurants": [
            "Leopold Cafe",
            "Bademiya",
            "The Table",
            "Britannia & Co.",
            "Khyber",
        ],
        "activities": [
            "See the waterfront and iconic city landmarks",
            "Explore art, shopping, and neighborhood cafes",
            "End the day with sea-facing dinner plans",
            "Keep time for local train-accessible city highlights",
            "Add a sunset stop and a late-evening food trail",
        ],
        "famous_places": [
            {"name": "Gateway of India", "description": "Historic arch monument.", "image": photo_url("Gateway of India Mumbai"), "best_time": "Morning", "visit_time": "1 hour"},
            {"name": "Marine Drive", "description": "Scenic seaside promenade.", "image": photo_url("Marine Drive Mumbai"), "best_time": "Sunset", "visit_time": "1-2 hours"},
            {"name": "Elephanta Caves", "description": "Ancient cave temples.", "image": photo_url("Elephanta Caves Mumbai"), "best_time": "Morning", "visit_time": "Half day"}
        ],
        "transport": [
            "Mumbai local trains for city travel.",
            "Cabs and auto-rickshaws.",
            "Ferries to Elephanta Caves."
        ],
    },
    "bangalore": {
        "hotels": [
            {"name": "Garden City Inn", "base_price": 2300},
            {"name": "Indiranagar Suites", "base_price": 3300},
            {"name": "MG Road Residency", "base_price": 4300},
            {"name": "Cubbon Park Hotel", "base_price": 5400},
            {"name": "Skydeck Premium Stay", "base_price": 6800},
        ],
        "restaurants": [
            "MTR",
            "Toit",
            "Vidyarthi Bhavan",
            "CTR",
            "The Only Place",
        ],
        "activities": [
            "Visit gardens and a popular city landmark",
            "Explore cafes, bookstores, and tech district hangouts",
            "Spend the evening in a lively food street or brewery area",
            "Reserve one block for parks and slow city walks",
            "Keep a flexible slot for shopping and coffee stops",
        ],
        "famous_places": [
            {"name": "Lalbagh Botanical Garden", "description": "Famous botanical garden.", "image": photo_url("Lalbagh Botanical Garden Bangalore"), "best_time": "Morning", "visit_time": "1-2 hours"},
            {"name": "Bangalore Palace", "description": "Royal palace with gardens.", "image": photo_url("Bangalore Palace"), "best_time": "Late morning", "visit_time": "1 hour"},
            {"name": "Cubbon Park", "description": "Large city park.", "image": photo_url("Cubbon Park Bangalore"), "best_time": "Early morning", "visit_time": "1-2 hours"}
        ],
        "transport": [
            "Metro and city buses.",
            "Auto-rickshaws and cabs."
        ],
    },
    "ahmedabad": {
        "hotels": [
            {"name": "Sabarmati Riverside Stay", "base_price": 2200},
            {"name": "Law Garden Residency", "base_price": 3200},
            {"name": "CG Road Comfort Hotel", "base_price": 4300},
            {"name": "Heritage Pol Courtyard", "base_price": 5500},
            {"name": "Riverfront Grand Suites", "base_price": 6800},
        ],
        "restaurants": [
            "Agashiye",
            "Gordhan Thal",
            "Swati Snacks",
            "The Green House",
            "Manek Chowk Food Market",
        ],
        "activities": [
            "Start with the riverfront and a heritage walk through the old city",
            "Visit museums, stepwells, and iconic city landmarks",
            "Keep the evening for street food and market exploration",
            "Reserve time for architecture photography and local shopping",
            "Add one relaxed cultural stop and a cafe break",
        ],
        "famous_places": [
            {"name": "Sabarmati Ashram", "description": "Historic residence of Mahatma Gandhi on the riverbank.", "image": photo_url("Sabarmati Ashram Ahmedabad"), "best_time": "Morning", "visit_time": "1-2 hours"},
            {"name": "Adalaj Stepwell", "description": "Intricately carved stepwell just outside the city.", "image": photo_url("Adalaj Stepwell Ahmedabad"), "best_time": "Morning", "visit_time": "1 hour"},
            {"name": "Kankaria Lake", "description": "Popular waterfront destination with family attractions and evening views.", "image": photo_url("Kankaria Lake Ahmedabad"), "best_time": "Evening", "visit_time": "2 hours"},
        ],
        "transport": [
            "Use BRTS buses and metro for affordable city travel.",
            "App cabs and auto-rickshaws are convenient for sightseeing.",
            "Old city areas are best covered partly on foot."
        ],
    },
    "mysore": {
        "hotels": [
            {"name": "Mysore Palace View Inn", "base_price": 2100},
            {"name": "Chamundi Comfort Stay", "base_price": 3100},
            {"name": "Devaraja Market Residency", "base_price": 4200},
            {"name": "Royal Heritage Courtyard", "base_price": 5400},
            {"name": "Brindavan Premium Retreat", "base_price": 6700},
        ],
        "restaurants": [
            "RRR Restaurant",
            "Mylari",
            "Vinayaka Mylari",
            "The Old House",
            "Mahesh Prasad",
        ],
        "activities": [
            "Begin with Mysore Palace and the nearby heritage district",
            "Explore markets, museums, and sandalwood or silk shopping areas",
            "Reserve sunset hours for gardens or a hill viewpoint",
            "Keep one block for local food and slow city walks",
            "Add a cultural stop with photography-friendly architecture",
        ],
        "famous_places": [
            {"name": "Mysore Palace", "description": "Grand royal palace known for its architecture and evening illumination.", "image": photo_url("Mysore Palace"), "best_time": "Evening", "visit_time": "1-2 hours"},
            {"name": "Chamundi Hills", "description": "Hilltop temple and viewpoint overlooking the city.", "image": photo_url("Chamundi Hills Mysore"), "best_time": "Early morning", "visit_time": "2 hours"},
            {"name": "Brindavan Gardens", "description": "Famous terraced gardens with musical fountain shows.", "image": photo_url("Brindavan Gardens Mysore"), "best_time": "Evening", "visit_time": "2-3 hours"},
        ],
        "transport": [
            "Auto-rickshaws and cabs work well for palace-area sightseeing.",
            "City buses connect major attractions at low cost.",
            "Chamundi Hills is easiest by cab or private vehicle."
        ],
    },
    "hubli": {
        "hotels": [
            {"name": "Hubli Central Stay", "base_price": 1900},
            {"name": "Unkal Lake Residency", "base_price": 2800},
            {"name": "Railway Junction Hotel", "base_price": 3600},
            {"name": "Twin City Comfort Suites", "base_price": 4700},
            {"name": "North Karnataka Premium Inn", "base_price": 5900},
        ],
        "restaurants": [
            "Basaveshwar Khanavali",
            "The Sigdi",
            "Kamat Restaurant",
            "Gokul Veg",
            "Shree Renuka Restaurant",
        ],
        "activities": [
            "Visit the city lake area and relax at popular local hangouts",
            "Explore temples, gardens, and everyday city culture",
            "Keep the evening free for local North Karnataka food",
            "Add one nearby historical or spiritual landmark stop",
            "Reserve time for markets and a relaxed city drive",
        ],
        "famous_places": [
            {"name": "Unkal Lake", "description": "Well-known lake and leisure spot in Hubli.", "image": photo_url("Unkal Lake Hubli"), "best_time": "Evening", "visit_time": "1-2 hours"},
            {"name": "Nrupatunga Betta", "description": "Hill viewpoint offering city panoramas and open space.", "image": photo_url("Nrupatunga Betta Hubli"), "best_time": "Sunset", "visit_time": "1 hour"},
            {"name": "Chandramouleshwara Temple", "description": "Historic temple admired for its stone architecture.", "image": photo_url("Chandramouleshwara Temple Hubli"), "best_time": "Morning", "visit_time": "45-60 mins"},
        ],
        "transport": [
            "Auto-rickshaws are the easiest way to move within Hubli.",
            "Cabs are useful for covering Hubli-Dharwad and nearby spots.",
            "Local buses are available for budget travel between key areas."
        ],
    },
    "punjab": {
        "hotels": [
            {"name": "Amritsar Heritage Inn", "base_price": 2100},
            {"name": "Ludhiana Grand Stay", "base_price": 3200},
            {"name": "Patiala Palace Residency", "base_price": 4300},
            {"name": "Punjab Courtyard Hotel", "base_price": 5400},
            {"name": "Golden Fields Retreat", "base_price": 6700},
        ],
        "restaurants": [
            "Kesar Da Dhaba",
            "Bharawan Da Dhaba",
            "Brothers Dhaba",
            "Pal Dhaba",
            "Kulcha Land",
        ],
        "activities": [
            "Begin with the best-known attractions and landmarks in Punjab",
            "Explore local food spots, shopping streets, and culture in Punjab",
            "Keep the evening free for scenic views, relaxed dining, and photos in Punjab",
            "Reserve time for local markets, sweets, and street photography",
            "Add a flexible stop for heritage, music, or a food trail",
        ],
        "famous_places": [
            {"name": "Golden Temple", "description": "Sacred Sikh shrine.", "image": photo_url("Golden Temple Amritsar"), "best_time": "Early morning", "visit_time": "2 hours"},
            {"name": "Jallianwala Bagh", "description": "Historic public garden.", "image": photo_url("Jallianwala Bagh Amritsar"), "best_time": "Morning", "visit_time": "45-60 mins"},
            {"name": "Wagah Border", "description": "India-Pakistan border ceremony.", "image": photo_url("Wagah Border"), "best_time": "Evening", "visit_time": "Half day"}
        ],
        "transport": [
            "State buses and trains for intercity travel.",
            "Auto-rickshaws and cabs in cities."
        ],
    },
}


def load_users():
    if not DATA_FILE.exists():
        return []

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_users(users):
    DATA_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


users = load_users()


def normalize_budget(value):
    text = str(value or "").strip().lower()

    if "low" in text or "budget" in text or "cheap" in text:
        return "low"

    if "high" in text or "luxury" in text or "premium" in text:
        return "high"

    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        amount = int(digits)
        if amount < 5000:
            return "low"
        if amount > 15000:
            return "high"

    return "medium"


def normalize_destination_name(destination):
    normalized = str(destination or "").strip().lower()
    return DESTINATION_ALIASES.get(normalized, normalized)


def generic_destination_data(destination):
    safe_destination = destination.title()
    return {
        "hotels": [
            {"name": f"{safe_destination} Budget Inn", "base_price": 1800},
            {"name": f"{safe_destination} Comfort Stay", "base_price": 2800},
            {"name": f"{safe_destination} Central Residency", "base_price": 3800},
            {"name": f"{safe_destination} Grand Hotel", "base_price": 5000},
            {"name": f"{safe_destination} Premium Retreat", "base_price": 6500},
        ],
        "restaurants": [
            f"{safe_destination} Food Court",
            f"{safe_destination} Spice House",
            f"{safe_destination} Heritage Kitchen",
            f"{safe_destination} Market Cafe",
            f"{safe_destination} Skyline Dining",
        ],
        "activities": [
            f"Begin with the best-known attractions and landmarks in {destination}",
            f"Explore local food spots, shopping streets, and culture in {destination}",
            f"Keep the evening free for scenic views, relaxed dining, and photos in {destination}",
            f"Add a flexible half-day to discover hidden gems in {destination}",
            f"Reserve time for a neighborhood walk and local market stop in {destination}",
        ],
        "famous_places": [
            {"name": f"{safe_destination} Main Attraction", "description": f"A must-see place in {destination}.", "image": photo_url(f"{safe_destination} attraction"), "best_time": "Morning", "visit_time": "1-2 hours"},
            {"name": f"{safe_destination} Landmark", "description": f"Famous landmark in {destination}.", "image": photo_url(f"{safe_destination} landmark"), "best_time": "Evening", "visit_time": "1 hour"}
        ],
        "transport": [
            f"Cabs and local buses in {destination}.",
            f"Auto-rickshaws and walking for short distances."
        ],
    }


def build_day_hotels(hotels, budget_key, day_index):
    multiplier = BUDGET_MULTIPLIERS[budget_key]
    day_hotels = []

    for hotel in hotels[day_index : day_index + 2]:
        adjusted_price = round(hotel["base_price"] * multiplier / 100) * 100
        day_hotels.append(
            {
                "name": hotel["name"],
                "price": f"Rs. {adjusted_price:,}/night",
                "rating": round(3.8 + ((day_index % 3) * 0.4), 1),
                "tag": BUDGET_LABELS[budget_key],
            }
        )

    if len(day_hotels) < 2:
        for hotel in hotels[: 2 - len(day_hotels)]:
            adjusted_price = round(hotel["base_price"] * multiplier / 100) * 100
            day_hotels.append(
                {
                    "name": hotel["name"],
                    "price": f"Rs. {adjusted_price:,}/night",
                    "rating": round(4.0 + (len(day_hotels) * 0.3), 1),
                    "tag": BUDGET_LABELS[budget_key],
                }
            )

    return day_hotels


def build_day_restaurants(restaurants, day_index):
    selection = restaurants[day_index : day_index + 2]
    if len(selection) < 2:
        selection += restaurants[: 2 - len(selection)]
    return selection


def build_days(destination, total_days, budget_key):
    normalized_destination = normalize_destination_name(destination)
    destination_data = DESTINATION_DATA.get(
        normalized_destination,
        generic_destination_data(destination),
    )

    support_notes = [
        f"Keep some extra time for local travel inside {destination}",
        "Add one flexible stop based on weather and timing",
        "Reserve the evening for food, shopping, or a relaxed walk",
        "Capture photos and keep a short backup indoor activity",
        "Use one lighter slot for rest and spontaneous exploration",
    ]

    days = []
    famous_places = destination_data.get("famous_places", [])
    transport_tips = destination_data.get("transport", [])

    for index in range(total_days):
        primary_activity = destination_data["activities"][
            index % len(destination_data["activities"])
        ]
        secondary_activity = support_notes[index % len(support_notes)]
        day_hotels = build_day_hotels(destination_data["hotels"], budget_key, index)
        day_restaurants = build_day_restaurants(destination_data["restaurants"], index)

        # Assign one famous place and one transport tip per day, cycling if fewer than days
        day_famous_places = [famous_places[index % len(famous_places)]] if famous_places else []
        day_transport = [transport_tips[index % len(transport_tips)]] if transport_tips else []
        meal_highlight = day_restaurants[index % len(day_restaurants)] if day_restaurants else ""

        days.append(
            {
                "date": f"Day {index + 1}",
                "activities": [primary_activity, secondary_activity],
                "hotels": day_hotels,
                "restaurants": day_restaurants,
                "famous_places": day_famous_places,
                "transport": day_transport,
                "meal_highlight": meal_highlight,
            }
        )

    return days


def build_transport_options(from_city, to_city, budget_key):
    budget_multiplier = {"low": 0.9, "medium": 1.0, "high": 1.25}[budget_key]
    return [
        {
            "mode": "Flight",
            "duration": "1.5-2.5 hrs",
            "price": f"Rs. {int(4500 * budget_multiplier):,}",
            "note": f"Fastest option from {from_city} to {to_city} if you want to save time.",
        },
        {
            "mode": "Train",
            "duration": "5-10 hrs",
            "price": f"Rs. {int(1200 * budget_multiplier):,}",
            "note": "Best value for comfort and scenic intercity travel.",
        },
        {
            "mode": "Cab / Self-drive",
            "duration": "Flexible",
            "price": f"Rs. {int(3500 * budget_multiplier):,}+",
            "note": "Good for groups or if you want more control over stops on the way.",
        },
    ]


def build_plaintext_itinerary(destinations, segments, transport_segments, budget_key):
    lines = [
        f"Travel Buddy itinerary for {', '.join(destinations)}",
        f"Budget: {BUDGET_LABELS[budget_key]}",
        "",
    ]

    for segment in segments:
        lines.append(f"{segment['destination']}")
        lines.append(f"Overview: {segment['overview']}")
        for day in segment["days"]:
            lines.append(f"{day['date']}: {day['activities'][0]}")
            if day.get("famous_places"):
                lines.append(f"Visit: {day['famous_places'][0]['name']}")
            if day.get("transport"):
                lines.append(f"Transport tip: {day['transport'][0]}")
        lines.append("")

    if transport_segments:
        lines.append("Inter-city transport")
        for segment in transport_segments:
            lines.append(f"{segment['from']} -> {segment['to']}")
            for option in segment["options"]:
                lines.append(
                    f"- {option['mode']}: {option['duration']} | {option['price']}"
                )

    return "\n".join(lines)


@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    email = str(data.get("email", "")).strip().lower()

    if not email or not data.get("password"):
        return jsonify({"message": "Email and password are required"}), 400

    for user in users:
        if user["email"].strip().lower() == email:
            return jsonify({"message": "User already exists"}), 409

    new_user = {
        "name": data.get("name", "Traveler"),
        "email": email,
        "password": data["password"],
    }
    users.append(new_user)
    save_users(users)
    return jsonify(
        {
            "message": "User registered",
            "user": {"name": new_user["name"], "email": new_user["email"]},
        }
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")

    for user in users:
        if user["email"].strip().lower() == email and user["password"] == password:
            return jsonify(
                {
                    "message": "Login success",
                    "user": {
                        "name": user.get("name", "Traveler"),
                        "email": user["email"],
                    },
                }
            )

    return jsonify({"message": "Invalid credentials"}), 401



# Multi-destination itinerary endpoint
@app.route("/generate_itinerary", methods=["POST"])
def generate_itinerary():
    data = request.json or {}

    # Accept either a single destination or a list
    destinations = data.get("destinations")
    if not destinations:
        # fallback to single destination for backward compatibility
        single = data.get("destination", "your destination")
        destinations = [single]

    total_days = int(data.get("days", 3) or 3)
    budget_key = normalize_budget(data.get("budget", "medium"))

    trip_segments = []
    for idx, destination in enumerate(destinations):
        normalized_destination = normalize_destination_name(destination)
        destination_data = DESTINATION_DATA.get(
            normalized_destination,
            generic_destination_data(destination),
        )
        days = build_days(destination, max(total_days, 1), budget_key)
        trip_segments.append({
            "destination": destination,
            "overview": f"{destination.title()} plan with top places, food picks, stays, and local transport tips.",
            "days": days,
            "famous_places": destination_data.get("famous_places", []),
            "transport": destination_data.get("transport", []),
            "hero_image": photo_url(f"{destination} travel"),
            "quick_facts": [
                f"Best for {BUDGET_LABELS[budget_key].lower()} travelers",
                f"{max(total_days, 1)} day stay suggestion",
                "Includes stays, food, sightseeing, and transport",
            ],
        })

    # Build transport segments between destinations
    transport_segments = []
    for i in range(len(destinations) - 1):
        from_city = destinations[i]
        to_city = destinations[i+1]
        transport_segments.append({
            "from": from_city,
            "to": to_city,
            "options": build_transport_options(from_city, to_city, budget_key),
        })

    payload = {
        "summary": f"Trip covering {', '.join(destinations)} with {BUDGET_LABELS[budget_key].lower()} budget recommendations.",
        "trip_title": f"{' - '.join(city.title() for city in destinations)} Explorer",
        "budget_label": BUDGET_LABELS[budget_key],
        "total_days": max(total_days, 1),
        "segments": trip_segments,
        "transport_segments": transport_segments,
        "itinerary": build_plaintext_itinerary(
            destinations, trip_segments, transport_segments, budget_key
        ),
    }
    trips.append(payload)
    return jsonify(payload)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
