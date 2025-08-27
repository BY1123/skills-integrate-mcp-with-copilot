"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
from sqlmodel import select

from .db import init_db, get_session
from .models import Activity, Signup


app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")


@app.on_event("startup")
def on_startup():
    init_db()
    # seed data if empty
    with get_session() as session:
        count = session.exec(select(Activity)).first()
        if not count:
            seed_activities = [
                Activity(name="Chess Club", description="Learn strategies and compete in chess tournaments", schedule="Fridays, 3:30 PM - 5:00 PM", max_participants=12),
                Activity(name="Programming Class", description="Learn programming fundamentals and build software projects", schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM", max_participants=20),
                Activity(name="Gym Class", description="Physical education and sports activities", schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", max_participants=30),
            ]
            session.add_all(seed_activities)
            session.commit()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    with get_session() as session:
        activities = session.exec(select(Activity)).all()
        return activities


@app.post("/activities/{activity_id}/signup")
def signup_for_activity(activity_id: int, email: str):
    with get_session() as session:
        activity = session.get(Activity, activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # check capacity
        current = session.exec(select(Signup).where(Signup.activity_id == activity_id)).all()
        if activity.max_participants and len(current) >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        # prevent duplicate signup
        existing = session.exec(select(Signup).where(Signup.activity_id == activity_id).where(Signup.student_email == email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        signup = Signup(student_email=email, activity_id=activity_id)
        session.add(signup)
        session.commit()
        session.refresh(signup)
        return {"message": f"Signed up {email} for {activity.name}"}


@app.delete("/activities/{activity_id}/unregister")
def unregister_from_activity(activity_id: int, email: str):
    with get_session() as session:
        activity = session.get(Activity, activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        existing = session.exec(select(Signup).where(Signup.activity_id == activity_id).where(Signup.student_email == email)).first()
        if not existing:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        session.delete(existing)
        session.commit()
        return {"message": f"Unregistered {email} from {activity.name}"}
