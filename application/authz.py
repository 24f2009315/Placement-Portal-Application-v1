from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth_api.login"))
            if current_user.role not in roles:
                flash("Unauthorized access", "danger")
                if current_user.role == "admin":
                    return redirect(url_for("admin_api.admin_dashboard"))
                if current_user.role == "company":
                    return redirect(url_for("company_api.company_dashboard"))
                if current_user.role == "student":
                    return redirect(url_for("student_api.student_dashboard"))
                return redirect(url_for("auth_api.login"))
            return view_func(*args, **kwargs)
        return wrapped
    return decorator
