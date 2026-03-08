from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from application.models import Company, Student, Users, db
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint("auth_api",__name__)

@api.route("/",methods=["GET"])
def index():
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
            if not company:
                flash("Company profile missing. Contact admin.", category="warning")
                return redirect(url_for("auth_api.login"))
            if company.status != "approved":
                flash("you cant login until approved")
                return redirect(url_for("auth_api.login"))
        
        login_user(user, remember=True)
        session.permanent = True
        flash("Login Successful",category="success")

        if user.role == "student":
            return redirect(url_for("student_api.student_dashboard"))
        elif user.role == "company":
            if company.status == "approved":
                return redirect(url_for("company_api.company_dashboard"))
            else:
                return redirect(url_for("auth_api.login"))
        return redirect(url_for("admin_api.admin_dashboard"))

@api.route("/company_signup",methods=["GET","POST"])
def company_signup():
    if request.method == "GET":
        return render_template("com_signup.html")
    if request.method == "POST":
        name = request.form.get("name","").strip()
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        confirm_password = request.form.get("confirm_password", "")
        hr_contact = request.form.get("hr_contact","").strip()
        website = request.form.get("website","").strip()

        errors=[]

        # Required checks
        if not name or len(name) < 3:
            errors.append("Company name must be at least 3 characters.")

        if not username or not username.replace("_", "").isalnum():
            errors.append("Invalid username format.")

        if len(password) < 8:
            errors.append("Password must be at least 8 characters.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        if not hr_contact.isdigit() or len(hr_contact) != 10:
            errors.append("HR contact must be 10 digits.")

        if not website.startswith("http"):
            errors.append("Website must start with http or https.")

        existing_company=Users.query.filter_by(username=username).first()

        if existing_company:
            flash("username already taken",category="inavlid-email")
            return redirect(url_for("auth_api.company_signup"))
        
        if errors:
            for error in errors:
                flash(error,category="warning")
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
        return render_template("index.html")
    
@api.route("/student_signup",methods=["GET","POST"])
def student_signup():
    if request.method == "GET":
        selected_degree=request.args.get("degree")
        return render_template("stu_signup.html",selected_degree=selected_degree)
    if request.method == "POST":
        name = request.form.get("name","").strip()
        username = request.form.get("username","").strip()
        password = request.form.get("password","")
        confirm_password = request.form.get("confirm_password", "")
        roll_no = request.form.get("roll_no","").strip()
        phone = request.form.get("phone","").strip()
        department = request.form.get("department","")
        degree = request.form.get("degree","")
        batch_year = request.form.get("batch_year","")
        cgpa = request.form.get("cgpa","")
        resume_url = request.form.get("resume_url","").strip()

        errors=[]

        # Name
        if len(name) < 3:
            errors.append("Name must be at least 3 characters.")

        # Username
        if not username.replace("_", "").isalnum():
            errors.append("Invalid username.")

        # Password
        if len(password) < 8:
            errors.append("Password too short.")

        if password != confirm_password:
            errors.append("Passwords do not match.")

        # Roll number
        if not roll_no:
            errors.append("Roll number required.")

        # Phone
        if not phone.isdigit() or len(phone) != 10:
            errors.append("Phone must be 10 digits.")

        # Batch year
        try:
            batch_year = int(batch_year)
            if batch_year < 2015 or batch_year > 2035:
                errors.append("Invalid batch year.")
        except:
            errors.append("Batch year must be numeric.")

        # CGPA
        try:
            cgpa = float(cgpa)
            if cgpa < 0 or cgpa > 10:
                errors.append("CGPA must be between 0 and 10.")
        except:
            errors.append("Invalid CGPA.")

        # Resume
        if not resume_url.startswith("http"):
            errors.append("Resume URL must start with http or https.")

        student=Users.query.filter_by(username=username).first()

        if student:
            flash("username already taken",category="warning")
            return redirect(url_for("auth_api.student_signup"))
        
        if errors:
            for error in errors:
                flash(error,category="warning")
            return redirect(url_for("auth_api.student_signup",degree=degree))
        
        if not name or not username:
            flash("both name and username are reuqired",category="warning")
            return render_template("stu_signup.html")
        
        new_user = Users(name=name,username=username,password=generate_password_hash(password,method="pbkdf2:sha256"),role="student",is_active=True)
        db.session.add(new_user)
        db.session.commit()

        new_student = Student(name=name,user_id=new_user.user_id,roll_no=roll_no,phone=phone,department=department,degree=degree,batch_year=batch_year,cgpa=cgpa,resume_url=resume_url,is_placed=False,status="active")
        db.session.add(new_student)
        db.session.commit()

        flash("Registration Successful",category="success")
        return render_template("index.html")
    
@api.route("/logout",methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("User logged out successfully",category="success")
    return redirect(url_for("auth_api.login"))
