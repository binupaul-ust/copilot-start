"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Fixture to provide a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Fixture to reset activities to initial state after each test"""
    from src import app as app_module
    
    initial_activities = {
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
        "Soccer Team": {
            "description": "Join the school soccer team and compete in local leagues",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["lucas@mergington.edu", "mia@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly matches",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["liam@mergington.edu", "ava@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and participate in school theater productions",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 16,
            "participants": ["amelia@mergington.edu", "benjamin@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["charlotte@mergington.edu", "elijah@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["william@mergington.edu", "sophia@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities after test
    app_module.activities = initial_activities


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that get_activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_includes_details(self, client):
        """Test that activities include all required details"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_initial_participants(self, client):
        """Test that activities include their initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "alex@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds the participant to the activity"""
        client.post("/activities/Chess%20Club/signup?email=alex@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert "alex@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signing up twice fails"""
        # First signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=alex@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Try to signup again
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=alex@mergington.edu"
        )
        assert response2.status_code == 400
        
        result = response2.json()
        assert "already signed up" in result["detail"]

    def test_signup_existing_participant_fails(self, client, reset_activities):
        """Test that signing up an existing participant fails"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "already signed up" in result["detail"]

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Club/signup?email=alex@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_signup_multiple_different_activities(self, client, reset_activities):
        """Test signing up for multiple different activities"""
        email = "alex@mergington.edu"
        
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        response2 = client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify participant is in both activities
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "michael@mergington.edu" in result["message"]
        assert "Chess Club" in result["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes the participant"""
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity_fails(self, client):
        """Test unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Nonexistent%20Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_not_registered_fails(self, client, reset_activities):
        """Test unregistering someone not registered fails"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=alex@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "not registered" in result["detail"]

    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that someone can sign up again after unregistering"""
        email = "alex@mergington.edu"
        
        # Sign up
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.delete(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response3.status_code == 200
        
        # Verify they're registered
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests"""

    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test complete signup and unregister flow"""
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        # Initial check
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        response = client.post(
            f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify count increased
        response = client.get("/activities")
        new_count = len(response.json()[activity]["participants"])
        assert new_count == initial_count + 1
        
        # Unregister
        response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify count returned to initial
        response = client.get("/activities")
        final_count = len(response.json()[activity]["participants"])
        assert final_count == initial_count

    def test_multiple_signups_and_unregisters(self, client, reset_activities):
        """Test multiple signups and unregisters"""
        activity = "Programming Class"
        emails = [
            "alice@mergington.edu",
            "bob@mergington.edu",
            "charlie@mergington.edu"
        ]
        
        # Sign up all
        for email in emails:
            response = client.post(
                f"/activities/{activity.replace(' ', '%20')}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all are registered
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        for email in emails:
            assert email in participants
        
        # Unregister middle one
        response = client.delete(
            f"/activities/{activity.replace(' ', '%20')}/unregister?email={emails[1]}"
        )
        assert response.status_code == 200
        
        # Verify only middle one was removed
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert emails[0] in participants
        assert emails[1] not in participants
        assert emails[2] in participants
