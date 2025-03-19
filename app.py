from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from models import db, User, Admin, Subject, Chapter, Quiz, Question
from datetime import datetime

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
        
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
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

@app.route("/admin/dashboard", methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    print(current_user.role)
    if current_user.role != "admin":
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

@app.route("/admin/subjects", methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
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
def edit_subject(subject_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
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
def delete_subject(subject_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
    subject = Subject.query.get_or_404(subject_id)
    
    db.session.delete(subject)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("manage_subjects"))

@app.route("/admin/subjects/<int:subject_id>/chapters", methods=["GET","POST"])
@login_required
def manage_chapters(subject_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
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
def edit_chapter(chapter_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
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
def delete_chapter(chapter_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("manage_chapters", subject_id=subject_id))

@app.route("/admin/chapters/<int:chapter_id>/quizzes", methods=["GET","POST"])
@login_required
def manage_quizzes(chapter_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
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
def edit_quiz(quiz_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
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
def delete_quiz(quiz_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
    quiz = Quiz.query.get_or_404(quiz_id)

    chapter_id = quiz.chapter_id
    db.session.delete(quiz)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("manage_quizzes", chapter_id=chapter_id))

@app.route("/admin/quizzes/<int:quiz_id>/questions", methods=["GET","POST"])
@login_required
def manage_questions(quiz_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
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
def edit_question(question_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
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
def delete_question(question_id):
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Deleted Successfully", "success")
    return redirect(url_for("manage_questions", quiz_id=quiz_id))

@app.route("/admin/users", methods=['GET'])
@login_required
def view_users():
    if current_user.role != "admin":
        return redirect(url_for("user_dashboard"))
    
    users = User.query.all()
    return render_template("admin_users.html", users=users)

@app.route("/user/dashboard", methods=['GET', 'POST'])
@login_required
def user_dashboard():
    print(current_user.role)
    if current_user.role != "user":
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

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