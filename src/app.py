"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""
# Validate student is not already signed up
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
import re
import threading

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },

    # Sports (nuevas)
    "Soccer Team": {
        "description": "Team practices, drills and inter-school matches",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["alex@mergington.edu", "noah@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Lap training, technique work and lifeguard basics",
        "schedule": "Tuesdays and Thursdays, 5:00 PM - 6:30 PM",
        "max_participants": 25,
        "participants": ["linda@mergington.edu"]
    },

    # Artistic (nuevas)
    "Art Club": {
        "description": "Drawing, painting and mixed-media workshops",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["sarah@mergington.edu"]
    },
    "Drama Club": {
        "description": "Acting exercises, rehearsals and stage productions",
        "schedule": "Fridays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": ["drew@mergington.edu"]
    },

    # Intellectual (nuevas)
    "Debate Team": {
        "description": "Prepare for debates, practice argumentation and public speaking",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["hanna@mergington.edu"]
    },
    "Math Club": {
        "description": "Problem solving, competitions and math enrichment",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["marco@mergington.edu"]
    }
}
# Lock para evitar condiciones de carrera al modificar `activities`
activities_lock = threading.Lock()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Basic email validation and normalization
    email_clean = (email or "").strip()
    if not re.match(r"^[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+$", email_clean):
        raise HTTPException(status_code=400, detail="Invalid email address")

    normalized_email = email_clean.lower()

    # Protege la comprobación y la modificación con un lock para evitar duplicados por concurrencia
    with activities_lock:
        activity = activities[activity_name]
        normalized_participants = [p.strip().lower() for p in activity.get("participants", [])]

        # Prevent duplicate registration
        if normalized_email in normalized_participants:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        # Prevent over-capacity
        if len(activity.get("participants", [])) >= activity.get("max_participants", float("inf")):
            raise HTTPException(status_code=400, detail="Activity is full")

        # Add student
        activity.setdefault("participants", []).append(email_clean)

    return {"message": f"Signed up {email_clean} for {activity_name}"}
