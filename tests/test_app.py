import pytest
from fastapi.testclient import TestClient


class TestRoot:
    """Test the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestActivities:
    """Test the activities endpoint"""
    
    def test_get_activities(self, client):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        
        # Check that we have expected activities
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club",
        ]
        
        for activity in expected_activities:
            assert activity in activities
            
    def test_activity_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test the signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "signed up" in result["message"].lower()
        assert "newstudent@mergington.edu" in result["message"]
        
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup is rejected"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "already signed up" in result["detail"].lower()
        
    def test_signup_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=test@mergington.edu",
            follow_redirects=True
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "not found" in result["detail"].lower()
        
    def test_signup_updates_participants(self, client, reset_activities):
        """Test that signup actually updates the participants list"""
        # Get initial state
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Sign up new participant
        client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
            follow_redirects=True
        )
        
        # Check updated state
        response = client.get("/activities")
        updated_count = len(response.json()["Chess Club"]["participants"])
        
        assert updated_count == initial_count + 1
        assert "newstudent@mergington.edu" in response.json()["Chess Club"]["participants"]


class TestUnregister:
    """Test the unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "unregistered" in result["message"].lower()
        
    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "not found" in result["detail"].lower()
        
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister for a student not signed up"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "not signed up" in result["detail"].lower()
        
    def test_unregister_updates_participants(self, client, reset_activities):
        """Test that unregister actually updates the participants list"""
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Unregister participant
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        # Check updated state
        response = client.get("/activities")
        updated_count = len(response.json()["Chess Club"]["participants"])
        
        assert updated_count == initial_count - 1
        assert "michael@mergington.edu" not in response.json()["Chess Club"]["participants"]


class TestIntegration:
    """Integration tests for signup and unregister workflows"""
    
    def test_signup_and_unregister_flow(self, client, reset_activities):
        """Test the full signup and unregister flow"""
        email = "integration@mergington.edu"
        activity = "Programming%20Class"
        
        # Verify initial state
        response = client.get("/activities")
        initial_participants = response.json()["Programming Class"]["participants"].copy()
        assert email not in initial_participants
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        assert email in response.json()["Programming Class"]["participants"]
        
        # Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        assert email not in response.json()["Programming Class"]["participants"]
