from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.teacher import bp
from app.models import Course, User, Enrollment
from sqlalchemy import func

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_teacher:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # My Courses: 3 course buatan sendiri, urut user terbanyak
    my_courses = (
        Course.query
        .outerjoin(Course.students)
        .filter(Course.teacher_id == current_user.id)
        .group_by(Course.id)
        .order_by(func.count(Enrollment.id).desc())
        .limit(3)
        .all()
    )
    # Recommended Courses: semua course, urut user terbanyak, limit 3
    recommended_courses = (
        Course.query
        .outerjoin(Course.students)
        .group_by(Course.id)
        .order_by(func.count(Enrollment.id).desc())
        .limit(3)
        .all()
    )
    return render_template('teacher/dashboard.html', 
                         title='Teacher Dashboard',
                         my_courses=my_courses,
                         recommended_courses=recommended_courses)

@bp.route('/my-courses')
@login_required
def my_courses_list():
    if not current_user.is_teacher:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    # Semua course buatan sendiri, urut user terbanyak
    courses = (
        Course.query
        .outerjoin(Course.students)
        .filter(Course.teacher_id == current_user.id)
        .group_by(Course.id)
        .order_by(func.count(Enrollment.id).desc())
        .all()
    )
    return render_template('teacher/my_courses.html',
                         title='My Courses',
                         courses=courses) 