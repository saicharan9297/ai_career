def generate_roadmap(age, education, role, hours):
    if education == "Final Year":
        priority = "High priority interview topics"
    else:
        priority = "Concept building"

    roadmap = {
        "role": role,
        "strategy": priority,
        "daily_hours": hours,
        "phases": [
            "Phase 1: Fundamentals",
            "Phase 2: Practice",
            "Phase 3: Mock Interviews"
        ]
    }

    return roadmap
