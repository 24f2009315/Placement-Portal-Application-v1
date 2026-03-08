from flask import Blueprint, jsonify, request
from application.models import Company, Placement, db
from datetime import datetime

api = Blueprint("drive_api",__name__)

@api.route('/api/drives', methods=['GET'])
def get_drives_api():
    placements = Placement.query.all()
    result = []
    for _ in placements:
        result.append({
            "drive_id":_.drive_id,
            "name":_.name
        })
    return jsonify(result)

@api.route('/api/drives', methods=['POST'])
def create_drive_api():
    data = request.get_json()

    if not data or not data.get("company_id") or not data.get("title"):
        return jsonify({"error": "invalid input"}), 400

    company = Company.query.get(data.get("company_id"))
    if not company:
        return jsonify({"error": "Company not found"}), 404

    deadline_str = data.get("deadline")

    deadline_obj = None
    if deadline_str:
        deadline_obj = datetime.strptime(deadline_str, "%Y-%m-%d").date()

    new_drive = Placement(
        company_id=data.get("company_id"),
        name=data.get("name"),
        title=data.get("title"),
        description=data.get("description"),
        eligibility=data.get("eligibility"),
        deadline=deadline_obj,
        status="open"
    )

    db.session.add(new_drive)
    db.session.commit()

    return jsonify({
        "message": "Drive created",
        "drive_id": new_drive.drive_id
    }), 201

@api.route('/api/drives/<int:drive_id>', methods=['PUT'])
def update_drive_api(drive_id):
    data = request.get_json()

    drive = Placement.query.get(drive_id)

    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    if data.get("name"):
        drive.name = data.get("name")

    if data.get("title"):
        drive.title= data.get("title")

    if data.get("description"):
        drive.description = data.get("description")

    if data.get("eligibility"):
        drive.eligibility = data.get("eligibility")

    if data.get("deadline"):
        drive.deadline = data.get("deadline")

    db.session.commit()

    return jsonify({"message": "Drive updated successfully"})

@api.route('/api/drives/<int:drive_id>', methods=['DELETE'])
def delete_drive_api(drive_id):

    drive = Placement.query.get(drive_id)

    if not drive:
        return jsonify({"error": "Drive not found"}), 404

    db.session.delete(drive)
    db.session.commit()

    return jsonify({"message": "Drive deleted successfully"})
