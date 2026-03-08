from flask import Flask
from application.models import db, Users
from application.auth import api as auth_api
from application.admin import api as admin_api
from application.company import api as company_api
from application.student import api as student_api
from application.drives import api as drive_api
from application.applications import api as application_api
from werkzeug.security import generate_password_hash
from flask_login import LoginManager
import os
from datetime import timedelta

login_manager=LoginManager()
login_manager.login_view="auth_api.login"

def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///model.db"
    app.config["SECRET_KEY"]= os.getenv("SECRET_KEY", "dev-only-change-me")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False  # True in HTTPS production
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        if not Users.query.filter_by(username="vaishnavi").first():
            admin=Users(name="Vaishnavi",username="vaishnavi",password=generate_password_hash("vaishnavi",method="pbkdf2:sha256"),role="admin",is_active=True)
            db.session.add(admin)
            db.session.commit()
    app.register_blueprint(auth_api,url_prefix="/")
    app.register_blueprint(admin_api,url_prefix="")
    app.register_blueprint(company_api,url_prefix="")
    app.register_blueprint(student_api,url_prefix="")
    app.register_blueprint(drive_api,url_prefix="/drive")
    app.register_blueprint(application_api,url_prefix="/application")

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    return app

app=create_app()

if __name__ == "__main__":
    app.debug=True
    app.run()
