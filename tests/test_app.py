"""
Tests for Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
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
            "description": "Competitive soccer practices and matches",
            "schedule": "Monday, Wednesday, Friday, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Pickup games, drills, and intramural tournaments",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "isabella@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore visual arts: painting, drawing, and mixed media",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["mia@mergington.edu", "charlotte@mergington.edu"]
        },
        "Drama Club": {
            "description": "Acting workshops, rehearsals, and school productions",
            "schedule": "Thursdays, 4:00 PM - 6:30 PM",
            "max_participants": 25,
            "participants": ["harper@mergington.edu", "amelia@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking, research, and argumentation skills",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["elijah@mergington.edu", "lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Hands-on experiments, STEM projects, and competitions",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["sophia.s@mergington.edu", "ethan@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(initial_activities)
    yield
    
    # Reset after test
    activities.clear()
    activities.update(initial_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_contains_required_fields(self, client, reset_activities):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants_list(self, client, reset_activities):
        """Test that participants list is accessible"""
        response = client.get("/activities")
        data = response.json()
        participants = data["Chess Club"]["participants"]
        
        assert isinstance(participants, list)
        assert len(participants) == 2
        assert "michael@mergington.edu" in participants


class TestSignupActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds participant to the activity"""
        new_email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={new_email}")
        
        response = client.get("/activities")
        data = response.json()
        assert new_email in data["Chess Club"]["participants"]
    
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup to non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_activity_full(self, client, reset_activities):
        """Test signup when activity is at capacity"""
        # Set activity to full
        activity = activities["Chess Club"]
        activity["participants"] = [f"student{i}@mergington.edu" for i in range(12)]
        
        response = client.post(
            "/activities/Chess Club/signup?email=full@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "full" in data["detail"]
    
    def test_signup_with_special_characters(self, client, reset_activities):
        """Test signup with URL-encoded email"""
        email = "student+tag@mergington.edu"
        response = client.post(
            f"/activities/Programming%20Class/signup?email={email.replace('+', '%2B')}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert email in data["Programming Class"]["participants"]


class TestUnregisterActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister"""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from activity"""
        email = "michael@mergington.edu"
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_participant_not_found(self, client, reset_activities):
        """Test unregister when participant not in activity"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notmember@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_with_special_characters(self, client, reset_activities):
        """Test unregister with URL-encoded email"""
        # First add a participant with special characters
        email = "student+tag@mergington.edu"
        client.post(
            f"/activities/Programming%20Class/signup?email={email.replace('+', '%2B')}"
        )
        
        # Now unregister
        response = client.delete(
            f"/activities/Programming%20Class/unregister?email={email.replace('+', '%2B')}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        data = response.json()
        assert email not in data["Programming Class"]["participants"]


class TestIntegration:
    """Integration tests for signup and unregister flows"""
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test complete signup and unregister flow"""
        email = "integration@mergington.edu"
        activity = "Art Club"
        
        # Signup
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_multiple_signups(self, client, reset_activities):
        """Test multiple students signing up for same activity"""
        activity = "Drama Club"
        emails = [
            "student1@mergington.edu",
            "student2@mergington.edu",
            "student3@mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all signed up
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data[activity]["participants"]
