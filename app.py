from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pranesh:pranesh%405264@localhost:5432/assessment_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'Pranesh@5264'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'users'  # Ensure the table name matches
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'))  # Update to match the SQL schema

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

class Role(db.Model):
    __tablename__ = 'roles'  # Ensure the table name matches
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)

class Course(db.Model):
    __tablename__ = 'courses'  # Ensure the table name matches
    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)

class Material(db.Model):
    __tablename__ = 'materials'  # Ensure the table name matches
    material_id = db.Column(db.Integer, primary_key=True)
    material_name = db.Column(db.String(255), nullable=False)
    material_link = db.Column(db.String(500), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))  # Update to match the SQL schema

class Question(db.Model):
    __tablename__ = 'questions'  # Ensure the table name matches
    question_id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))  # Update to match the SQL schema
    faculty_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # Update to match the SQL schema

class Slot(db.Model):
    __tablename__ = 'slots'  # Ensure the table name matches
    slot_id = db.Column(db.Integer, primary_key=True)
    slot_time = db.Column(db.Time, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))  # Update to match the SQL schema
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'))  # Update to match the SQL schema

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    
    # Check if user exists and password matches
    if user and user.password == password:
        session['user_id'] = user.user_id
        session['name'] = user.name
        session['role_id'] = user.role_id
        if user.role_id == 1:  # Admin
            return redirect(url_for('admin_dashboard'))
        elif user.role_id == 2:  # Faculty
            return redirect(url_for('faculty_dashboard'))
        elif user.role_id == 3:  # Student
            return redirect(url_for('student_dashboard'))
    
    return 'Invalid credentials'

@app.route('/admin/dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/faculty/dashboard')
def faculty_dashboard():
    courses = Course.query.all()
    return render_template('faculty_dashboard.html', courses=courses)

@app.route('/student/dashboard')
def student_dashboard():
    courses = Course.query.all()
    return render_template('student_dashboard.html', courses=courses)

@app.route('/faculty/course/<int:course_id>')
def faculty_course(course_id):
    return render_template('faculty_course.html')

@app.route('/student/course/<int:course_id>')
def student_course(course_id):
    materials = Material.query.filter_by(course_id=course_id).all()
    return render_template('student_course_materials.html', materials=materials, course=Course.query.get(course_id))

@app.route('/student/book_slot', methods=['POST'])
def book_slot():
    data = request.get_json()
    slot_time = data['slot_time']
    course_id = data['course_id']
    new_slot = Slot(slot_time=slot_time, student_id=session['user_id'], course_id=course_id)
    db.session.add(new_slot)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/assessment/rules/<int:course_id>')
def assessment_rules(course_id):
    return render_template('assessment_rules.html', course=Course.query.get(course_id))

@app.route('/assessment/<int:course_id>')
def assessment(course_id):
    questions = Question.query.filter_by(course_id=course_id).all()
    return render_template('assessment.html', questions=questions, course=Course.query.get(course_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
