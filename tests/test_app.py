from fastapi.testclient import TestClient
import pytest
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 307  # Código de redirección temporal
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    
    # Verificar estructura de una actividad
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)

def test_signup_success():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    # Verificar que el estudiante fue agregado
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]

def test_signup_activity_not_found():
    response = client.post("/activities/NonExistentClub/signup?email=student@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_signup_already_registered():
    activity_name = "Programming Class"
    email = "emma@mergington.edu"  # Este email ya está registrado en esta actividad
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student already signed up for this activity"}

def test_unregister_success():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # Un email que sabemos que está registrado
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

    # Verificar que el estudiante fue eliminado
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]

def test_unregister_activity_not_found():
    response = client.post("/activities/NonExistentClub/unregister?email=student@mergington.edu")
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}

def test_unregister_not_registered():
    activity_name = "Chess Club"
    email = "notregistered@mergington.edu"
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not registered for this activity"}