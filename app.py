from flask import Flask
from application.models import db , Users
from application.auth import api as auth_api
from application.admin import api as admin_api
from application.company import api as company_api
from application.student import api as student_api
from werkzeug.security import generate_password_hash
from flask_login import LoginManager

login_manager=LoginManager()
login_manager.login_view="auth_api.login"

def create_app():
    app=Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///model.db"
    app.config["SECRET_KEY"]="dnkpitwxjkuhvhfxsggnlhfhg"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        db.create_all()
        if not Users.query.filter_by(username="vaishnavi").first():
            admin=Users(name="Vaishnavi",username="vaishnavi",password=generate_password_hash("vaishnavi",method="pbkdf2:sha256"),role="admin",is_active=True)
            db.session.add(admin)
            db.session.commit()
    app.register_blueprint(auth_api)
    app.register_blueprint(admin_api)
    app.register_blueprint(company_api)
    app.register_blueprint(student_api)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))
    return app

app=create_app()

if __name__ == "__main__":
    app.debug=True
    app.run()