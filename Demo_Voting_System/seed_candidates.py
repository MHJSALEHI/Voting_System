from app import create_app
from models import db, Candidate

app = create_app()

with app.app_context():
    # Delete all existing records in the Candidate table
    Candidate.query.delete()
    db.session.commit()

    # List of candidate names
    candidate_names = [
        "Candidate 1",
        "Candidate 2",
        "Candidate 3",
        "Candidate 4",
        "Candidate 5",
        "Candidate 6",
        "Candidate 7",
        "Candidate 8",
        "Candidate 9",
        "Candidate 10"
    ]

    # Create and add candidate records
    for name in candidate_names:
        candidate = Candidate(name=name)
        db.session.add(candidate)

    # Commit the changes to the database
    db.session.commit()
