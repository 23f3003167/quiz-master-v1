import os
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from models import db, Admin

load_dotenv()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()
    if not Admin.query.first():
        admin = Admin(username="Admin".lower(), role="admin")
        admin_password = os.getenv("ADMIN_PASSWORD")
        if not admin_password:
            print("ADMIN_PASSWORD is missing in the .env file")
            exit(1)
        admin.password = admin_password
        db.session.add(admin)
        db.session.commit()
    print('Tables created and Admin credentials added.')

if __name__=="__main__":
    app.run(debug=True)