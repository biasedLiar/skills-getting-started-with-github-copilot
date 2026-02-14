import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_200(self):
        """Test that /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary of activities"""
        response = client.get("/activities")
        activities = response.json()
        assert isinstance(activities, dict)
    
    def test_get_activities_contains_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
    
    def test_get_activities_has_chess_club(self):
        """Test that Chess Club is in the activities list"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Tennis%20Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
    
    def test_signup_for_nonexistent_activity(self):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_duplicate_email_returns_error(self):
        """Test that signing up with the same email twice returns error"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Drama%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Drama%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()
    
    def test_signup_response_contains_email(self):
        """Test that signup response contains the email"""
        email = "newstudent@mergington.edu"
        response = client.post(
            f"/activities/Art%20Studio/signup?email={email}"
        )
        assert response.status_code == 200
        assert email in response.json()["message"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_unregister_participant_success(self):
        """Test successful unregistration of a participant"""
        # First, signup
        email = "unregister@mergington.edu"
        client.post(
            f"/activities/Basketball/signup?email={email}"
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/Basketball/participants/{email}"
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
    
    def test_unregister_nonexistent_activity(self):
        """Test unregistering from non-existent activity returns 404"""
        response = client.delete(
            "/activities/NonExistent%20Activity/participants/test@mergington.edu"
        )
        assert response.status_code == 404
    
    def test_unregister_nonexistent_participant(self):
        """Test unregistering non-existent participant returns 404"""
        response = client.delete(
            "/activities/Chess%20Club/participants/notregistered@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_removes_participant(self):
        """Test that unregistering actually removes the participant"""
        email = "removetest@mergington.edu"
        activity = "Robotics%20Club"
        
        # Signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify in participants list
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Robotics Club"]["participants"]
        
        # Unregister
        client.delete(f"/activities/Robotics%20Club/participants/{email}")
        
        # Verify removed from participants list
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Robotics Club"]["participants"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_index(self):
        """Test that root endpoint redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
