from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Course, User, Enrollment
from app.forms import ProfileForm, ChangePasswordForm
from datetime import datetime, timedelta
from sqlalchemy import func

@bp.route('/')
@bp.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    # Popular courses = recommended/top courses (by students count)
    popular_courses = (
        Course.query
        .outerjoin(Course.students)
        .group_by(Course.id)
        .order_by(func.count(Enrollment.id).desc())
        .limit(3)
        .all()
    )
    return render_template('index.html', title='Home', popular_courses=popular_courses)

@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category')
    level = request.args.get('level')
    search = request.args.get('search', '')
    sort = request.args.get('sort', 'newest')

    query = Course.query

    # Add search filter
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                Course.title.ilike(search_term),
                Course.description.ilike(search_term)
            )
        )

    if category:
        query = query.filter_by(category=category)
    if level:
        query = query.filter_by(level=level)

    if sort == 'popular':
        query = query.outerjoin(Course.students).group_by(Course.id).order_by(func.count(Enrollment.id).desc())
    elif sort == 'rating':
        # Implement rating system later
        pass
    else:  # newest
        query = query.order_by(Course.created_at.desc())

    courses = query.paginate(page=page, per_page=12, error_out=False)
    return render_template('explore.html', title='Explore Courses', courses=courses)

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    elif current_user.is_teacher:
        return redirect(url_for('teacher.dashboard'))
    
    # Get student's enrolled courses
    enrollments = current_user.enrolled_courses.order_by(Enrollment.last_accessed.desc()).all()
    
    # Get recent activity (last 7 days)
    recent_activity = []
    for enrollment in enrollments:
        if enrollment.last_accessed > datetime.utcnow() - timedelta(days=7):
            recent_activity.append({
                'course': enrollment.course,
                'progress': enrollment.progress,
                'last_accessed': enrollment.last_accessed
            })
    
    # Get recommended courses
    recommended_courses = (
        db.session.query(Course)
        .outerjoin(Course.students)
        .filter(~Course.id.in_([e.course_id for e in enrollments]))
        .group_by(Course.id)
        .order_by(func.count(Enrollment.id).desc())
        .limit(3)
        .all()
    )
    
    # Get course categories for stats
    categories = db.session.query(
        Course.category, 
        db.func.count(Course.id)
    ).group_by(Course.category).all()
    
    return render_template('dashboard/student.html',
                         title='Student Dashboard',
                         enrollments=enrollments,
                         recent_activity=recent_activity,
                         recommended_courses=recommended_courses,
                         categories=categories)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(original_username=current_user.username, 
                      original_email=current_user.email)
    password_form = ChangePasswordForm()
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('main.profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio
    
    return render_template('profile.html', title='Profile', 
                         form=form, password_form=password_form)

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated.', 'success')
        else:
            flash('Current password is incorrect.', 'danger')
    return redirect(url_for('main.profile')) 