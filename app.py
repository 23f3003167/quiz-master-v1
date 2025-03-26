from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from models import db, User, Admin, Subject, Chapter, Quiz, Question, Score
from datetime import datetime, date
from functools import wraps
import pytz

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "abcdefghijklmnopqrstuvwxyz"

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    if 'is_admin' in session and session['is_admin']:
        return Admin.query.get(int(user_id))
    return User.query.get(int(user_id))
    
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        qualification = request.form['qualification']
        dob = request.form['dob']

        if not email or not full_name or not password or not qualification or not dob:
            flash("All fields are required!", "danger")
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash("Password must be atleast 6 characters long", "danger")
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            flash("You are Already Registered", "danger")
            return redirect(url_for('login'))
        
        new_user = User(
            username=email,
            full_name=full_name,
            qualification=qualification,
            dob=dob,
            role='user'
        )

        new_user.password = password
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        
        session.clear()
    
        if role.lower() == 'admin':
            admin = Admin.query.filter_by(username=email).first()
            if admin and admin.check_password(password):
                login_user(admin)
                print(current_user)
                session['is_admin'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                flash("Invalid Credentials", "danger")
                return redirect(url_for('login'))
            
        user = User.query.filter_by(username=email).first()
        if user and user.check_password(password):
            login_user(user)
            print(current_user)
            session['is_admin'] = False
            return redirect(url_for('user_dashboard'))
        flash("Invalid Credentials", "danger")
        return redirect(url_for('login'))
    
    return render_template('login.html')
        
@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != "admin":
            flash("Unauthorized access!", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/dashboard", methods=['GET', 'POST'])
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route("/admin/subjects", methods=['GET', 'POST'])
@login_required
@admin_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
    
        existing_subject = Subject.query.filter_by(name=name).first()
        if existing_subject:
            flash("Subject already exists!", "danger")
            return redirect(url_for("manage_students"))
        
        db.session.add(Subject(name=name, description=description))
        db.session.commit()
        flash("Subject Added Successfully!", "success")
        return redirect(url_for("manage_subjects"))
    
    return render_template("admin_subjects.html", subjects=Subject.query.all())

@app.route("/admin/subjects/edit/<int:subject_id>", methods=["GET","POST"])
@login_required
@admin_required
def edit_subject(subject_id):
    
    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        subject.name = request.form["name"]
        subject.description = request.form["description"]
        db.session.commit()
        flash("Updated Successfully!", "success")
        return redirect(url_for("manage_subjects"))
    
    return render_template("edit_subject.html", subject=subject)

@app.route("/admin/subjects/delete/<int:subject_id>", methods=["POST"])
@login_required
@admin_required
def delete_subject(subject_id):
    
    subject = Subject.query.get_or_404(subject_id)
    
    db.session.delete(subject)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("manage_subjects"))

@app.route("/admin/subjects/<int:subject_id>/chapters", methods=["GET","POST"])
@login_required
@admin_required
def manage_chapters(subject_id):
    
    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        existing_chapter = Chapter.query.filter_by(name=name, subject_id=subject_id).first()
        if existing_chapter:
            flash("Chapter already Exists", "danger")
            return redirect(url_for("manage_chapters", subject_id=subject_id))
        
        db.session.add(Chapter(name=name, description=description, subject_id=subject_id))
        db.session.commit()
        flash("Chapter Added Successfully!","success")
        return redirect(url_for("manage_chapters", subject_id=subject_id))
    
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template("admin_chapters.html", subject=subject, chapters=chapters)

@app.route("/admin/chapters/edit/<int:chapter_id>", methods=["GET","POST"])
@login_required
@admin_required
def edit_chapter(chapter_id):
    
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == "POST":
        chapter.name = request.form["name"]
        chapter.description = request.form["description"]
        db.session.commit()
        flash("Updated Successfully!", "success")
        return redirect(url_for("manage_subjects", subject_id=chapter.subject_id))
    
    return render_template("edit_chapter.html", chapter=chapter)

@app.route("/admin/chapters/delete/<int:chapter_id>", methods=["POST"])
@login_required
@admin_required
def delete_chapter(chapter_id):
    
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("manage_chapters", subject_id=subject_id))

@app.route("/admin/chapters/<int:chapter_id>/quizzes", methods=["GET","POST"])
@login_required
@admin_required
def manage_quizzes(chapter_id):
    
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == "POST":
        title = request.form["title"]
        date_of_quiz = datetime.strptime(request.form["date_of_quiz"], "%Y-%m-%d").date()
        time_duration = request.form["time_duration"]
        remarks = request.form["remarks"]

        existing_quiz = Quiz.query.filter_by(title=title, chapter_id=chapter_id).first()
        if existing_quiz:
            flash("Quiz Title already Exists", "danger")
            return redirect(url_for("manage_quizzes", chapter_id=chapter_id))

        new_quiz = Quiz(
            chapter_id=chapter_id,
            title=title,
            date_of_quiz=date_of_quiz,
            time_duration=time_duration,
            remarks=remarks
        )
        db.session.add(new_quiz)
        db.session.commit()
        print("Success")
        flash("Quiz added Successfully!", "success")
        return redirect(url_for("manage_quizzes", chapter_id=chapter_id))
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template("admin_quizzes.html", chapter=chapter, quizzes=quizzes)

@app.route("/admin/quizzes/edit/<int:quiz_id>", methods=["GET","POST"])
@login_required
@admin_required
def edit_quiz(quiz_id):
    
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        quiz.title = request.form["title"]
        quiz.date_of_quiz = datetime.strptime(request.form["date_of_quiz"], "%Y-%m-%d").date()
        quiz.time_duration = request.form["time_duration"]
        quiz.remarks = request.form["remarks"]
        db.session.commit()
        flash("Updated Successfully!", "success")
        return redirect(url_for("manage_quizzes", chapter_id=quiz.chapter_id))
    
    return render_template("edit_quiz.html", quiz=quiz)

@app.route("/admin/quizzes/delete/<int:quiz_id>", methods=["POST"])
@login_required
@admin_required
def delete_quiz(quiz_id):
    
    quiz = Quiz.query.get_or_404(quiz_id)

    chapter_id = quiz.chapter_id
    db.session.delete(quiz)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("manage_quizzes", chapter_id=chapter_id))

@app.route("/admin/quizzes/<int:quiz_id>/questions", methods=["GET","POST"])
@login_required
@admin_required
def manage_questions(quiz_id):
    
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        question_statement = request.form["question_statement"]
        option_1 = request.form["option_1"]
        option_2 = request.form["option_2"]
        option_3 = request.form["option_3"]
        option_4 = request.form["option_4"]
        correct_option = int(request.form["correct_option"])

        new_question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option_1=option_1,
            option_2=option_2,
            option_3=option_3,
            option_4=option_4,
            correct_option=correct_option
        )

        db.session.add(new_question)
        db.session.commit()
        flash("Question Added Successfully!", "success")
        return redirect(url_for("manage_questions", quiz_id=quiz_id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template("admin_questions.html", quiz=quiz, questions=questions)

@app.route("/admin/questions/edit/<int:question_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_question(question_id):
    
    question = Question.query.get_or_404(question_id)

    if request.method=="POST":
        question.question_statement = request.form["question_statement"]
        question.option_1 = request.form["option_1"]
        question.option_2 = request.form["option_2"]
        question.option_3 = request.form["option_3"]
        question.option_4 = request.form["option_4"]
        question.correct_option = int(request.form["correct_option"])
        db.session.commit()
        flash("Question updated Successfully", "success")
        return redirect(url_for("manage_questions", quiz_id=question.quiz_id))
    
    return render_template("edit_question.html", question=question)

@app.route("/admin/questions/delete/<int:question_id>", methods=["POST"])
@login_required
@admin_required
def delete_question(question_id):
    
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Deleted Successfully", "success")
    return redirect(url_for("manage_questions", quiz_id=quiz_id))

@app.route("/admin/users", methods=['GET'])
@login_required
@admin_required
def view_users():
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@app.route("/admin/search", methods=['GET','POST'])
@login_required
@admin_required
def admin_search():
    
    results = []
    search_term = request.form.get("search_term","").strip()
    filter_by = request.form.getlist("filter_by")

    if request.method == "POST" and search_term:
        if "users" in filter_by:
            results.extend(User.query.filter(User.full_name.ilike(f"%{search_term}%")).all())
        if "subjects" in filter_by:
            results.extend(Subject.query.filter(Subject.name.ilike(f"%{search_term}%")).all())
        if "quizzes" in filter_by:
            results.extend(Quiz.query.filter(Quiz.title.ilike(f"%{search_term}%")).all())
        if "questions" in filter_by:
            results.extend(Question.query.filter(Question.question_statement.ilike(f"%{search_term}%")).all())

    return render_template("admin_search.html", results=results, search_term=search_term)

@app.route("/user/dashboard", methods=['GET', 'POST'])
@login_required
def user_dashboard():
    print(current_user.role)
    if current_user.role != "user":
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

@app.route("/user/subjects", methods=['GET'])
@login_required
def user_subjects():
    if current_user.role != "user":
        return redirect(url_for('admin_dashboard'))
    
    subjects = Subject.query.all()
    return render_template('user_subjects.html', subjects=subjects)

@app.route("/user/subjects/<int:subject_id>/quizzes", methods=['GET'])
@login_required
def user_quizzes(subject_id):
    if current_user.role != "user":
        return redirect(url_for('admin_dashboard'))
    subject = Subject.query.get_or_404(subject_id)
    quizzes = Quiz.query.filter_by(chapter_id=subject.id).all()
    today = date.today()

    return render_template('user_quizzes.html',subject=subject, quizzes=quizzes, today=today)

@app.route("/user/quizzes/<int:quiz_id>/attempt",methods=['GET','POST'])
@login_required
def attempt_quiz(quiz_id):
    if current_user.role != "user":
        return redirect(url_for('admin_dashboard'))
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    ist = pytz.timezone('Asia/Kolkata')

    today = date.today()
    if quiz.date_of_quiz != today:
        flash(f"This quiz is only available on {quiz.date_of_quiz.strftime('%d-%m-%Y')}", "danger")
        return redirect(url_for("user_quizzes", subject_id=quiz.chapter.subject_id))

    if request.method == 'GET':
        session['quiz_start_time'] = datetime.now().isoformat()

    if request.method == 'POST':
        score = 0
        for question in questions:
            selected_option = request.form.get(f'question_{question.id}')
            if selected_option and int(selected_option) == question.correct_option:
                score += 1

        start_time = session.get('quiz_start_time')
        print(start_time)
        end_time = datetime.now()
        print(end_time)

        if start_time:
            start_time = datetime.fromisoformat(start_time)
            time_taken = (end_time - start_time).seconds
            minutes = time_taken // 60
            seconds = time_taken % 60
        else:
            minutes, seconds = 0,0

        new_score = Score(
            quiz_id=quiz_id,
            user_id=current_user.id,
            time_stamp_of_attempt=datetime.now(),
            total_scored=score,
            completion_minutes=minutes,
            completion_seconds=seconds
        )
        db.session.add(new_score)
        db.session.commit()

        flash(f'Quiz Completed! Your Score: {score}/{len(questions)} in {minutes} minutes {seconds} seconds', "success")
        return redirect(url_for('user_dashboard'))
    
    return render_template('attempt_quiz.html', quiz=quiz, questions=questions)

@app.route("/user/scores", methods=['GET'])
@login_required
def view_scores():
    if current_user.role != "user":
        return redirect(url_for("admin_dashboard"))
    
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp_of_attempt.desc()).all()
    return render_template("user_scores.html", scores=scores)

@app.route("/user/search", methods=['GET','POST'])
@login_required
def user_search():
    if current_user.role != "user":
        return redirect(url_for("admin_dashboard"))
    
    results = []
    search_term = request.form.get("search_term","").strip()
    filter_by = request.form.getlist("filter_by")

    if request.method == "POST" and search_term:
        if "subjects" in filter_by:
            results.extend(Subject.query.filter(Subject.name.ilike(f"%{search_term}%")).all())
        if "quizzes" in filter_by:
            results.extend(Quiz.query.filter(Quiz.title.ilike(f"%{search_term}%")).all())

    return render_template("user_search.html", results=results, search_term=search_term)

@app.route("/user/quiz-summary", methods=['GET'])
@login_required
def quiz_summary():
    if current_user.role != "user":
        return redirect(url_for("admin_dashboard"))
    
    scores = Score.query.filter_by(user_id=current_user.id).all()

    quiz_titles = [s.quiz.title for s in scores]
    scores_list = [s.total_scored for s in scores]

    return render_template("quiz_summary.html", quiz_titles=quiz_titles, scores_list=scores_list)

if __name__=="__main__":
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            admin = Admin(username="admin@gmail.com", role="admin")
            admin.password = "admin@2005"
            db.session.add(admin)
            db.session.commit()
            print('Admin credentials added.')
    app.run(debug=True)