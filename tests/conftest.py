import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a clean state before each test"""
    # Store original activities
    original_activities = {
        k: {"participants": v["participants"].copy(), **{kk: vv for kk, vv in v.items() if kk != "participants"}}
        for k, v in activities.items()
    }
    
    yield
    
    # Restore original state after test
    for key, value in original_activities.items():
        if key in activities:
            activities[key]["participants"] = value["participants"]
