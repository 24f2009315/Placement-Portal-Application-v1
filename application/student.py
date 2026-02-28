from flask import Flask,Blueprint,render_template,request,flash,redirect,url_for,jsonify
from application.authz import role_required
from application.models import Users,Company,db,Student,Placement,Application
from flask_login import login_user,logout_user,login_required,current_user
from werkzeug.security import generate_password_hash, check_password_hash

api = Blueprint("student_api",__name__)

@api.route("/student/student_dashboard",methods=["GET","POST","PUT","PATCH","DELETE"])
@login_required
@role_required("student")
def student_dashboard():
    registered_companies = Company.query.filter_by(status="approved").all()
    student = Student.query.filter_by(user_id = current_user.user_id).first()
    applied_drives = Application.query.filter_by(student_id = student.student_id).all()
    status_counts = {}
    for app in applied_drives:
        status = (app.status or "applied").capitalize()
        status_counts[status] = status_counts.get(status, 0) + 1

    student_chart_data = {
        "labels": list(status_counts.keys()),
        "values": list(status_counts.values())
    }
    return render_template("student/dashboard.html",
                           registered_companies=registered_companies,
                           applied_drives=applied_drives,
                           student_chart_data=student_chart_data)

@api.route("/student/view_drives/<int:company_id>",methods=["GET"])
@login_required
@role_required("student")
def view_drives(company_id):
    company = Company.query.filter_by(company_id=company_id).first()
    drives = Placement.query.filter_by(company_id=company_id,status="open").all()
    return render_template("student/view_drives.html",company=company,drives=drives)

@api.route("/student/view_drive/<int:drive_id>", methods=["GET"])
@login_required
@role_required("student")
def view_drive(drive_id):

    drive = Placement.query.filter_by(drive_id=drive_id).first()
    company = Company.query.get(drive.company_id)

    return render_template("student/drive.html",drive=drive,company=company)

@api.route("/student/apply_drive/<int:drive_id>",methods=["POST"])
@login_required
@role_required("student")
def apply_drive(drive_id):
    student = Student.query.filter_by(user_id=current_user.user_id).first()

    existing_application = Application.query.filter_by(student_id=student.student_id,drive_id=drive_id).first()

    if existing_application:
        flash("You have already applied to this drive", "warning")
        return redirect(url_for("student_api.student_dashboard"))

    application = Application(student_id=student.student_id,drive_id=drive_id,status="applied")
    db.session.add(application)
    db.session.commit()

    flash("applied successfully",category="alert-success")
    return redirect(url_for('student_api.student_dashboard'))

@api.route("/student/search",methods=["GET","POST"])
@login_required
@role_required("student")
def search():
    query=request.args.get("query","").strip()
    companies=[]
    if query:
        companies = Company.query.filter(
            (Company.name.ilike(f'%{query}%'))
        ).all()
    return render_template("student/search.html",companies=companies)

@api.route('/api/students', methods=['GET'])
def get_students_api():
    students = Student.query.all()
    result = []
    for _ in students:
        result.append({
            "student_id":_.student_id,
            "name":_.name
        })
    return jsonify(result)

@api.route('/api/students', methods=['POST'])
def create_students_api():
    data = request.get_json()

    if not data:
        return jsonify({"error": "invalid input"}), 400

    new_user = Users(
        name=data.get("name"),
        username=data.get("username"),
        password=data.get("password"),
        role="student",
        is_active=True
    )
    db.session.add(new_user)
    db.session.commit()

    new_student = Student(
        name=data.get("name"),
        user_id=new_user.user_id,
        roll_no=data.get("roll_no")
    )
    db.session.add(new_student)
    db.session.commit()

    return jsonify({
        "message": "student created",
        "student_id": new_student.student_id,
        "user_id": new_user.user_id
    }), 201

@api.route('/api/students/<int:student_id>', methods=['PUT'])
def update_student_api(student_id):
    data = request.get_json()

    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    if data.get("name"):
        student.user.name = data.get("name")

    if data.get("roll_no"):
        student.roll_no = data.get("roll_no")

    if data.get("phone"):
        student.phone = data.get("phone")

    if data.get("department"):
        student.department = data.get("department")

    if data.get("degree"):
        student.degree = data.get("degree")

    if data.get("batch_year"):
        student.batch_year = data.get("batch_year")

    if data.get("cgpa"):
        student.cgpa = data.get("cgpa")

    if data.get("resume_url"):
        student.resume_url = data.get("resume_url")

    db.session.commit()

    return jsonify({"message": "Student updated successfully"})

@api.route('/api/students/<int:student_id>', methods=['DELETE'])
def delete_student_api(student_id):

    student = Student.query.get(student_id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    user = student.user

    db.session.delete(student)
    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Student deleted successfully"})