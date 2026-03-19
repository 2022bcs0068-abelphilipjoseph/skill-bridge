import pytest
from app import fallback_analysis, load_data

# Test 1: Happy Path - Testing the Data Loader
def test_load_data_happy_path():
    # Act
    data = load_data()
    
    # Assert
    assert isinstance(data, dict)
    assert "Cloud Engineer" in data # Checking if our synthetic data loaded
    assert "required_skills" in data["Cloud Engineer"]

# Test 2: Edge Case - Testing the Rule-Based Fallback with the new Roadmap schema
def test_fallback_analysis_edge_case():
    # Arrange
    user_text = "I have 3 years of experience with Python, HTML, and I know Git."
    target_skills = ["Python", "React", "Git", "Docker"]
    
    # Act
    result = fallback_analysis(user_text, target_skills)
    
    # Assert
    assert result["method"] == "Rule-Based Fallback"
    assert "Python" in result["matched_skills"]
    assert "Git" in result["matched_skills"]
    assert "React" in result["missing_skills"]
    assert "Docker" in result["missing_skills"]
    
    # Testing the newly added Learning Roadmap feature!
    assert "learning_roadmap" in result
    assert len(result["learning_roadmap"]) == 2 # Should match the 2 missing skills (React & Docker)
    assert result["learning_roadmap"][0]["missing_skill"] == "React"
    assert result["learning_roadmap"][0]["timeline"] == "1-2 Weeks"
