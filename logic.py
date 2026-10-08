import math

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)

    a = (
        math.sin(dp/2)**2
        + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    )
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1-a))

def rank_services(lat, lon, services, category="All", radius_km=15):
    result = []
    for service in services:
        row = dict(service)

        if category != "All" and row.get("category") != category:
            continue

        distance = haversine_km(
            float(lat), float(lon),
            float(row["lat"]), float(row["lon"])
        )

        if distance <= radius_km:
            row["distance_km"] = round(distance, 2)
            result.append(row)

    return sorted(result, key=lambda x: x["distance_km"])

def emergency_priority(service):
    score = 0
    if int(service.get("open_24x7", 0)):
        score += 20
    if int(service.get("verified", 0)):
        score += 15
    if service.get("phone"):
        score += 20

    category_bonus = {
        "Hospital": 20,
        "Police": 20,
        "Fire Station": 20,
        "Ambulance": 25,
        "Disaster Response": 20,
        "Blood Bank": 10,
        "Women Support": 10
    }
    score += category_bonus.get(service.get("category"), 5)
    return min(score, 100)
