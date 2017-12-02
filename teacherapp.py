import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing


conn = sqlite3.connect('hw13.db')

students = (1, 'John', 'Smith')
quizzes = (1, "Python Basics", 5, "2015-02-05")
student_result = (
    (1, 1, 85),
    (1, 1, 95)
)


with conn:
    cur = conn.cursor()
    # used to delete rows used for testing
    # cur.execute("DELETE FROM student_result")
    # cur.execute("DELETE FROM sqlite_sequence where name = 'students'")
    # cur.execute("DELETE FROM sqlite_sequence where name = 'quizzes'")
    # cur.execute("DELETE FROM quizzes")
    # cur.execute("DELETE FROM students")
    cur.execute("INSERT OR IGNORE INTO students VALUES(?, ?, ?)", students)
    cur.execute("INSERT OR IGNORE INTO quizzes VALUES(?, ?, ?, ?)", quizzes)
    cur.executemany("INSERT OR IGNORE  INTO student_result VALUES(?, ?, ?)", student_result)

DATABASE = 'hw13.db'
DEBUG = True
USERNAME = 'admin'
PASSWORD = 'password'
SECRET_KEY = 'development key'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def teacher_app():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('dashboard'))
    return render_template('login.html', error=error)


@app.route('/dashboard')
def dashboard():
    cur = g.db.execute('select id, first_name, last_name from students')
    cur2 = g.db.execute('select id, subject, number_of_questions, date_of_quiz from quizzes')
    items = cur.fetchall()
    rows = cur2.fetchall()
    return render_template('dashboard.html', items=items, rows=rows)


@app.route('/student_add')
def student_add():
    return render_template('/student/add.html')


@app.route('/quiz_add')
def quiz_add():
    return render_template('/quiz/add.html')


@app.route('/results_add')
def results_add():
    cur = g.db.execute('select id, first_name, last_name from students')
    cur2 = g.db.execute('select id, subject from quizzes')
    row = cur.fetchall()
    row2 = cur2.fetchall()
    return render_template('/results/add.html', row=row, row2=row2)


@app.route('/add', methods=['GET', 'POST'])
def add_entry():
    error = None
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        if request.form['first_name'] == "":
            error = "Please enter student's first name."
            return render_template('/student/add.html', error=error)
        if request.form['last_name'] == "":
            error = "Please enter student's last name."
            return render_template('/student/add.html', error=error)

    g.db.execute('insert into students (first_name, last_name) values (?, ?)',
                 [request.form['first_name'], request.form['last_name']])
    g.db.commit()
    flash('Student was successfully posted')
    return redirect(url_for('dashboard'))


@app.route('/add2', methods=['GET', 'POST'])
def add2_entry():
    error = None
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        if request.form['subject'] == '':
            error = "Please enter the subject."
            return render_template('/quiz/add.html', error=error)
        if request.form['number_of_questions'] == '':
            error = "Please enter the number of questions."
            return render_template('/quiz/add.html', error=error)
        if request.form['date_of_quiz'] == '':
            error = "Please enter the date."
            return render_template('quiz/add.html', error=error)

    g.db.execute('insert into quizzes (subject, number_of_questions, date_of_quiz) values (?, ?, ?)',
                 [request.form['subject'], request.form['number_of_questions'], request.form['date_of_quiz']])
    g.db.commit()
    flash('Quiz was successfully posted')
    return redirect(url_for('dashboard'))


@app.route('/add3', methods=['GET', 'POST'])
def add3_entry():
    error = None
    if not session.get('logged_in'):
        abort(401)
    if request.method == 'POST':
        if request.form['score'] == '':
            error = "Please enter the score."
            return render_template('/results/add.html', error=error)
        if request.form['student'] == 'none':
            error = "Please pick a student from the drop down menu."
            return render_template('/results/add.html', error=error)
        if request.form['subject'] == 'none':
            error = "Please pick a subject from the drop down menu."
            return render_template('/results/add.html', error=error)

    g.db.execute('insert into student_result (student_id, quiz_id, score) values (?, ?, ?)',
                 [request.form['student'], request.form['subject'], request.form['score']])
    g.db.commit()
    flash('Result was successfully posted')
    return redirect(url_for('dashboard'))


@app.route('/student/<id>')
def student_id(id):
    error = None
    cur = g.db.execute('select quiz_id, score from student_result inner join students on students.id = '
                       'student_result.student_id where student_id=?', (id,))
    entries = cur.fetchall()
    if not entries:
        error = "No Results"
        return render_template('student.html', error=error)
    return render_template('student.html', entries=entries)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()