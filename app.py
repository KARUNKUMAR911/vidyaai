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

class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    grade = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    lesson = db.Column(db.String(80), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    stars = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'grade', 'subject', 'lesson', name='uq_lesson_progress'),
    )

# Canonical lesson lists used to compute subject totals.
GRADE1_ENGLISH_LESSONS = [
    'alphabets',
    'fruits',
    'vegetables',
    'animals',
    'body',
    'story1',
    'school',
    'family',
    'shapes',
    'habits',
    'transport',
    'numbers',
    'story2',
]


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
    # Kannada-medium Class 1 dashboard (overall).
    return render_template('class1/class1_dashboard_kannada.html', student=student)

@app.route('/class/1/kannada/chapters')
def class1_kannada_chapters():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    # Kannada subject chapter index (used by both English-medium and Kannada-medium).
    return render_template('class1/class1_kannada_chapters.html', student=student)

@app.route('/class/1/kannada/maths')
def class1_kannada_maths_chapters():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_kannada_maths_chapters.html', student=student)

@app.route('/class/1/kannada/maths/lesson<int:lesson_num>')
def class1_kannada_maths_lesson(lesson_num: int):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    # Lessons are stored as templates/class1_kannada_maths_lesson{N}.html
    if lesson_num < 1 or lesson_num > 19:
        return redirect('/class/1/kannada/maths')
    return render_template(f'class1_kannada_maths_lesson{lesson_num}.html', student=student)

# Kannada-medium EVS index (lessons currently reuse the English-medium EVS lesson pages)
@app.route('/class/1/kannada/evs')
def class1_kannada_evs_chapters():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_kannada_evs_chapters.html', student=student)

@app.route('/class/1/kannada/evs/lesson<int:lesson_num>')
def class1_kannada_evs_lesson(lesson_num: int):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])

    # Map "lesson number" to templates. Kannada lessons exist for 1-9; the rest
    # currently fall back to the English-medium EVS pages so navigation works.
    lesson_templates = {
        1:  'class1/class1_kannada_evs_chapter1_animals.html',
        2:  'class1/class1_kannada_evs_chapter2_plants.html',
        3:  'class1/class1_kannada_evs_chapter3_water.html',
        4:  'class1/class1_kannada_evs_chapter4_food.html',
        5:  'class1/class1_kannada_evs_chapter5_food_needed.html',
        6:  'class1/class1_kannada_evs_chapter6_my_home.html',
        7:  'class1/class1_kannada_evs_chapter7_swachha_abhyasagalu.html',
        8:  'class1/class1_kannada_evs_chapter8_surakshate_shistu.html',
        9:  'class1/class1_kannada_evs_chapter9_vehicles.html',
        10: 'class1/class1_evs_chapter10_family.html',
        11: 'class1/class1_evs_chapter11_neighbourhood.html',
        12: 'class1/class1_evs_chapter12_play_the_game.html',
        13: 'class1/class1_evs_chapter13_i_need_these.html',
        14: 'class1/class1_evs_chapter14_heavenly_friends.html',
        15: 'class1/class1_evs_chapter15_around_us.html',
    }

    tpl = lesson_templates.get(lesson_num)
    if not tpl:
        return redirect('/class/1/kannada/evs')
    return render_template(tpl, student=student)

# Class 1 Kannada lessons
@app.route('/class/1/kannada/vandane')
def class1_kannada_vandane():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_kannada_ch1.html', student=student)

@app.route('/class/1/kannada/sahakara')
def class1_kannada_sahakara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch2_sahakara.html', student=student)

@app.route('/class/1/kannada/ootada-eta')
def class1_kannada_ootada_eta():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch3.html', student=student)

@app.route('/class/1/kannada/hodeota')
def class1_kannada_hodeota():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch4.html', student=student)

@app.route('/class/1/kannada/rekha')
def class1_kannada_rekha():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('kannada_ch5_rekhaabhyasa.html', student=student)

@app.route('/class/1/kannada/besige')
def class1_kannada_besige():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch6_besige_raje.html', student=student)

@app.route('/class/1/kannada/koti-akilu')
def class1_kannada_koti_akilu():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('kannada_ch7_kooti_alilu.html', student=student)

@app.route('/class/1/kannada/pada-odu')
def class1_kannada_pada_odu():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch8.html', student=student)

@app.route('/class/1/kannada/chandira')
def class1_kannada_chandira():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch9.html', student=student)

@app.route('/class/1/kannada/gunita')
def class1_kannada_gunita():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch10.html', student=student)

@app.route('/class/1/kannada/vivekananda')
def class1_kannada_vivekananda():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch11.html', student=student)

@app.route('/class/1/kannada/ottu')
def class1_kannada_ottu():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch12.html', student=student)

@app.route('/class/1/kannada/abbasa')
def class1_kannada_abbasa():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch13.html', student=student)

@app.route('/class/1/kannada/molada-mari')
def class1_kannada_molada_mari():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch14.html', student=student)

@app.route('/class/1/kannada/shankara')
def class1_kannada_shankara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch15.html', student=student)

@app.route('/class/1/kannada/kai-toleya')
def class1_kannada_kai_toleya():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch16.html', student=student)

@app.route('/class/1/kannada/sigadi')
def class1_kannada_sigadi():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1_kannada_ch17.html', student=student)

@app.route('/class/1/maths')
def class1_maths():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_chapters.html', student=student)

@app.route('/class/1/maths/spatial')
def class1_maths_spatial():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch1_spatial.html', student=student)

@app.route('/class/1/maths/solids')
def class1_maths_solids():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch2_solids.html', student=student)

@app.route('/class/1/maths/digits')
def class1_maths_digits():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch3_digits.html', student=student)

@app.route('/class/1/maths/zero')
def class1_maths_zero():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch4_zero.html', student=student)

@app.route('/class/1/maths/addition1')
def class1_maths_addition1():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch5_addition.html', student=student)

@app.route('/class/1/maths/subtraction1')
def class1_maths_subtraction1():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch6_subtraction.html', student=student)

@app.route('/class/1/maths/number10')
def class1_maths_number10():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch7_number10.html', student=student)

@app.route('/class/1/maths/units-tens')
def class1_maths_units_tens():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch8_units_and_tens.html', student=student)

@app.route('/class/1/maths/numbers11to20')
def class1_maths_numbers11to20():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch9_numbers_11_to_20.html', student=student)

@app.route('/class/1/maths/addition2')
def class1_maths_addition2():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch10_addition_sum_not_more_than_20.html', student=student)

@app.route('/class/1/maths/subtraction2')
def class1_maths_subtraction2():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch11_subtraction_difference_not_more_than_20.html', student=student)

@app.route('/class/1/maths/numbers21to99')
def class1_maths_numbers21to99():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch12_numbers_21_to_99.html', student=student)

@app.route('/class/1/maths/mental-arithmetic')
def class1_maths_mental_arithmetic():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch13_mental_arithmetic.html', student=student)

@app.route('/class/1/maths/money')
def class1_maths_money():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch14_money.html', student=student)

@app.route('/class/1/maths/length')
def class1_maths_length():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch15_length.html', student=student)

@app.route('/class/1/maths/weight')
def class1_maths_weight():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch16_weight.html', student=student)

@app.route('/class/1/maths/time')
def class1_maths_time():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch17_time.html', student=student)

@app.route('/class/1/maths/data-handling')
def class1_maths_data_handling():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch18_data_handling.html', student=student)

@app.route('/class/1/maths/patterns')
def class1_maths_patterns():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_maths_ch19_patterns.html', student=student)

@app.route('/class/1/evs')
def class1_evs():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapters.html', student=student)

# Class 1 EVS lessons
@app.route('/class/1/evs/animals')
def class1_evs_animals():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter1.html', student=student)

@app.route('/class/1/evs/plants')
def class1_evs_plants():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter2.html', student=student)

@app.route('/class/1/evs/water')
def class1_evs_water():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter3.html', student=student)

@app.route('/class/1/evs/delicious-food')
def class1_evs_delicious_food():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter4.html', student=student)

@app.route('/class/1/evs/do-we-need-food')
def class1_evs_do_we_need_food():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter5.html', student=student)

@app.route('/class/1/evs/my-house')
def class1_evs_my_house():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter6_my_house.html', student=student)

@app.route('/class/1/evs/clean-habits')
def class1_evs_clean_habits():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter7_clean_habits.html', student=student)

@app.route('/class/1/evs/safety-discipline')
def class1_evs_safety_discipline():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter8_safety_and_discipline.html', student=student)

@app.route('/class/1/evs/transportation')
def class1_evs_transportation():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter9_transportation.html', student=student)

@app.route('/class/1/evs/i-and-my-family')
def class1_evs_i_and_my_family():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter10_family.html', student=student)

@app.route('/class/1/evs/neighbourhood')
def class1_evs_neighbourhood():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter11_neighbourhood.html', student=student)

@app.route('/class/1/evs/play-the-game')
def class1_evs_play_the_game():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter12_play_the_game.html', student=student)

@app.route('/class/1/evs/i-need-these')
def class1_evs_i_need_these():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter13_i_need_these.html', student=student)

@app.route('/class/1/evs/heavenly-friends')
def class1_evs_heavenly_friends():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter14_heavenly_friends.html', student=student)

@app.route('/class/1/evs/around-us')
def class1_evs_around_us():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_evs_chapter15_around_us.html', student=student)

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

@app.route('/api/lesson_progress/load', methods=['GET'])
def load_lesson_progress():
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'})

    grade = request.args.get('grade', session.get('student_grade'))
    subject = request.args.get('subject')
    if not subject:
        return jsonify({'error': 'Missing subject'}), 400

    lessons = None
    if str(grade) == '1' and subject == 'english':
        lessons = GRADE1_ENGLISH_LESSONS

    if lessons is None:
        return jsonify({'subject': subject, 'grade': grade, 'totalLessons': 0, 'lessons': {}})

    rows = LessonProgress.query.filter_by(
        student_id=session['student_id'],
        grade=str(grade),
        subject=subject
    ).all()
    lesson_map = {r.lesson: {'completed': bool(r.completed), 'stars': int(r.stars or 0)} for r in rows}

    # Ensure stable keys for all lessons even if not saved yet.
    normalized = {k: lesson_map.get(k, {'completed': False, 'stars': 0}) for k in lessons}
    return jsonify({'subject': subject, 'grade': str(grade), 'totalLessons': len(lessons), 'lessons': normalized})

@app.route('/api/lesson_progress/save', methods=['POST'])
def save_lesson_progress():
    if 'student_id' not in session:
        return jsonify({'error': 'Not logged in'})

    data = request.json or {}
    grade = str(data.get('grade', session.get('student_grade')))
    subject = data.get('subject')
    lesson = data.get('lesson')
    completed = bool(data.get('completed', False))
    stars = int(data.get('stars', 0) or 0)

    if not subject or not lesson:
        return jsonify({'error': 'Missing subject or lesson'}), 400

    # Upsert lesson progress.
    row = LessonProgress.query.filter_by(
        student_id=session['student_id'],
        grade=grade,
        subject=subject,
        lesson=lesson
    ).first()

    if row:
        # Never "uncomplete" and never reduce stars when replaying.
        row.completed = bool(row.completed) or completed
        row.stars = max(int(row.stars or 0), stars)
        row.last_updated = datetime.utcnow()
    else:
        row = LessonProgress(
            student_id=session['student_id'],
            grade=grade,
            subject=subject,
            lesson=lesson,
            completed=completed,
            stars=stars,
            last_updated=datetime.utcnow()
        )
        db.session.add(row)

    # If we know the official lesson list, also keep the aggregated Progress row in sync.
    lessons = None
    if grade == '1' and subject == 'english':
        lessons = GRADE1_ENGLISH_LESSONS

    if lessons is not None:
        rows = LessonProgress.query.filter_by(
            student_id=session['student_id'],
            grade=grade,
            subject=subject
        ).all()
        by_lesson = {r.lesson: r for r in rows}
        completed_count = sum(1 for k in lessons if k in by_lesson and bool(by_lesson[k].completed))
        stars_total = sum(int(by_lesson[k].stars or 0) for k in lessons if k in by_lesson)

        prog = Progress.query.filter_by(
            student_id=session['student_id'],
            grade=grade,
            subject=subject
        ).first()
        if prog:
            prog.completed = completed_count
            prog.total = len(lessons)
            prog.stars = stars_total
            prog.last_updated = datetime.utcnow()
        else:
            prog = Progress(
                student_id=session['student_id'],
                grade=grade,
                subject=subject,
                completed=completed_count,
                total=len(lessons),
                stars=stars_total,
                last_updated=datetime.utcnow()
            )
            db.session.add(prog)

    db.session.commit()
    return jsonify({'success': True})

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
    # Keep the URL stable while allowing us to organize templates by grade.
    return render_template('class1/class1_dashboard.html', student=student)

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
    return render_template('ukg_days_months.html', student=student)

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
    return render_template('ukg_kannada_numbers.html', student=student)

@app.route('/ukg/kannada/banna')
def ukg_kannada_banna():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_colors.html', student=student)

@app.route('/ukg/kannada/aakara')
def ukg_kannada_aakara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_shapes.html', student=student)

@app.route('/ukg/kannada/praani')
def ukg_kannada_praani():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_animals.html', student=student)

@app.route('/ukg/kannada/hanna')
def ukg_kannada_hanna():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_fruits_vegetables.html', student=student)

@app.route('/ukg/kannada/sharira')
def ukg_kannada_sharira():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_body_parts.html', student=student)

@app.route('/ukg/kannada/padya')
def ukg_kannada_padya():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_rhymes.html', student=student)

@app.route('/ukg/kannada/kutumba')
def ukg_kannada_kutumba():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_family.html', student=student)

@app.route('/ukg/kannada/vaara')
def ukg_kannada_vaara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_days_months_seasons.html', student=student)

@app.route('/ukg/kannada/parisara')
def ukg_kannada_parisara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_nature.html', student=student)

@app.route('/ukg/kannada/saarige')
def ukg_kannada_saarige():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('ukg_kannada_vehicles.html', student=student)

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
    return render_template('lkg_kannada_numbers.html', student=student)

@app.route('/lkg/kannada/banna')
def lkg_kannada_banna():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_colors.html', student=student)

@app.route('/lkg/kannada/aakara')
def lkg_kannada_aakara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_shapes.html', student=student)

@app.route('/lkg/kannada/praani')
def lkg_kannada_praani():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_animals.html', student=student)

@app.route('/lkg/kannada/hanna')
def lkg_kannada_hanna():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_fruits_vegetables.html', student=student)

@app.route('/lkg/kannada/sharira')
def lkg_kannada_sharira():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_body_parts.html', student=student)

@app.route('/lkg/kannada/padya')
def lkg_kannada_padya():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_rhymes.html', student=student)

@app.route('/lkg/kannada/kutumba')
def lkg_kannada_kutumba():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_family.html', student=student)

@app.route('/lkg/kannada/vaara')
def lkg_kannada_vaara():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('lkg_kannada_days_months.html', student=student)

@app.route('/class/1/english')

@app.route('/class/1/english')
def class1_english():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_chapters.html', student=student)

@app.route('/class/1/english/alphabets')
@app.route('/class/1/english/chapter/alphabets')
def class1_english_ch1():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_alphabets.html', student=student)

@app.route('/class/1/english/fruits')
def class1_english_ch2():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch1.html', student=student)

@app.route('/class/1/english/vegetables')
def class1_english_vegetables():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch2.html', student=student)

@app.route('/class/1/english/animals')
def class1_english_animals():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch3.html', student=student)

@app.route('/class/1/english/body')
def class1_english_body():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch4.html', student=student)

@app.route('/class/1/english/story1')
def class1_english_story1():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('stories_for_listening.html', student=student)

@app.route('/class/1/english/school')
def class1_english_school():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch5_my_school.html', student=student)

@app.route('/class/1/english/family')
def class1_english_family():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch6_family.html', student=student)

@app.route('/class/1/english/shapes')
def class1_english_shapes():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch7_shapes_colours.html', student=student)

@app.route('/class/1/english/habits')
def class1_english_habits():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch8_good_habits.html', student=student)

@app.route('/class/1/english/transport')
def class1_english_transport():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch9_means_of_transport.html', student=student)

@app.route('/class/1/english/numbers')
def class1_english_numbers():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('class1/class1_english_ch10_numbers_and_days.html', student=student)

@app.route('/class/1/english/story2')
def class1_english_story2():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student = Student.query.get(session['student_id'])
    return render_template('stories_for_listening2.html', student=student)



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database created!")
    import os
    port = int(os.environ.get('PORT', 5001))
    print(f"VidyaAI running on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
