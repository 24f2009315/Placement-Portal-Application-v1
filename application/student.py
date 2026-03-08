from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from application.models import Application, Company, Placement, Student, Users, db
from flask_login import current_user, login_required

api = Blueprint("student_api",__name__)

@api.before_request
@login_required
def require_student():
    if current_user.role != "student":
        return "Access Denied", 403

@api.route("/student/student_dashboard", methods=["GET"])
def student_dashboard():
    registered_companies = Company.query.filter_by(status="approved").all()
    student = Student.query.filter_by(user_id = current_user.user_id).first()
    if not student:
        flash("Student profile missing. Contact admin.", "warning")
        return redirect(url_for("auth_api.login"))
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
def view_drives(company_id):
    company = Company.query.filter_by(company_id=company_id).first()
    drives = Placement.query.filter_by(company_id=company_id,status="approved").all()
    return render_template("student/view_drives.html",company=company,drives=drives)

@api.route("/student/view_drive/<int:drive_id>", methods=["GET"])
def view_drive(drive_id):

    drive = Placement.query.filter_by(drive_id=drive_id).first()
    if not drive:
        flash("Drive not found.", "warning")
        return redirect(url_for("student_api.student_dashboard"))
    company = Company.query.get(drive.company_id)
    if not company:
        flash("Company record missing for this drive.", "warning")
        return redirect(url_for("student_api.student_dashboard"))

    return render_template("student/drive.html",drive=drive,company=company)

@api.route("/student/apply_drive/<int:drive_id>",methods=["POST"])
def apply_drive(drive_id):
    student = Student.query.filter_by(user_id=current_user.user_id).first()
    if not student:
        flash("Student profile missing. Contact admin.", "warning")
        return redirect(url_for("auth_api.login"))
    drive = Placement.query.filter(
        Placement.drive_id == drive_id,
        Placement.status.in_(["approved", "open"]),
    ).first()
    if not drive:
        flash("Drive not found or closed.", "warning")
        return redirect(url_for("student_api.student_dashboard"))


    existing_application = Application.query.filter_by(student_id=student.student_id,drive_id=drive.drive_id).first()

    if existing_application:
        flash("You have already applied to this drive", "warning")
        return redirect(url_for("student_api.student_dashboard"))

    application = Application(student_id=student.student_id,drive_id=drive_id,status="applied")
    db.session.add(application)
    db.session.commit()

    flash("applied successfully",category="alert-success")
    return redirect(url_for('student_api.student_dashboard'))

@api.route("/student/search", methods=["GET"])
def search():
    query=request.args.get("query","").strip()
    companies=[]
    if query:
        companies = Company.query.filter(
            (Company.name.ilike(f'%{query}%'))
        ).all()
    return render_template("student/search.html",companies=companies)

@api.route("/profile/update", methods=["GET", "POST"])
def update_profile():
    student = Student.query.filter_by(user_id=current_user.user_id).first()

    if request.method == "GET":
        return render_template("student/update_profile.html", student=student)

    if request.method == "POST":

        phone = request.form.get("phone", "").strip()
        cgpa = request.form.get("cgpa", "")
        resume_url = request.form.get("resume_url", "").strip()

        errors = []

        if not phone.isdigit() or len(phone) != 10:
            errors.append("Invalid phone number.")

        try:
            cgpa = float(cgpa)
            if cgpa < 0 or cgpa > 10:
                errors.append("CGPA must be between 0 and 10.")
        except:
            errors.append("Invalid CGPA.")

        if not resume_url.startswith("http"):
            errors.append("Invalid resume URL.")

        if errors:
            for error in errors:
                flash(error, "warning")
            return redirect(url_for("student_api.update_profile"))

        # Safe update
        student.phone = phone
        student.cgpa = cgpa
        student.resume_url = resume_url

        db.session.commit()

        flash("Profile updated successfully", "success")
        return redirect(url_for("student_api.student_dashboard"))

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
