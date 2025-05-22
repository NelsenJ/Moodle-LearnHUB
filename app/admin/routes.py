from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.admin import bp
from app.models import User, Course, Lesson, Enrollment, Quiz, Question, QuizAttempt

@bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.index'))
    
    # Fetch all data
    users = User.query.all()
    courses = Course.query.all()
    lessons = Lesson.query.all()
    enrollments = Enrollment.query.all()
    quizzes = Quiz.query.all()
    questions = Question.query.all()
    quiz_attempts = QuizAttempt.query.all()
    
    # Calculate statistics
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_teachers = User.query.filter_by(role='teacher').count()
    total_students = User.query.filter_by(role='student').count()
    total_admins = User.query.filter_by(role='admin').count()
    total_lessons = Lesson.query.count()
    total_enrollments = Enrollment.query.count()
    total_quizzes = Quiz.query.count()
    total_questions = Question.query.count()
    total_attempts = QuizAttempt.query.count()
    
    return render_template(
        'admin/dashboard.html',
        title='Admin Dashboard',
        users=users,
        courses=courses,
        lessons=lessons,
        enrollments=enrollments,
        quizzes=quizzes,
        questions=questions,
        quiz_attempts=quiz_attempts,
        total_users=total_users,
        total_courses=total_courses,
        total_teachers=total_teachers,
        total_students=total_students,
        total_admins=total_admins,
        total_lessons=total_lessons,
        total_enrollments=total_enrollments,
        total_quizzes=total_quizzes,
        total_questions=total_questions,
        total_attempts=total_attempts
    )

# User Management Routes
@bp.route('/user/<int:user_id>/edit', methods=['POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        # Validate required fields
        if 'username' in data and not data['username'].strip():
            return jsonify({'error': 'Username cannot be empty'}), 400
        if 'email' in data and not data['email'].strip():
            return jsonify({'error': 'Email cannot be empty'}), 400
        if 'role' in data and data['role'] not in ['admin', 'teacher', 'student']:
            return jsonify({'error': 'Invalid role'}), 400
            
        # Update fields
        if 'username' in data:
            user.username = data['username'].strip()
        if 'email' in data:
            user.email = data['email'].strip()
        if 'role' in data:
            user.role = data['role']
        if 'bio' in data:
            user.bio = data['bio'].strip()
        
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    user = User.query.get_or_404(user_id)
    
    try:
        # Delete all courses taught by this user
        for course in user.courses:
            # Delete all lessons in the course
            for lesson in course.lessons:
                # Delete all quizzes in the lesson
                for quiz in lesson.quizzes:
                    # Delete all quiz attempts
                    QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
                    # Delete all questions in the quiz
                    Question.query.filter_by(quiz_id=quiz.id).delete()
                    db.session.delete(quiz)
                db.session.delete(lesson)
            # Delete all enrollments in the course
            Enrollment.query.filter_by(course_id=course.id).delete()
            db.session.delete(course)
        
        # Delete all enrollments of this user
        Enrollment.query.filter_by(user_id=user.id).delete()
        
        # Delete all quiz attempts by this user
        QuizAttempt.query.filter_by(user_id=user.id).delete()
        
        # Finally delete the user
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User and all related data deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Course Management Routes
@bp.route('/course/<int:course_id>/edit', methods=['POST'])
@login_required
def edit_course(course_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    course = Course.query.get_or_404(course_id)
    data = request.get_json()
    
    try:
        # Validate required fields
        if 'title' in data and not data['title'].strip():
            return jsonify({'error': 'Title cannot be empty'}), 400
        if 'level' in data and data['level'] not in ['beginner', 'intermediate', 'advanced']:
            return jsonify({'error': 'Invalid level'}), 400
            
        # Update fields
        if 'title' in data:
            course.title = data['title'].strip()
        if 'description' in data:
            course.description = data['description'].strip()
        if 'category' in data:
            course.category = data['category'].strip()
        if 'level' in data:
            course.level = data['level']
        if 'duration' in data:
            course.duration = int(data['duration']) if data['duration'] else 0
        
        db.session.commit()
        return jsonify({'message': 'Course updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/course/<int:course_id>/delete', methods=['POST'])
@login_required
def delete_course(course_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    course = Course.query.get_or_404(course_id)
    
    try:
        # Delete all lessons in the course
        for lesson in course.lessons:
            # Delete all quizzes in the lesson
            for quiz in lesson.quizzes:
                # Delete all quiz attempts
                QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
                # Delete all questions in the quiz
                Question.query.filter_by(quiz_id=quiz.id).delete()
                db.session.delete(quiz)
            db.session.delete(lesson)
        
        # Delete all enrollments in the course
        Enrollment.query.filter_by(course_id=course.id).delete()
        
        # Finally delete the course
        db.session.delete(course)
        db.session.commit()
        return jsonify({'message': 'Course and all related data deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Lesson Management Routes
@bp.route('/lesson/<int:lesson_id>/edit', methods=['POST'])
@login_required
def edit_lesson(lesson_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    lesson = Lesson.query.get_or_404(lesson_id)
    data = request.get_json()
    
    try:
        # Validate required fields
        if 'title' in data and not data['title'].strip():
            return jsonify({'error': 'Title cannot be empty'}), 400
            
        # Update fields
        if 'title' in data:
            lesson.title = data['title'].strip()
        if 'content' in data:
            lesson.content = data['content'].strip()
        if 'video_url' in data:
            lesson.video_url = data['video_url'].strip()
        if 'order' in data:
            lesson.order = int(data['order']) if data['order'] else 0
        if 'duration' in data:
            lesson.duration = int(data['duration']) if data['duration'] else 0
        
        db.session.commit()
        return jsonify({'message': 'Lesson updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/lesson/<int:lesson_id>/delete', methods=['POST'])
@login_required
def delete_lesson(lesson_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    try:
        # Delete all quizzes in the lesson
        for quiz in lesson.quizzes:
            # Delete all quiz attempts
            QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
            # Delete all questions in the quiz
            Question.query.filter_by(quiz_id=quiz.id).delete()
            db.session.delete(quiz)
        
        # Finally delete the lesson
        db.session.delete(lesson)
        db.session.commit()
        return jsonify({'message': 'Lesson and all related data deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Enrollment Management Routes
@bp.route('/enrollment/<int:enrollment_id>/edit', methods=['POST'])
@login_required
def edit_enrollment(enrollment_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    data = request.get_json()
    
    try:
        # Validate fields
        if 'progress' in data:
            progress = int(data['progress'])
            if progress < 0 or progress > 100:
                return jsonify({'error': 'Progress must be between 0 and 100'}), 400
            enrollment.progress = progress
            
        if 'completed_lessons' in data:
            completed = int(data['completed_lessons'])
            if completed < 0:
                return jsonify({'error': 'Completed lessons cannot be negative'}), 400
            enrollment.completed_lessons = completed
        
        db.session.commit()
        return jsonify({'message': 'Enrollment updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/enrollment/<int:enrollment_id>/delete', methods=['POST'])
@login_required
def delete_enrollment(enrollment_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    
    try:
        db.session.delete(enrollment)
        db.session.commit()
        return jsonify({'message': 'Enrollment deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Quiz Management Routes
@bp.route('/quiz/<int:quiz_id>/edit', methods=['POST'])
@login_required
def edit_quiz(quiz_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    try:
        # Validate required fields
        if 'title' in data and not data['title'].strip():
            return jsonify({'error': 'Title cannot be empty'}), 400
        if 'passing_score' in data:
            score = int(data['passing_score'])
            if score < 0 or score > 100:
                return jsonify({'error': 'Passing score must be between 0 and 100'}), 400
            
        # Update fields
        if 'title' in data:
            quiz.title = data['title'].strip()
        if 'description' in data:
            quiz.description = data['description'].strip()
        if 'passing_score' in data:
            quiz.passing_score = int(data['passing_score'])
        
        db.session.commit()
        return jsonify({'message': 'Quiz updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/quiz/<int:quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    quiz = Quiz.query.get_or_404(quiz_id)
    
    try:
        # Delete all quiz attempts
        QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
        # Delete all questions in the quiz
        Question.query.filter_by(quiz_id=quiz.id).delete()
        # Finally delete the quiz
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({'message': 'Quiz and all related data deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/user/create', methods=['POST'])
@login_required
def create_user():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    try:
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role'),
            password='default123'  # kamu bisa set password default atau hash
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
