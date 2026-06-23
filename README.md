# Placement Portal Application

Placement Portal is a Flask-based web application for managing campus recruitment workflows. It supports three roles:

- `admin` manages companies, students, and drive approvals
- `company` creates placement drives and reviews applicants
- `student` browses approved drives and applies to them

The project uses server-rendered Flask templates for the web UI and also exposes JSON APIs for core entities.

## Tech Stack

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLite
- Jinja2 templates
- HTML, CSS, Bootstrap

## Main Features

- Admin dashboard for approving or rejecting companies and drives
- Company dashboard for creating drives and updating application status
- Student dashboard for browsing companies, viewing drives, and applying
- CRUD JSON APIs for companies, students, drives, and applications
- OpenAPI YAML file for the API contract

## Project Structure

```text
Placement-Portal-Application-v1/
|-- app.py
|-- requirements.txt
|-- api.yaml
|-- application/
|-- templates/
`-- instance/
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python app.py
```

4. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Default Admin Account

On first run, the app seeds a default admin user if it does not already exist:

- Username: `vaishnavi`
- Password: `vaishnavi`

This is defined in [app.py](/c:/Users/mvnr7/Placement-Portal-Application-v1/app.py) and should be changed for any non-local use.

## API Documentation

The JSON API definition is available in [openapi.yaml](/c:/Users/mvnr7/Placement-Portal-Application-v1/openapi.yaml).

Implemented API groups:

- `GET, POST /api/companies`
- `PUT, DELETE /api/companies/{company_id}`
- `GET, POST /api/students`
- `PUT, DELETE /api/students/{student_id}`
- `GET, POST /api/drives`
- `PUT, DELETE /api/drives/{drive_id}`
- `GET, POST /api/applications`
- `PUT, DELETE /api/applications/{application_id}`

## Notes

- The application uses SQLite with `sqlite:///model.db`.
- Session configuration and app bootstrapping are defined in [app.py](/c:/Users/mvnr7/Placement-Portal-Application-v1/app.py).
- The web UI routes and the JSON API routes are both part of the same Flask application.

## Watch the Demo Video Here
[https://drive.google.com/file/d/145oGVoo6vpYfxyPLk2avdnWeXbZYYMU-/view?usp=drive_link]
