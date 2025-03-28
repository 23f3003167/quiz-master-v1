from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, User, Subject, Chapter, Quiz, Question, Score
from datetime import datetime
from functools import wraps

admin = Blueprint("admin", __name__)

# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if current_user.role != "admin":
#             return redirect(url_for('auth.login'))
#         return f(*args, **kwargs)
#     return decorated_function

@admin.route("/admin/dashboard", methods=['GET', 'POST'])
@login_required
# #@admin_required
def admin_dashboard():
    subjects = Subject.query.all()
    subject_data = []

    for subject in subjects:
        chapters = Chapter.query.filter_by(subject_id=subject.id).all()
        chapter_data = [
            {
                 "id": chapter.id,
                "name": chapter.name,
                "quiz_count": Quiz.query.filter_by(chapter_id=chapter.id).count()
            }
            for chapter in chapters
        ]
        subject_data.append({"id": subject.id, "name": subject.name, "chapters": chapter_data})

    return render_template('admin/admin_dashboard.html', subject_data=subject_data)

@admin.route("/admin/subjects", methods=['GET', 'POST'])
@login_required
#@admin_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
    
        existing_subject = Subject.query.filter_by(name=name).first()
        if existing_subject:
            flash("Subject already exists!", "danger")
            print("Already exists")
            return redirect(url_for("admin.manage_subjects"))
        
        db.session.add(Subject(name=name, description=description))
        db.session.commit()
        flash("Subject Added Successfully!", "success")
        return redirect(url_for("admin.manage_subjects"))
    
    return render_template("admin/admin_subjects.html", subjects=Subject.query.all())

@admin.route("/admin/subjects/edit/<int:subject_id>", methods=["GET","POST"])
@login_required
#@admin_required
def edit_subject(subject_id):
    
    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        subject.name = request.form["name"]
        subject.description = request.form["description"]
        db.session.commit()
        flash("Updated Successfully!", "success")
        return redirect(url_for("admin.manage_subjects"))
    
    return render_template("admin/edit_subject.html", subject=subject)

@admin.route("/admin/subjects/delete/<int:subject_id>", methods=["POST"])
@login_required
#@admin_required
def delete_subject(subject_id):
    
    subject = Subject.query.get_or_404(subject_id)

    Chapter.query.filter_by(subject_id=subject_id).delete()
    
    db.session.delete(subject)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("admin.manage_subjects"))

@admin.route('/admin/manage_chapters/<int:chapter_id>')
def manage_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    return render_template('manage_chapters.html', chapter=chapter)

@admin.route("/admin/subjects/<int:subject_id>/chapters", methods=["GET","POST"])
@login_required
#@admin_required
def manage_chapters(subject_id):
    
    subject = Subject.query.get_or_404(subject_id)

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        existing_chapter = Chapter.query.filter_by(name=name, subject_id=subject_id).first()
        if existing_chapter:
            flash("Chapter already Exists", "danger")
            return redirect(url_for("admin.manage_chapters", subject_id=subject_id))
        
        db.session.add(Chapter(name=name, description=description, subject_id=subject_id))
        db.session.commit()
        flash("Chapter Added Successfully!","success")
        return redirect(url_for("admin.manage_chapters", subject_id=subject_id))
    
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template("admin/admin_chapters.html", subject=subject, chapters=chapters)

@admin.route("/admin/chapters/edit/<int:chapter_id>", methods=["GET","POST"])
@login_required
#@admin_required
def edit_chapter(chapter_id):
    
    chapter = Chapter.query.get_or_404(chapter_id)

    if request.method == "POST":
        chapter.name = request.form["name"]
        chapter.description = request.form["description"]
        db.session.commit()
        flash("Updated Successfully!", "success")
        return redirect(url_for("admin.manage_chapters", subject_id=chapter.subject_id))
    
    return render_template("admin/edit_chapter.html", chapter=chapter)

@admin.route("/admin/chapters/delete/<int:chapter_id>", methods=["POST"])
@login_required
#@admin_required
def delete_chapter(chapter_id):
    
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("admin.manage_chapters", subject_id=subject_id))

@admin.route("/admin/chapters/<int:chapter_id>/quizzes", methods=["GET","POST"])
@login_required
#@admin_required
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
            return redirect(url_for("admin.manage_quizzes", chapter_id=chapter_id))

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
        return redirect(url_for("admin.manage_quizzes", chapter_id=chapter_id))
    
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template("admin/admin_quizzes.html", chapter=chapter, quizzes=quizzes)

@admin.route("/admin/quizzes/edit/<int:quiz_id>", methods=["GET","POST"])
@login_required
#@admin_required
def edit_quiz(quiz_id):
    
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        quiz.title = request.form["title"]
        quiz.date_of_quiz = datetime.strptime(request.form["date_of_quiz"], "%Y-%m-%d").date()
        quiz.time_duration = request.form["time_duration"]
        quiz.remarks = request.form["remarks"]
        db.session.commit()
        flash("Updated Successfully!", "success")
        return redirect(url_for("admin.manage_quizzes", chapter_id=quiz.chapter_id))
    
    return render_template("admin/edit_quiz.html", quiz=quiz)

@admin.route("/admin/quizzes/delete/<int:quiz_id>", methods=["POST"])
@login_required
#@admin_required
def delete_quiz(quiz_id):
    
    quiz = Quiz.query.get_or_404(quiz_id)

    chapter_id = quiz.chapter_id
    db.session.delete(quiz)
    db.session.commit()
    flash("Deleted Successfully!", "success")
    return redirect(url_for("admin.manage_quizzes", chapter_id=chapter_id))

@admin.route("/admin/quizzes/<int:quiz_id>/questions", methods=["GET","POST"])
@login_required
#@admin_required
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
        return redirect(url_for("admin.manage_questions", quiz_id=quiz_id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template("admin/admin_questions.html", quiz=quiz, questions=questions)

@admin.route("/admin/questions/edit/<int:question_id>", methods=["GET", "POST"])
@login_required
#@admin_required
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
        return redirect(url_for("admin.manage_questions", quiz_id=question.quiz_id))
    
    return render_template("admin/edit_question.html", question=question)

@admin.route("/admin/questions/delete/<int:question_id>", methods=["POST"])
@login_required
#@admin_required
def delete_question(question_id):
    
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    db.session.delete(question)
    db.session.commit()
    flash("Deleted Successfully", "success")
    return redirect(url_for("admin.manage_questions", quiz_id=quiz_id))

@admin.route("/admin/users", methods=['GET'])
@login_required
#@admin_required
def view_users():
    users = User.query.all()
    return render_template("admin/admin_users.html", users=users)

@admin.route("/admin/search", methods=['GET','POST'])
@login_required
#@admin_required
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

    return render_template("admin/admin_search.html", results=results, search_term=search_term)

@admin.route("/admin/quiz-summary", methods=['GET'])
@login_required
#@admin_required
def quiz_summary():
    subjects = Subject.query.all()
    top_scores = {}
    for subject in subjects:
        highest_score = (
            db.session.query(User.full_name, Score.total_scored)
            .join(Score) 
            .join(Quiz, Score.quiz_id == Quiz.id)
            .join(Chapter, Quiz.chapter_id == Chapter.id) 
            .join(Subject, Chapter.subject_id == Subject.id)
            .filter(Subject.id == subject.id)
            .order_by(Score.total_scored.desc())
            .first()
        )
        if highest_score:
            top_scores[subject.name]={
                "user": highest_score[0],
                "score": highest_score[1]
            }
    return render_template("admin/quiz_summary.html", top_scores=top_scores)
