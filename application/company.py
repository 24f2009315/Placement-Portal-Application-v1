from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Users,Company,db,Student
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint("company_api",__name__)

@api.route("/company_dashboard",methods=["GET","POST","PUT","PATCH","DELETE"])
def company_dashboard():
    if request.method == "GET":
        return render_template("company/dashboard.html")