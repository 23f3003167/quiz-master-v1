from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import db, Subject, Chapter, Quiz, Question, Score
from datetime import datetime, date
import pytz
from functools import wraps

user = Blueprint("user", __name__)

@user.route("/user/dashboard", methods=['GET', 'POST'])
@login_required
def user_dashboard():
    quizzes = Quiz.query.join(Chapter).join(Subject).all()
    today = date.today()
    quiz_question_count = {quiz.id: Question.query.filter_by(quiz_id=quiz.id).count() for quiz in quizzes}
    return render_template('user/user_dashboard.html', quizzes=quizzes, quiz_question_count=quiz_question_count, today=today)

# @user.route("/user/subjects", methods=['GET'])
# @login_required
# #@user_required
# def user_subjects():
    
#     subjects = Subject.query.all()
#     return render_template('user/user_subjects.html', subjects=subjects)

# @user.route("/user/subjects/<int:subject_id>/quizzes", methods=['GET'])
# @login_required
# #@user_required
# def user_quizzes(subject_id):
    
#     subject = Subject.query.get_or_404(subject_id)
#     quizzes = Quiz.query.filter_by(chapter_id=subject.id).all()
#     today = date.today()

#     return render_template('user/user_quizzes.html',subject=subject, quizzes=quizzes, today=today)

@user.route("/user/quizzes/<int:quiz_id>/attempt",methods=['GET','POST'])
@login_required
def attempt_quiz(quiz_id):
    
    
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    ist = pytz.timezone('Asia/Kolkata')

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
        return redirect(url_for('user.user_dashboard'))
    
    return render_template('user/attempt_quiz.html', quiz=quiz, questions=questions)

@user.route("/user/scores", methods=['GET'])
@login_required
def view_scores():
    
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp_of_attempt.desc()).all()
    quizzes = Quiz.query.all()
    quiz_question_count = {quiz.id: Question.query.filter_by(quiz_id=quiz.id).count() for quiz in quizzes}
    return render_template("user/user_scores.html", scores=scores, quiz_question_count=quiz_question_count)

@user.route("/user/search", methods=['GET','POST'])
@login_required
#@user_required
def user_search():
    
    results = []
    search_term = request.form.get("search_term","").strip()
    filter_by = request.form.getlist("filter_by")

    if request.method == "POST" and search_term:
        if "subjects" in filter_by:
            results.extend(Subject.query.filter(Subject.name.ilike(f"%{search_term}%")).all())
        if "quizzes" in filter_by:
            results.extend(Quiz.query.filter(Quiz.title.ilike(f"%{search_term}%")).all())

    return render_template("user/user_search.html", results=results, search_term=search_term)

@user.route("/user/quiz-summary", methods=['GET'])
@login_required
#@user_required
def quiz_summary():
    
    scores = Score.query.filter_by(user_id=current_user.id).all()

    highest_scores = {}
    for score in scores:
        quiz_title = score.quiz.title
        if quiz_title in highest_scores:
            highest_scores[quiz_title] = max(highest_scores[quiz_title], score.total_scored)
        else:
            highest_scores[quiz_title] = score.total_scored

    quiz_titles = list(highest_scores.keys())
    scores_list = list(highest_scores.values())

    return render_template("user/quiz_summary.html", quiz_titles=quiz_titles, scores_list=scores_list)