from flask import Blueprint, jsonify, request
from application.models import Application, db

api = Blueprint("application_api",__name__)

@api.route('/api/applications', methods=['GET'])
def get_applications_api():
    applications = Application.query.all()
    result = []

    for app in applications:
        result.append({
            "application_id": app.application_id,
            "student_id": app.student_id,
            "drive_id": app.drive_id,
            "status": app.status
        })

    return jsonify(result)

@api.route('/api/applications', methods=['POST'])
def create_application_api():
    data = request.get_json()

    if not data or not data.get("student_id") or not data.get("drive_id"):
        return jsonify({"error": "invalid input"}), 400

    new_application = Application(
        student_id=data.get("student_id"),
        drive_id=data.get("drive_id"),
        status="applied"
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify({
        "message": "Application submitted",
        "application_id": new_application.application_id
    }), 201

@api.route('/api/applications/<int:application_id>', methods=['PUT'])
def update_application_api(application_id):
    data = request.get_json()

    application = Application.query.get(application_id)

    if not application:
        return jsonify({"error": "Application not found"}), 404

    if data.get("status"):
        application.status = data.get("status")

    db.session.commit()

    return jsonify({"message": "Application updated"})

@api.route('/api/applications/<int:application_id>', methods=['DELETE'])
def delete_application_api(application_id):

    application = Application.query.get(application_id)

    if not application:
        return jsonify({"error": "Application not found"}), 404

    db.session.delete(application)
    db.session.commit()

    return jsonify({"message": "Application deleted"})
