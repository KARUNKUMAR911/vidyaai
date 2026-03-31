from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'vidyaai_secret_key_2026'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'vidyaai.db')
os.makedirs(os.path.join(basedir, 'database'), exist_ok=True)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    language = db.Column(db.String(20), default='english')
    school = db.Column(db.String(200))
    avatar = db.Column(db.String(10), default='🧑')
    joined = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0)
    progress = db.Column(db.Text, default='{}') 

class Progress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    grade = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    completed = db.Column(db.Integer, default=0)
    total = db.Column(db.Integer, default=0)
    stars = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    receiver_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    friend_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    status = db.Column(db.String(20), default='pending')

# Routes
@app.route('/')
def home():
    if 'student_id' in session:
        return redirect(url_for('grade_dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        grade = request.form['grade']
        language = request.form['language']
        school = request.form['school']

        # Check if email exists
        if Student.query.filter_by(email=email).first():
            return render_template('signup.html', error='Email already registered!')

        # Create student
        hashed_password = generate_password_hash(password)
        student = Student(
            name=name,
            email=email,
            password=hashed_password,
            grade=grade,
            language=language,
            school=school
        )
        db.session.add(student)
        db.session.commit()

        session['student_id'] = student.id
        session['student_name'] = student.name
        session['student_grade'] = student.grade
        return redirect(url_for('grade_dashboard'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        student = Student.query.filter_by(email=email).first()
        if student and check_password_hash(student.password, password):
            session['student_id'] = student.id
            session['student_name'] = student.name
            session['student_grade'] = student.grade
            session['student_language'] = student.language
            return redirect(url_for('grade_dashboard'))

        return render_template('login.html', error='Wrong email or password!')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('dashboard.html', student=student)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/students/search')
def search_students():
    query = request.args.get('q', '')
    students = Student.query.filter(
        Student.name.contains(query),
        Student.id != session.get('student_id')
    ).limit(10).all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'grade': s.grade,
        'avatar': s.avatar
    } for s in students])

@app.route('/api/send_message', methods=['POST'])
def send_message():
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'})
    data = request.json
    msg = Message(
        sender_id=session['student_id'],
        receiver_id=data['receiver_id'],
        content=data['content']
    )
    db.session.add(msg)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/messages/<int:friend_id>')
def get_messages(friend_id):
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'})
    my_id = session['student_id']
    messages = Message.query.filter(
        ((Message.sender_id == my_id) & (Message.receiver_id == friend_id)) |
        ((Message.sender_id == friend_id) & (Message.receiver_id == my_id))
    ).order_by(Message.timestamp).all()
    return jsonify([{
        'sender_id': m.sender_id,
        'content': m.content,
        'timestamp': m.timestamp.strftime('%H:%M')
    } for m in messages])

@app.route('/tutor')
def tutor():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    subject = request.args.get('subject', 'General')
    return render_template('tutor.html', student=student, subject=subject)

@app.route('/friends')
def friends():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    all_students = Student.query.filter(Student.id != session['student_id']).all()
    return render_template('friends.html', student=student, students=all_students)

@app.route('/lkg/alphabets')
def lkg_alphabets():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_alphabets.html', student=student)

@app.route('/learn')
def grade_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    grade    = session.get('student_grade', '')
    language = session.get('student_language', 'english')

    if grade == 'LKG':
        if language == 'kannada':
            return redirect(url_for('lkg_dashboard_kannada'))
        elif language == 'hindi':
            return redirect(url_for('lkg_dashboard_hindi'))
        elif language == 'tamil':
            return redirect(url_for('lkg_dashboard_tamil'))
        elif language == 'telugu':
            return redirect(url_for('lkg_dashboard_telugu'))
        else:
            return redirect(url_for('lkg_dashboard'))

    elif grade == 'UKG':
        if language == 'kannada':
            return redirect(url_for('ukg_dashboard_kannada'))
        else:
            return redirect(url_for('ukg_dashboard'))

    elif grade in ['1','2','3','4','5','6','7','8','9','10','11','12']:
        if language == 'kannada':
            return redirect(f'/class/{grade}/kannada')
        else:
            return redirect(f'/class/{grade}')
    else:
        return redirect(url_for('lkg_dashboard'))
    


@app.route('/lkg/kannada')
def lkg_dashboard_kannada():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_dashboard_kannada.html', student=student)

@app.route('/class/1/kannada')
def class1_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_dashboard_kannada.html', student=student)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    if request.method == 'POST':
        new_grade = request.form.get('grade')
        new_language = request.form.get('language')
        new_school = request.form.get('school')
        student.grade = new_grade
        student.language = new_language
        student.school = new_school
        db.session.commit()
        session['student_grade'] = new_grade
        session['student_language'] = new_language
        return redirect(url_for('grade_dashboard'))
    return render_template('profile.html', student=student)

@app.route('/lkg/numbers')
def lkg_numbers():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_numbers.html', student=student)


@app.route('/lkg/colors')
def lkg_colors():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_colors.html', student=student)

@app.route('/lkg/shapes')
def lkg_shapes():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_shapes.html', student=student)

@app.route('/lkg/animals')
def lkg_animals():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_animals.html', student=student)

@app.route('/lkg/fruits')
def lkg_fruits_vegetables():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_fruits_vegetables.html', student=student)




@app.route('/lkg/body')
def lkg_body():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_body.html', student=student)

@app.route('/lkg/rhymes')
def lkg_rhymes():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_rhymes_songs.html', student=student)

@app.route('/lkg/family')
def lkg_family():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_family.html', student=student)

@app.route('/lkg/days')
def lkg_days():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_days.html', student=student)


import json

@app.route('/api/progress/save', methods=['POST'])
def save_progress():
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'})
    data = request.json
    grade = data.get('grade')
    subject = data.get('subject')
    completed = data.get('completed', 0)
    total = data.get('total', 0)
    stars = data.get('stars', 0)

    prog = Progress.query.filter_by(
        student_id=session['student_id'],
        grade=grade,
        subject=subject
    ).first()

    if prog:
        prog.completed = completed
        prog.total = total
        prog.stars = stars
        prog.last_updated = datetime.utcnow()
    else:
        prog = Progress(
            student_id=session['student_id'],
            grade=grade,
            subject=subject,
            completed=completed,
            total=total,
            stars=stars
        )
        db.session.add(prog)

    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/progress/load', methods=['GET'])
def load_progress():
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'})
    grade = request.args.get('grade', session.get('student_grade'))
    progs = Progress.query.filter_by(
        student_id=session['student_id'],
        grade=grade
    ).all()
    return jsonify({
        p.subject: {
            'completed': p.completed,
            'total': p.total,
            'stars': p.stars
        } for p in progs
    })

@app.route('/ukg')
def ukg_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_dashboard.html', student=student)


@app.route('/lkg')
def lkg_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_dashboard.html', student=student)

@app.route('/ukg/kannada')
def ukg_dashboard_kannada():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_dashboard_kannada.html', student=student)

@app.route('/class/1')
def primary_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    grade = session.get('student_grade', '1')
    return render_template(f'class{grade}_dashboard.html', student=student)

@app.route('/class/2')
def class2_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class2_dashboard.html', student=student)

@app.route('/class/3')
def class3_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class3_dashboard.html', student=student)

@app.route('/class/4')
def class4_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class4_dashboard.html', student=student)

@app.route('/class/5')
def class5_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class5_dashboard.html', student=student)

@app.route('/class/6')
def middle_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class6_dashboard.html', student=student)

@app.route('/class/7')
def class7_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class7_dashboard.html', student=student)

@app.route('/class/8')
def class8_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class8_dashboard.html', student=student)

@app.route('/class/9')
def high_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class9_dashboard.html', student=student)

@app.route('/class/10')
def class10_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class10_dashboard.html', student=student)

@app.route('/class/11')
def higher_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class11_dashboard.html', student=student)

@app.route('/class/12')
def class12_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class12_dashboard.html', student=student)

@app.route('/class/2/kannada')
def class2_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class2_dashboard_kannada.html', student=student)

@app.route('/class/3/kannada')
def class3_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class3_dashboard_kannada.html', student=student)

@app.route('/class/4/kannada')
def class4_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class4_dashboard_kannada.html', student=student)

@app.route('/class/5/kannada')
def class5_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class5_dashboard_kannada.html', student=student)

@app.route('/class/6/kannada')
def class6_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class6_dashboard_kannada.html', student=student)

@app.route('/class/7/kannada')
def class7_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class7_dashboard_kannada.html', student=student)

@app.route('/class/8/kannada')
def class8_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class8_dashboard_kannada.html', student=student)

@app.route('/class/9/kannada')
def class9_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class9_dashboard_kannada.html', student=student)

@app.route('/class/10/kannada')
def class10_kannada_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class10_dashboard_kannada.html', student=student)

# UKG English Lessons
@app.route('/ukg/alphabets')
def ukg_alphabets():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_alphabets.html', student=student)

@app.route('/ukg/numbers')
def ukg_numbers():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_numbers.html', student=student)

@app.route('/ukg/colors')
def ukg_colors():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_colors.html', student=student)

@app.route('/ukg/shapes')
def ukg_shapes():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_shapes.html', student=student)

@app.route('/ukg/animals')
def ukg_animals():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_animals.html', student=student)

@app.route('/ukg/fruits')
def ukg_fruits():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_fruits_vegetables.html', student=student)

@app.route('/ukg/body')
def ukg_body():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_body.html', student=student)

@app.route('/ukg/rhymes')
def ukg_rhymes():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_rhymes_songs.html', student=student)

@app.route('/ukg/family')
def ukg_family():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_family.html', student=student)

@app.route('/ukg/days')
def ukg_days():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_days.html', student=student)

@app.route('/ukg/environment')
def ukg_environment():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_environment.html', student=student)

@app.route('/ukg/transport')
def ukg_transport():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_transport.html', student=student)

# UKG Kannada Lessons
@app.route('/ukg/kannada/varnamale')
def ukg_kannada_varnamale():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_varnamale.html', student=student)

@app.route('/ukg/kannada/sankhye')
def ukg_kannada_sankhye():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_sankhye.html', student=student)

@app.route('/ukg/kannada/banna')
def ukg_kannada_banna():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_banna.html', student=student)

@app.route('/ukg/kannada/aakara')
def ukg_kannada_aakara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_aakara.html', student=student)

@app.route('/ukg/kannada/praani')
def ukg_kannada_praani():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_praani.html', student=student)

@app.route('/ukg/kannada/hanna')
def ukg_kannada_hanna():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_hanna.html', student=student)

@app.route('/ukg/kannada/sharira')
def ukg_kannada_sharira():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_sharira.html', student=student)

@app.route('/ukg/kannada/padya')
def ukg_kannada_padya():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_padya.html', student=student)

@app.route('/ukg/kannada/kutumba')
def ukg_kannada_kutumba():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_kutumba.html', student=student)

@app.route('/ukg/kannada/vaara')
def ukg_kannada_vaara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_vaara.html', student=student)

@app.route('/ukg/kannada/parisara')
def ukg_kannada_parisara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_parisara.html', student=student)

@app.route('/ukg/kannada/saarige')
def ukg_kannada_saarige():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_saarige.html', student=student)

# LKG Kannada Lessons
@app.route('/lkg/kannada/varnamale')
def lkg_kannada_varnamale():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_varnamale.html', student=student)

@app.route('/lkg/kannada/sankhye')
def lkg_kannada_sankhye():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_sankhye.html', student=student)

@app.route('/lkg/kannada/banna')
def lkg_kannada_banna():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_banna.html', student=student)

@app.route('/lkg/kannada/aakara')
def lkg_kannada_aakara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_aakara.html', student=student)

@app.route('/lkg/kannada/praani')
def lkg_kannada_praani():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_praani.html', student=student)

@app.route('/lkg/kannada/hanna')
def lkg_kannada_hanna():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_hanna.html', student=student)

@app.route('/lkg/kannada/sharira')
def lkg_kannada_sharira():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_sharira.html', student=student)

@app.route('/lkg/kannada/padya')
def lkg_kannada_padya():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_padya.html', student=student)

@app.route('/lkg/kannada/kutumba')
def lkg_kannada_kutumba():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_kutumba.html', student=student)

@app.route('/lkg/kannada/vaara')
def lkg_kannada_vaara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_vaara.html', student=student)@app.route('/class/1/english')

@app.route('/class/1/english')
def class1_english():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_english_chapters.html', student=student)

@app.route('/class/1/english/chapter/alphabets')
def class1_english_ch1():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_english_ch1.html', student=student)

@app.route('/class/1/english/vegetables')
def class1_english_ch2():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_english_ch2.html', student=student)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database created!")
    import os
    port = int(os.environ.get('PORT', 5001))
    print(f"VidyaAI running on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
