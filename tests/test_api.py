"""
Tests for the main API endpoints.
"""

import pytest


def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client, reset_activities):
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert "Gym Class" in activities
    
    # Check structure of an activity
    chess_club = activities["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


class TestSignup:
    """Tests for signup endpoint."""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test signup for activity when already registered."""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_increases_participant_count(self, client, reset_activities):
        """Test that signup actually adds participant to activity."""
        # Get initial participant count
        initial = client.get("/activities").json()
        initial_count = len(initial["Chess Club"]["participants"])
        
        # Sign up new student
        client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        
        # Check updated participant count
        updated = client.get("/activities").json()
        updated_count = len(updated["Chess Club"]["participants"])
        
        assert updated_count == initial_count + 1
        assert "newstudent@mergington.edu" in updated["Chess Club"]["participants"]


class TestUnregister:
    """Tests for unregister endpoint."""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity."""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Unregistered" in data["message"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister when not registered for activity."""
        response = client.post(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]
    
    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that unregister actually removes participant from activity."""
        # Get initial participant count
        initial = client.get("/activities").json()
        initial_count = len(initial["Chess Club"]["participants"])
        
        # Unregister a student
        client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        
        # Check updated participant count
        updated = client.get("/activities").json()
        updated_count = len(updated["Chess Club"]["participants"])
        
        assert updated_count == initial_count - 1
        assert "michael@mergington.edu" not in updated["Chess Club"]["participants"]
    
    def test_unregister_then_signup_again(self, client, reset_activities):
        """Test that student can re-signup after unregistering."""
        email = "michael@mergington.edu"
        
        # Unregister
        client.post(f"/activities/Chess Club/unregister?email={email}")
        
        # Verify unregistered
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]
        
        # Re-signup should work
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 200
        
        # Verify re-registered
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
