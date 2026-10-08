# How IBM Bob Was Used in ResQNear AI

IBM Bob was used as an AI-assisted development tool throughout the creation of ResQNear AI. It helped analyze the emergency-service discovery problem, plan the multi-file architecture, generate and refine Python and Streamlit code, design the SQLite database, and implement major features such as place-name geocoding, latitude/longitude search, Haversine distance calculation, nearest-service ranking, category filtering, emergency contact display, map visualization, and local-directory management. IBM Bob also assisted in integrating optional OpenStreetMap Nominatim and Overpass services, creating fallback behavior when external services are unavailable, connecting configuration through the `.env` file, adding an optional Groq-powered emergency assistant, improving validation and error handling, refactoring reusable logic into separate modules, and preparing the project documentation. The developer remained responsible for choosing the final features, reviewing generated code, verifying emergency-information assumptions, testing the application, and ensuring that demo contact data is clearly separated from verified real-world emergency information.

## Example IBM Bob Prompts

### Ask Mode

```text
Analyze the problem of finding emergency services quickly based on a user's
location. Suggest features for locating hospitals, police stations, fire
stations, ambulances, blood banks and emergency contact numbers. The solution
should still work in demo/offline mode if a live API is unavailable.
```

### Plan Mode

```text
Create a modular Streamlit + SQLite implementation plan for an emergency
service locator. Include typed-location geocoding, coordinate search,
Haversine distance ranking, local emergency contacts, OpenStreetMap lookup,
service-category filters, maps, admin directory management, .env configuration,
and an optional AI emergency assistant.
```

### Agent Mode

```text
Implement the complete emergency-service locator across multiple Python files.
Create the Streamlit interface, SQLite schema, location logic, geocoding,
OpenStreetMap service lookup, nearest-service ranking, phone-number display,
admin tools, fallback behavior, AI assistant, environment configuration,
validation and documentation.
```
