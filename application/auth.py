from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for
from application.models import Users,Company,db,Student
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint("auth_api",__name__)

@api.route("/",methods=["GET"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
@api.route("/login",methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Enter both username and password",category="warning")
            return redirect(url_for("auth_api.login"))
        
        user=Users.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password,password):
            flash("Invalid User",category="invalid-email")
            return redirect(url_for("auth_api.login"))
        
        if not user.is_active:
            flash("Account disabled", category="warning")
            return redirect(url_for("auth_api.login"))
    
        if user.role == "company":
            company=Company.query.filter_by(user_id=user.user_id).first()
            if company.status != "approved":
                flash("you cant login until approved")
                return redirect(url_for("auth_api.login"))
        
        login_user(user)
        flash("Login Successful",category="success")

        if user.role == "student":
            return render_template("student_api.student_dashboard")
        elif user.role == "company":
            if company.status == "approved":
                return render_template("company_api.company_dashboard")
            else:
                return redirect(url_for("auth_api.login"))
        return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/company_signup",methods=["GET","POST"])
def company_signup():
    if request.method == "GET":
        return render_template("company/signup.html")
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        hr_contact = request.form.get("hr_contact")
        website = request.form.get("website")

        company=Users.query.filter_by(username=username).first()

        if company:
            flash("username already taken",category="inavlid-email")
            return redirect(url_for("auth_api.company_signup"))
        
        if not name or not username:
            flash("both name and username are reuqired",category="warning")
            return render_template("company/signup.html")
        
        new_user = Users(name=name,username=username,password=generate_password_hash(password,method="pbkdf2:sha256"),role="company",is_active=True)
        db.session.add(new_user)
        db.session.commit()

        new_company = Company(name=name,user_id=new_user.user_id,hr_contact=hr_contact,website=website,status="pending")
        db.session.add(new_company)
        db.session.commit()

        flash("Registration Successful",category="success")
        return render_template("company/signup.html")
    
@api.route("/student_signup",methods=["GET","POST"])
def student_signup():
    if request.method == "GET":
        selected_degree=request.args.get("degree")
        return render_template("student/signup.html",selected_degree=selected_degree)
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        roll_no = request.form.get("roll_no")
        phone = request.form.get("phone")
        department = request.form.get("department")
        degree = request.form.get("degree")
        batch_year = request.form.get("batch_year")
        cgpa = request.form.get("cgpa")
        resume_url = request.form.get("resume_url")

        student=Users.query.filter_by(username=username).first()

        if student:
            flash("username already taken",category="inavlid-email")
            return redirect(url_for("auth_api.student_signup"))
        
        if not name or not username:
            flash("both name and username are reuqired",category="warning")
            return render_template("student/signup.html")
        
        new_user = Users(name=name,username=username,password=generate_password_hash(password,method="pbkdf2:sha256"),role="student",is_active=True)
        db.session.add(new_user)
        db.session.commit()

        new_student = Student(name=name,user_id=new_user.user_id,roll_no=roll_no,phone=phone,department=department,degree=degree,batch_year=batch_year,cgpa=cgpa,resume_url=resume_url,is_placed=False,status="active")
        db.session.add(new_student)
        db.session.commit()

        flash("Registration Successful",category="success")
        return render_template("index.html")