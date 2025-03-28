from flask import Flask, session, redirect, url_for
from flask_login import LoginManager
from flask_migrate import Migrate
from models import db, User, Admin
from controllers.auth import auth
from controllers.admin import admin
from controllers.user import user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "abcdefghijklmnopqrstuvwxyz"

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    if 'is_admin' in session and session['is_admin']:
        return db.session.get(Admin, int(user_id))
    return db.session.get(User, int(user_id))

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(user)

@app.route("/")
def index():
    return redirect(url_for("auth.login"))

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