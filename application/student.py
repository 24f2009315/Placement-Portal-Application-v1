from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Users,Company,db,Student
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint("student_api",__name__)

@api.route("/student_dashboard",methods=["GET","POST","PUT","PATCH","DELETE"])
def student_dashboard():
    if request.method == "GET":
        return render_template("student/dashboard.html")