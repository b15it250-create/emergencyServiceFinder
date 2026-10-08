# ResQNear AI — Emergency Service Locator & Contact Number Finder

ResQNear AI is a hackathon-ready emergency service locator designed to help users quickly find nearby hospitals, police stations, fire stations, ambulance services, blood banks, disaster-response offices, and other critical support services based on their location.

## Main Features

- Search using a typed place name
- Search using latitude and longitude
- Nearest-service ranking using Haversine distance
- Hospital locator
- Police station locator
- Fire station locator
- Ambulance locator
- Blood bank locator
- Disaster-response service locator
- Local emergency contact directory
- Emergency helpline directory
- One-tap `tel:` call links
- Map view of nearby services
- Optional live OpenStreetMap lookup
- Local/offline SQLite fallback directory
- Admin service-directory management
- Admin helpline management
- Optional Groq AI emergency assistant
- `.env` configuration

## Important Demo Note

The bundled local directory contains fictional demonstration phone numbers so that the project does not misrepresent them as real emergency contacts.

For a real deployment, administrators should replace all demo records with verified official service data.

OpenStreetMap results may provide real locations, but phone numbers can be missing, outdated, or unverified.

## Primary Emergency Number

The default `.env` uses:

```env
PRIMARY_EMERGENCY_NUMBER=112
```

This is configured for the India demo. Before deploying elsewhere, update emergency numbers according to the target country or region.

## How Location Search Works

### Place-name search

The system uses OpenStreetMap Nominatim to convert a location such as:

```text
Guwahati Railway Station, Assam
```

into latitude and longitude.

### Coordinate search

The user can directly enter:

```text
Latitude
Longitude
```

### Distance ranking

The Haversine formula calculates approximate straight-line geographic distance between the user and emergency services.

## Live Emergency Service Lookup

When enabled in `.env`:

```env
ENABLE_ONLINE_OSM_LOOKUP=true
```

the project can use OpenStreetMap Overpass data to search for nearby:

- Hospitals
- Police stations
- Fire stations
- Ambulance stations
- Blood-donation / blood-bank locations where tagged

The system merges live results with the local directory and removes simple duplicates.

## Offline / Local Directory

SQLite stores a local directory so that the core project can still demonstrate service search without relying completely on a live external service.

Admins can add:

- Service name
- Category
- Address
- Area
- Phone
- Alternate phone
- GPS coordinates
- 24×7 status
- Verification status

## AI Emergency Assistant

The project works without AI.

If a Groq key is added:

```env
GROQ_API_KEY=your_key
```

the emergency assistant can generate short safety-first guidance.

Without the key, a built-in rule-based emergency advisor is used.

## Technology Stack

- Python
- Streamlit
- SQLite
- Pandas
- Plotly
- Requests
- python-dotenv
- OpenStreetMap Nominatim
- OpenStreetMap Overpass API

## Project Structure

```text
resqnear_ai_emergency_locator/
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
├── HOW_IBM_BOB_WAS_USED.md
├── run_app.bat
├── .streamlit/
│   └── config.toml
├── data/
│   └── resqnear.db
└── utils/
    ├── database.py
    ├── logic.py
    └── services.py
```

## Installation

```bash
pip install -r requirements.txt
```

Run:

```bash
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

Windows users can also run:

```text
run_app.bat
```

## Default Admin Password

```text
admin123
```

Change it inside `.env`.

## Problem Statement

During emergencies, people often lose valuable time searching for the nearest hospital, police station, fire station, ambulance provider, blood bank, or disaster-response office. Search results may be scattered across different websites, contact numbers may be difficult to find, and users may not know which service is actually closest to their current location. This becomes even more challenging for travellers, people in unfamiliar areas, rural communities, or users facing stressful situations where quick decisions are important.

Another major challenge is that emergency contact data can be incomplete or outdated. A useful emergency platform therefore needs both location-based discovery and a manageable local directory that authorities or administrators can verify and maintain. It should also continue to provide basic functionality when external services are unavailable.

## Solution Statement

ResQNear AI is a location-based emergency service locator and contact-number finder built using Python, Streamlit, SQLite, and OpenStreetMap services.

Users can enter a place name or GPS coordinates and select the type of emergency service they need. The application calculates the geographic distance to nearby services and ranks them from nearest to farthest. Results can include the service name, category, address, distance, 24×7 availability information, data source, and phone number when available.

The system includes dedicated nearest-hospital, nearest-police, and nearest-fire-station search pages, along with a general multi-category emergency locator. A local SQLite emergency directory provides offline/demo data, while optional OpenStreetMap integration can discover additional nearby services. An admin dashboard allows emergency-service records and helplines to be added and maintained.

The platform also includes direct call links, emergency helplines, maps, and an optional AI emergency assistant. The AI layer is not required for the core locator to work, and rule-based safety guidance is available when no API key is configured.

## Hackathon Pitch

"ResQNear AI reduces the time between an emergency and the right response. Instead of searching multiple websites or guessing which service is closest, users can enter their location and instantly see nearby hospitals, police stations, fire stations, ambulance services, blood banks, and emergency contacts ranked by distance."

## Suggested Demo Flow

1. Enter a location name.
2. Convert the location to GPS coordinates.
3. Choose Hospital, Police, Fire Station, or All Services.
4. Search within a selected radius.
5. Display results ordered by distance.
6. Show contact numbers and call links.
7. Plot nearby services on a map.
8. Enable OpenStreetMap lookup to discover live public map listings.
9. Demonstrate the offline SQLite fallback directory.
10. Use the admin panel to add a verified local emergency service.
11. Ask the emergency assistant what to do during an accident or fire.

## Future Improvements

- Browser GPS auto-detection
- Native Android/iOS application
- Real road-travel time instead of straight-line distance
- Live ambulance availability
- Hospital bed availability
- Traffic-aware routing
- Government emergency-service APIs
- Verified-service badges with review dates
- SMS emergency location sharing
- WhatsApp emergency location sharing
- Multilingual voice assistant
- Offline map packs
- Accessibility mode
- Emergency contacts for family members
