from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Admin

auth = Blueprint("auth", __name__)
    
@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        qualification = request.form['qualification']
        dob = request.form['dob']

        if not email or not full_name or not password or not qualification or not dob:
            flash("All fields are required!", "danger")
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash("Password must be atleast 6 characters long", "danger")
            return redirect(url_for('auth.register'))
        
        existing_user = User.query.filter_by(username=email).first()
        if existing_user:
            flash("You are Already Registered", "danger")
            return redirect(url_for('auth.login'))
        
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

        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route("/login", methods=['GET', 'POST'])
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
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash("Invalid Credentials", "danger")
                return redirect(url_for('auth.login'))
            
        user = User.query.filter_by(username=email).first()
        if user and user.check_password(password):
            login_user(user)
            session['is_admin'] = False
            return redirect(url_for('user.user_dashboard'))
        flash("Invalid Credentials", "danger")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')
        
@auth.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('auth.login'))
