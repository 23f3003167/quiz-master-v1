from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
from models import db, User

auth = Blueprint("auth", __name__)
    
@auth.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        qualification = request.form['qualification']
        dob = request.form['dob']
        
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
        flash("Registered Successfully", "success")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        
        session.clear()
    
        user = User.query.filter_by(username=email, role=role.lower()).first()
        if user and user.check_password(password):
            login_user(user)
            session['is_admin'] = user.role == 'admin'
            
            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            else:
                return redirect(url_for('user.user_dashboard'))
            
        flash("Invalid Credentials", "danger")
        return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')
        
@auth.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for('auth.login'))