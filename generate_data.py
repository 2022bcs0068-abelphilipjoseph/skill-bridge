import json
import os

def generate_synthetic_data():
    jobs_data = {
        "Cloud Engineer": {
            "title": "Cloud Engineer",
            "description": "Responsible for designing, building, and maintaining scalable cloud infrastructure.",
            "required_skills": ["AWS", "Python", "Kubernetes", "Terraform", "CI/CD", "Linux"]
        },
        "Frontend Developer": {
            "title": "Frontend Developer",
            "description": "Builds responsive, accessible, and highly performant user interfaces.",
            "required_skills": ["React", "TypeScript", "HTML/CSS", "Jest", "Webpack", "Git"]
        },
        "Data Scientist": {
            "title": "Data Scientist",
            "description": "Analyzes complex datasets to extract actionable business insights and train predictive models.",
            "required_skills": ["Python", "SQL", "Pandas", "Machine Learning", "TensorFlow", "Statistics"]
        }
    }

    # Write to JSON file
    file_path = "jobs.json"
    with open(file_path, "w") as f:
        json.dump(jobs_data, f, indent=4)
        
    print(f"✅ Synthetic data successfully written to {file_path}")

if __name__ == "__main__":
    generate_synthetic_data()
