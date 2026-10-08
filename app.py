import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from utils.database import init_db, connect
from utils.logic import rank_services, emergency_priority
from utils.services import geocode_location, fetch_osm_services, ask_ai

load_dotenv()
init_db()

APP_NAME = os.getenv("APP_NAME", "ResQNear AI")
REGION_NAME = os.getenv("REGION_NAME", "Demo Region")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
COUNTRY = os.getenv("COUNTRY", "India")
PRIMARY_EMERGENCY_NUMBER = os.getenv("PRIMARY_EMERGENCY_NUMBER", "112")
DEFAULT_LAT = float(os.getenv("DEFAULT_LAT", "26.1445"))
DEFAULT_LON = float(os.getenv("DEFAULT_LON", "91.7362"))
DEFAULT_RADIUS = float(os.getenv("DEFAULT_SEARCH_RADIUS_KM", "15"))

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🚑",
    layout="wide"
)

def df_query(sql, params=()):
    conn = connect()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df

def execute(sql, params=()):
    conn = connect()
    conn.execute(sql, params)
    conn.commit()
    conn.close()

def call_link(phone):
    phone = str(phone or "").strip()
    if not phone:
        return "Phone not listed"
    clean = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
    return f"[Call {phone}](tel:{clean})"

def combine_services(lat, lon, radius_km, category, include_online):
    local_df = df_query("SELECT * FROM services")
    local_records = local_df.to_dict("records")
    combined = list(local_records)

    if include_online:
        online = fetch_osm_services(lat, lon, radius_km)
        existing = {
            (str(x.get("name","")).lower().strip(), round(float(x["lat"]),4), round(float(x["lon"]),4))
            for x in combined
        }
        for row in online:
            key = (
                str(row.get("name","")).lower().strip(),
                round(float(row["lat"]),4),
                round(float(row["lon"]),4)
            )
            if key not in existing:
                combined.append(row)
                existing.add(key)

    return rank_services(lat, lon, combined, category, radius_km)

def locator_input(prefix):
    st.markdown("#### Your location")
    mode = st.radio(
        "Choose location method",
        ["Enter place name", "Enter coordinates"],
        horizontal=True,
        key=f"{prefix}_mode"
    )

    if mode == "Enter place name":
        place = st.text_input(
            "Town / locality / landmark",
            placeholder="Example: Guwahati Railway Station, Assam",
            key=f"{prefix}_place"
        )
        if st.button("Find Location", key=f"{prefix}_geocode"):
            if not place.strip():
                st.error("Enter a location first.")
            else:
                location = geocode_location(place)
                if location:
                    st.session_state[f"{prefix}_lat"] = location["lat"]
                    st.session_state[f"{prefix}_lon"] = location["lon"]
                    st.session_state[f"{prefix}_display"] = location["display_name"]
                else:
                    st.error("Could not locate that place. Try coordinates instead.")
    else:
        st.session_state[f"{prefix}_lat"] = st.number_input(
            "Latitude",
            value=float(st.session_state.get(f"{prefix}_lat", DEFAULT_LAT)),
            format="%.6f",
            key=f"{prefix}_lat_input"
        )
        st.session_state[f"{prefix}_lon"] = st.number_input(
            "Longitude",
            value=float(st.session_state.get(f"{prefix}_lon", DEFAULT_LON)),
            format="%.6f",
            key=f"{prefix}_lon_input"
        )

    lat = float(st.session_state.get(f"{prefix}_lat", DEFAULT_LAT))
    lon = float(st.session_state.get(f"{prefix}_lon", DEFAULT_LON))
    display = st.session_state.get(f"{prefix}_display", f"{lat:.6f}, {lon:.6f}")

    st.caption(f"Using location: {display}")
    return lat, lon

with st.sidebar:
    st.title(APP_NAME)
    st.caption(f"Emergency service locator for {REGION_NAME}")

    role = st.selectbox("Use as", ["Citizen", "Directory Admin"])

    if role == "Citizen":
        page = st.radio(
            "Navigation",
            [
                "Emergency Home",
                "Find Nearby Services",
                "Emergency Numbers",
                "Nearest Hospital",
                "Nearest Police",
                "Nearest Fire Station",
                "Emergency AI Assistant"
            ]
        )
    else:
        page = st.radio(
            "Navigation",
            [
                "Admin Dashboard",
                "Manage Service Directory",
                "Manage Helplines"
            ]
        )

    st.divider()
    st.markdown(f"### Emergency")
    st.markdown(call_link(PRIMARY_EMERGENCY_NUMBER))
    st.caption("Always verify local emergency numbers and service availability.")

if page == "Emergency Home":
    st.title(f"🚑 {APP_NAME}")
    st.subheader("Find the nearest emergency service and contact number quickly.")

    services = df_query("SELECT * FROM services")
    helplines = df_query("SELECT * FROM helplines")

    c1,c2,c3 = st.columns(3)
    c1.metric("Local Directory Services", len(services))
    c2.metric("Emergency Categories", services["category"].nunique() if not services.empty else 0)
    c3.metric("Stored Helplines", len(helplines))

    st.error(
        f"If there is immediate danger, call the appropriate local emergency service. "
        f"The configured primary emergency number is {PRIMARY_EMERGENCY_NUMBER}. "
        "This project helps locate services but does not replace emergency dispatch."
    )

    st.markdown("### What the project can locate")
    st.write(
        "Hospitals, police stations, fire stations, ambulance services, blood banks, "
        "disaster-response offices, and other emergency support points."
    )

    st.info(
        "The included local directory contains demo entries with fictional local phone numbers. "
        "Online OpenStreetMap results may contain real place data, but phone numbers can be missing or outdated."
    )

elif page == "Find Nearby Services":
    st.title("Find Nearby Emergency Services")

    lat, lon = locator_input("all")

    c1,c2,c3 = st.columns(3)
    with c1:
        category = st.selectbox(
            "Service Category",
            ["All","Hospital","Police","Fire Station","Ambulance","Blood Bank","Disaster Response","Women Support"]
        )
    with c2:
        radius = st.slider("Search Radius (km)", 1, 50, int(DEFAULT_RADIUS))
    with c3:
        online = st.checkbox("Include live OpenStreetMap lookup", value=True)

    if st.button("Search Emergency Services", use_container_width=True):
        results = combine_services(lat,lon,radius,category,online)

        if not results:
            st.warning("No services found in this radius. Increase the radius or try another location.")
        else:
            st.success(f"Found {len(results)} service(s).")

            map_rows = []

            for rank, service in enumerate(results[:25], start=1):
                map_rows.append({"lat":service["lat"],"lon":service["lon"]})

                with st.container(border=True):
                    st.markdown(f"### #{rank} — {service['name']}")
                    a,b,c,d = st.columns(4)
                    a.metric("Category", service["category"])
                    b.metric("Distance", f"{service['distance_km']:.2f} km")
                    c.metric("24×7", "Yes" if int(service.get("open_24x7",0)) else "Not confirmed")
                    d.metric("Source", service.get("source","Unknown"))

                    st.write(service.get("address","Address not listed"))
                    st.markdown(call_link(service.get("phone","")))

                    if service.get("alternate_phone"):
                        st.markdown(call_link(service["alternate_phone"]))

                    if not service.get("phone"):
                        st.caption("No phone number was provided by this listing. Verify contact details before relying on it.")

            if map_rows:
                st.subheader("Service Map")
                st.map(pd.DataFrame(map_rows))

elif page in ["Nearest Hospital","Nearest Police","Nearest Fire Station"]:
    mapping = {
        "Nearest Hospital":"Hospital",
        "Nearest Police":"Police",
        "Nearest Fire Station":"Fire Station"
    }
    category = mapping[page]

    st.title(page)
    lat,lon = locator_input(page.replace(" ","_"))
    radius = st.slider("Search Radius (km)", 1, 50, int(DEFAULT_RADIUS), key=f"{category}_radius")
    online = st.checkbox("Include live OpenStreetMap lookup", value=True, key=f"{category}_online")

    if st.button(f"Find {category}", use_container_width=True):
        results = combine_services(lat,lon,radius,category,online)

        if not results:
            st.warning(f"No {category.lower()} found in the selected radius.")
        else:
            nearest = results[0]

            st.success(f"Nearest result: {nearest['name']}")
            c1,c2,c3 = st.columns(3)
            c1.metric("Distance", f"{nearest['distance_km']:.2f} km")
            c2.metric("24×7", "Yes" if int(nearest.get("open_24x7",0)) else "Not confirmed")
            c3.metric("Source", nearest.get("source","Unknown"))

            st.write(nearest.get("address","Address not listed"))
            st.markdown(call_link(nearest.get("phone","")))

            st.map(pd.DataFrame([{"lat":nearest["lat"],"lon":nearest["lon"]}]))

            if len(results) > 1:
                st.subheader("Other Nearby Options")
                rows = pd.DataFrame(results[1:6])
                display_cols = ["name","category","address","phone","distance_km","source"]
                st.dataframe(rows[display_cols], use_container_width=True)

elif page == "Emergency Numbers":
    st.title("Emergency Numbers")

    st.warning(
        "Emergency numbers can vary by country, state, and service provider. "
        "The directory should be verified before deployment."
    )

    helplines = df_query(
        "SELECT * FROM helplines WHERE country=? ORDER BY category,name",
        (COUNTRY,)
    )

    if helplines.empty:
        st.info("No emergency helplines are stored for this country.")
    else:
        for _, row in helplines.iterrows():
            with st.container(border=True):
                st.markdown(f"### {row['name']}")
                st.write(row["description"] or "")
                st.markdown(call_link(row["phone"]))

elif page == "Emergency AI Assistant":
    st.title("Emergency AI Assistant")
    st.caption("Uses Groq if configured in .env; otherwise built-in safety guidance is used.")

    question = st.text_area(
        "Describe the emergency",
        placeholder="Example: There has been a road accident and someone is injured. What should I do first?"
    )

    if st.button("Get Emergency Guidance", use_container_width=True):
        context = (
            f"Country: {COUNTRY}. Configured primary emergency number: "
            f"{PRIMARY_EMERGENCY_NUMBER}."
        )
        answer, mode = ask_ai(
            question,
            context=context,
            emergency_number=PRIMARY_EMERGENCY_NUMBER
        )
        st.warning(answer)
        st.caption(mode)

elif page == "Admin Dashboard":
    st.title("Emergency Directory Admin Dashboard")

    password = st.text_input("Admin Password", type="password")
    if password != ADMIN_PASSWORD:
        st.warning("Enter the admin password configured in .env.")
        st.stop()

    services = df_query("SELECT * FROM services")
    helplines = df_query("SELECT * FROM helplines")

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Services", len(services))
    c2.metric("Verified Listings", int(services["verified"].sum()) if not services.empty else 0)
    c3.metric("24×7 Listings", int(services["open_24x7"].sum()) if not services.empty else 0)
    c4.metric("Helplines", len(helplines))

    if not services.empty:
        summary = services.groupby("category",as_index=False).size()
        st.plotly_chart(
            px.bar(summary,x="category",y="size",text_auto=True),
            use_container_width=True
        )

        st.subheader("Directory Map")
        st.map(services[["lat","lon"]])

elif page == "Manage Service Directory":
    st.title("Manage Service Directory")

    password = st.text_input("Admin Password", type="password", key="servicepass")
    if password != ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()

    with st.form("service_form", clear_on_submit=True):
        c1,c2 = st.columns(2)

        with c1:
            name = st.text_input("Service Name")
            category = st.selectbox(
                "Category",
                ["Hospital","Police","Fire Station","Ambulance","Blood Bank","Disaster Response","Women Support","Other"]
            )
            address = st.text_input("Address")
            area = st.text_input("Area")
            phone = st.text_input("Phone")

        with c2:
            alternate = st.text_input("Alternate Phone")
            lat = st.number_input("Latitude", value=DEFAULT_LAT, format="%.6f")
            lon = st.number_input("Longitude", value=DEFAULT_LON, format="%.6f")
            open_24x7 = st.checkbox("Open 24×7")
            verified = st.checkbox("Contact/details verified")

        if st.form_submit_button("Add Emergency Service", use_container_width=True):
            if not name.strip() or not address.strip():
                st.error("Service name and address are required.")
            else:
                execute("""INSERT INTO services
                    (name,category,address,area,phone,alternate_phone,lat,lon,
                     open_24x7,verified,source)
                    VALUES (?,?,?,?,?,?,?,?,?,?,'Admin Directory')""",
                    (
                        name,category,address,area,phone,alternate,lat,lon,
                        int(open_24x7),int(verified)
                    )
                )
                st.success("Service added.")
                st.rerun()

    services = df_query("SELECT * FROM services ORDER BY category,name")
    st.dataframe(services,use_container_width=True)

elif page == "Manage Helplines":
    st.title("Manage Emergency Helplines")

    password = st.text_input("Admin Password", type="password", key="helplinepass")
    if password != ADMIN_PASSWORD:
        st.warning("Enter admin password.")
        st.stop()

    with st.form("helpline_form", clear_on_submit=True):
        name = st.text_input("Helpline Name")
        category = st.text_input("Category")
        phone = st.text_input("Phone Number")
        description = st.text_area("Description")
        country = st.text_input("Country", value=COUNTRY)

        if st.form_submit_button("Add Helpline", use_container_width=True):
            if not name.strip() or not phone.strip():
                st.error("Name and phone number are required.")
            else:
                execute("""INSERT INTO helplines
                    (name,category,phone,description,country)
                    VALUES (?,?,?,?,?)""",
                    (name,category,phone,description,country)
                )
                st.success("Helpline added.")
                st.rerun()

    st.dataframe(
        df_query("SELECT * FROM helplines ORDER BY country,category,name"),
        use_container_width=True
    )
