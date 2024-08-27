from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Vote, Candidate
import pandas as pd


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///votes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            student_id = request.form['student_id']
            password = request.form['password']
            if User.query.filter_by(student_id=student_id).first() is None:
                user = User(student_id=student_id, password=password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                return "Student ID already exists!"
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            student_id = request.form['student_id']
            password = request.form['password']
            user = User.query.filter_by(student_id=student_id, password=password).first()
            if user:
                session['student_id'] = student_id
                return redirect(url_for('vote'))
            else:
                return "Invalid credentials!"
        return render_template('login.html')

    @app.route('/admin_login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            admin_id = request.form['admin_id']
            password = request.form['password']
            # Simple admin check (in practice, use more secure method)
            if admin_id == 'iptamenos' and password == 'iptamenos1@2@3':
                session['admin'] = True
                return redirect(url_for('upload_students'))
            else:
                return "Invalid admin credentials!"
        return render_template('admin_login.html')

    @app.route('/upload_students', methods=['GET', 'POST'])
    def upload_students():
        if 'admin' not in session:
            return redirect(url_for('admin_login'))

        if request.method == 'POST':
            file = request.files['file']
            if file and file.filename.endswith('.xlsx'):
                df = pd.read_excel(file)
                student_ids = df['student_id'].tolist()

                # Save student IDs to a file or database for validation
                with open('formatted_eligible_students.txt', 'w') as f:
                    for student_id in student_ids:
                        f.write(f"{student_id}\n")

                return "Student IDs uploaded and saved!"
            else:
                return "Please upload a valid Excel file."

        return render_template('upload_students.html')

    @app.route('/vote', methods=['GET', 'POST'])
    def vote():
        if 'student_id' not in session:
            return redirect(url_for('login'))

        # Check if student ID is in the eligible list
        with open('formatted_eligible_students.txt', 'r') as f:
            eligible_ids = [line.strip() for line in f]

        if session['student_id'] not in eligible_ids:
            return "You are not eligible to vote!"

        if request.method == 'POST':
            candidate_id = request.form['candidate_id']
            student_id = session['student_id']
            if Vote.query.filter_by(student_id=student_id, candidate_id=candidate_id).first() is None:
                vote = Vote(student_id=student_id, candidate_id=candidate_id)
                db.session.add(vote)
                db.session.commit()
                return render_template('vote_recorded.html')
            else:
                return render_template('already_voted.html')

        # If GET request and the student is eligible
        candidates = Candidate.query.all()
        return render_template('vote.html', candidates=candidates)

        # If GET request and the student is eligible
        candidates = Candidate.query.all()
        return render_template('vote.html', candidates=candidates)

    @app.route('/results')
    def results():
        results = db.session.query(
            Candidate.name,
            db.func.count(Vote.id).label('vote_count')
        ).outerjoin(Vote, Candidate.id == Vote.candidate_id
                    ).group_by(Candidate.id
                               ).order_by(db.func.count(Vote.id).desc()
                                          ).all()

        if results:
            highest_vote_count = results[0][1]
            results = [
                {
                    'name': result[0],
                    'vote_count': result[1],
                    'is_highest': result[1] == highest_vote_count
                } for result in results
            ]

        return render_template('results.html', results=results)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=False)
