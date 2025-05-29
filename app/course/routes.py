from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.course import bp
from app.models import Course, Lesson, Enrollment, Quiz, QuizAttempt, Question
from datetime import datetime
from sqlalchemy import desc
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Mathematics', 'Mathematics'),
        ('Physics', 'Physics'),
        ('Biology', 'Biology'),
        ('Chemistry', 'Chemistry'),
        ('English', 'English'),
        ('Programming', 'Programming'),
        ('Design', 'Design'),
        ('Business', 'Business')
    ], validators=[DataRequired()])
    level = SelectField('Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    duration = IntegerField('Duration (hours)', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Create Course')

@bp.route('/<int:course_id>')
def view(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = None
    is_teacher = False
    
    if current_user.is_authenticated:
        # If user is the teacher of this course, they don't need enrollment
        if current_user.is_teacher and course.teacher_id == current_user.id:
            is_teacher = True
            # Create a virtual enrollment for teachers to access course content
            enrollment = Enrollment(
                user_id=current_user.id,
                course_id=course_id,
                progress=100,  # Teachers have full access
                completed_lessons=course.lessons.count()  # All lessons are considered completed
            )
        else:
            enrollment = Enrollment.query.filter_by(
                user_id=current_user.id,
                course_id=course_id
            ).first()
    
    return render_template('course/view.html', 
                         course=course, 
                         enrollment=enrollment, 
                         is_teacher=is_teacher,
                         Lesson=Lesson)

@bp.route('/<int:course_id>/enroll')
@login_required
def enroll(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_authenticated:
        flash('Please login to enroll in this course', 'warning')
        return redirect(url_for('auth.login'))
    
    enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if enrollment:
        flash('You are already enrolled in this course', 'info')
    else:
        enrollment = Enrollment(user_id=current_user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        flash('Successfully enrolled in the course!', 'success')
    
    return redirect(url_for('course.view', course_id=course_id))

@bp.route('/<int:course_id>/lesson/<int:lesson_id>')
def view_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if user is enrolled or if it's the first lesson
    if not current_user.is_authenticated and lesson.order > 1:
        flash('Please login to access this lesson', 'warning')
        return redirect(url_for('auth.login'))
    
    if current_user.is_authenticated:
        # If user is the teacher of this course, they have full access
        if current_user.is_teacher and course.teacher_id == current_user.id:
            pass
        else:
            enrollment = Enrollment.query.filter_by(
                user_id=current_user.id,
                course_id=course_id
            ).first()
            if not enrollment and lesson.order > 1:
                flash('Please enroll in this course to access this lesson', 'warning')
                return redirect(url_for('course.view', course_id=course_id))
    
    return render_template('course/view_lesson.html', course=course, lesson=lesson, Lesson=Lesson)

@bp.route('/my-courses')
@login_required
def my_courses():
    enrollments = current_user.enrolled_courses.all()
    return render_template('course/my_courses.html', enrollments=enrollments)

@bp.route('/<int:course_id>/lesson/<int:lesson_id>/quiz')
@login_required
def take_quiz(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    quiz_id = request.args.get('quiz_id', type=int)
    if quiz_id:
        quiz = Quiz.query.filter_by(id=quiz_id, lesson_id=lesson_id).first()
    else:
        quiz = lesson.quizzes.first()
    
    # Allow teachers to access their own course quizzes without enrollment
    if current_user.is_teacher and course.teacher_id == current_user.id:
        pass
    else:
        # Check if user is enrolled
        enrollment = Enrollment.query.filter_by(
            user_id=current_user.id,
            course_id=course_id
        ).first()
        
        if not enrollment:
            flash('Please enroll in this course to take the quiz.', 'warning')
            return redirect(url_for('course.view', course_id=course_id))
    
    if not quiz:
        flash('This lesson does not have a quiz yet.', 'info')
        return redirect(url_for('course.view_lesson', course_id=course_id, lesson_id=lesson_id))
    
    # Get all completed attempts, best_attempt (highest score), and last_attempt (latest)
    attempts = QuizAttempt.query.filter(
        QuizAttempt.quiz_id == quiz.id,
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at != None
    ).order_by(
        QuizAttempt.score.desc(),
        QuizAttempt.completed_at.desc()
    ).all()
    best_attempt = attempts[0] if attempts else None
    last_attempt = QuizAttempt.query.filter(
        QuizAttempt.quiz_id == quiz.id,
        QuizAttempt.user_id == current_user.id,
        QuizAttempt.completed_at != None
    ).order_by(
        QuizAttempt.completed_at.desc()
    ).first()
    
    return render_template('course/quiz.html', 
                         title='Take Quiz',
                         course=course,
                         lesson=lesson,
                         quiz=quiz,
                         best_attempt=best_attempt,
                         last_attempt=last_attempt)

@bp.route('/<int:course_id>/lesson/<int:lesson_id>/quiz/submit', methods=['POST'])
@login_required
def submit_quiz(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    quiz_id = request.form.get('quiz_id', type=int) or request.args.get('quiz_id', type=int)
    if quiz_id:
        quiz = Quiz.query.filter_by(id=quiz_id, lesson_id=lesson_id).first()
    else:
        quiz = lesson.quizzes.first()

    if not quiz:
        flash('This lesson does not have a quiz.', 'error')
        return redirect(url_for('course.view_lesson', course_id=course_id, lesson_id=lesson_id))

    if not hasattr(quiz, 'questions') or quiz.questions is None or quiz.questions.count() == 0:
        flash('This quiz does not have any questions.', 'error')
        return redirect(url_for('course.view_lesson', course_id=course_id, lesson_id=lesson_id))

    # Create new attempt
    attempt = QuizAttempt(
        quiz_id=quiz.id,
        user_id=current_user.id,
        answers={}
    )

    # Load quiz secara eksplisit
    attempt.quiz = quiz

    # Process answers
    answers = {}
    for question in quiz.questions:
        answer = request.form.get(f'question_{question.id}')
        if answer:
            answers[str(question.id)] = answer
    attempt.answers = answers  # assign all at once, so SQLAlchemy detects change

    # Calculate score
    attempt.calculate_score()

    # Save attempt
    db.session.add(attempt)
    db.session.commit()

    # Update progress in Enrollment
    enrollment = Enrollment.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if enrollment:
        lessons = Lesson.query.filter_by(course_id=course_id).all()
        completed = 0
        for l in lessons:
            quiz_l = l.quizzes.first()
            if quiz_l:
                latest_attempt = QuizAttempt.query.filter_by(quiz_id=quiz_l.id, user_id=current_user.id).order_by(QuizAttempt.completed_at.desc()).first()
                if latest_attempt and latest_attempt.completed_at:
                    completed += 1
        total = len(lessons)
        progress = int((completed / total) * 100) if total > 0 else 0
        enrollment.completed_lessons = completed
        enrollment.progress = progress
        db.session.commit()

    flash('Quiz submitted successfully!', 'success')
    return redirect(url_for('course.take_quiz', course_id=course_id, lesson_id=lesson_id, quiz_id=quiz.id))

@bp.route('/<int:course_id>/lesson/<int:lesson_id>/quiz/retake')
@login_required
def retake_quiz(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    quiz_id = request.args.get('quiz_id', type=int)
    if quiz_id:
        quiz = Quiz.query.filter_by(id=quiz_id, lesson_id=lesson_id).first()
    else:
        quiz = lesson.quizzes.first()

    if not quiz:
        flash('This lesson does not have a quiz.', 'error')
        return redirect(url_for('course.view_lesson', course_id=course_id, lesson_id=lesson_id))

    # Hapus attempt terakhir
    attempt = QuizAttempt.query.filter_by(
        quiz_id=quiz.id,
        user_id=current_user.id
    ).order_by(QuizAttempt.started_at.desc()).first()

    if attempt:
        db.session.delete(attempt)
        db.session.commit()

    flash('Quiz reset. You can retake the quiz now.', 'success')
    return redirect(url_for('course.take_quiz', course_id=course_id, lesson_id=lesson_id, quiz_id=quiz.id))

@bp.route('/<int:course_id>/lesson/<int:lesson_id>/quiz/review')
@login_required
def review_quiz(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    quiz_id = request.args.get('quiz_id', type=int)
    if quiz_id:
        quiz = Quiz.query.filter_by(id=quiz_id, lesson_id=lesson_id).first()
    else:
        quiz = lesson.quizzes.first()
    if not quiz:
        flash('This lesson does not have a quiz.', 'error')
        return redirect(url_for('course.view_lesson', course_id=course_id, lesson_id=lesson_id))

    # Get best attempt (highest score)
    attempt = QuizAttempt.query.filter_by(
        quiz_id=quiz.id,
        user_id=current_user.id
    ).order_by(QuizAttempt.score.desc(), QuizAttempt.completed_at.desc()).first()

    if not attempt or not attempt.completed_at:
        flash('You have not completed this quiz yet.', 'warning')
        return redirect(url_for('course.take_quiz', course_id=course_id, lesson_id=lesson_id, quiz_id=quiz.id))

    # Get all attempts (for history)
    attempts = QuizAttempt.query.filter_by(
        quiz_id=quiz.id,
        user_id=current_user.id
    ).order_by(QuizAttempt.completed_at.desc()).all()

    # Prepare review data: list of (question, user_answer, correct_answer, is_correct)
    review_data = []
    for question in quiz.questions:
        user_answer = attempt.answers.get(str(question.id)) if attempt.answers else None
        correct_answer = question.correct_answer
        is_correct = (user_answer == correct_answer)
        review_data.append({
            'question': question,
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct
        })

    return render_template('course/quiz_review.html', course=course, lesson=lesson, quiz=quiz, attempt=attempt, review_data=review_data, attempts=attempts)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not current_user.is_teacher:
        flash('You do not have permission to create a course.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            level=form.level.data,
            duration=form.duration.data,
            teacher_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully!', 'success')
        return redirect(url_for('course.view', course_id=course.id))
    
    return render_template('course/create.html', form=form)

@bp.route('/<int:course_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_course(course_id):
    course = Course.query.get_or_404(course_id)
    
    # Check if user is the teacher of this course
    if not current_user.is_teacher or course.teacher_id != current_user.id:
        flash('You do not have permission to manage this course.', 'error')
        return redirect(url_for('course.view', course_id=course.id))
    
    if request.method == 'POST':
        action = request.form.get('action')
        print(f"DEBUG: Received action: {action}")  # Debug print
        
        if action == 'edit_course':
            try:
                # Validate required fields
                title = request.form.get('title', '').strip()
                description = request.form.get('description', '').strip()
                category = request.form.get('category', '').strip()
                level = request.form.get('level', '').strip()
                duration = request.form.get('duration', type=int)

                if not title:
                    flash('Course title is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                if not description:
                    flash('Course description is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                if not category:
                    flash('Course category is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                if not level or level not in ['beginner', 'intermediate', 'advanced']:
                    flash('Valid course level is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                if duration is None or duration < 1:
                    flash('Valid course duration is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))

                # Update course details
                course.title = title
                course.description = description
                course.category = category
                course.level = level
                course.duration = duration

                db.session.commit()
                flash('Course updated successfully!', 'success')
                return redirect(url_for('course.manage_course', course_id=course_id))
                
            except Exception as e:
                db.session.rollback()
                flash('Error updating course: ' + str(e), 'error')
                return redirect(url_for('course.manage_course', course_id=course_id))
        
        elif action == 'add_lesson':
            try:
                # Debug prints
                print("DEBUG: Processing add_lesson action")
                print(f"DEBUG: Form data: {request.form}")
                
                # Validate required fields
                title = request.form.get('title', '').strip()
                content = request.form.get('content', '').strip()
                order = request.form.get('order', type=int)
                duration = request.form.get('duration', type=int)
                
                print(f"DEBUG: Parsed values - title: {title}, content length: {len(content)}, order: {order}, duration: {duration}")
                
                if not title:
                    flash('Lesson title is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                if not content:
                    flash('Lesson content is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                if order is None or order < 1:
                    flash('Valid lesson order is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                    
                if duration is None or duration < 1:
                    flash('Valid lesson duration is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                # Create new lesson
                lesson = Lesson(
                    title=title,
                    content=content,
                    video_url=request.form.get('video_url', '').strip(),
                    order=order,
                    duration=duration,
                    course_id=course_id
                )
                db.session.add(lesson)
                db.session.commit()
                flash('Lesson added successfully!', 'success')
                return redirect(url_for('course.manage_course', course_id=course_id))
                
            except Exception as e:
                import traceback
                print(f"DEBUG: Exception in add_lesson: {str(e)}")
                print("DEBUG: Traceback:")
                traceback.print_exc()
                db.session.rollback()
                flash('Error adding lesson: ' + str(e), 'error')
                return redirect(url_for('course.manage_course', course_id=course_id))
                
        elif action == 'edit_lesson':
            try:
                lesson_id = request.form.get('lesson_id', type=int)
                lesson = Lesson.query.get_or_404(lesson_id)
                if lesson.course_id != course_id:
                    flash('Invalid lesson.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                # Update fields
                lesson.title = request.form.get('title', '').strip()
                lesson.content = request.form.get('content', '').strip()
                lesson.video_url = request.form.get('video_url', '').strip()
                lesson.order = int(request.form.get('order')) if request.form.get('order') else lesson.order
                lesson.duration = int(request.form.get('duration')) if request.form.get('duration') else lesson.duration
                
                db.session.commit()
                flash('Lesson updated successfully!', 'success')
                return redirect(url_for('course.manage_course', course_id=course_id))
                
            except Exception as e:
                db.session.rollback()
                flash('Error updating lesson: ' + str(e), 'error')
                return redirect(url_for('course.manage_course', course_id=course_id))
        
        elif action == 'manage_quiz':
            try:
                lesson_id = request.form.get('lesson_id', type=int)
                quiz_action = request.form.get('quiz_action', 'add')
                lesson = Lesson.query.get_or_404(lesson_id)
                
                if lesson.course_id != course_id:
                    flash('Invalid lesson.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                # Validate required fields
                quiz_title = request.form.get('quiz_title', '').strip()
                if not quiz_title:
                    flash('Quiz title is required.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                passing_score = request.form.get('passing_score', type=int)
                if passing_score is None or passing_score < 0 or passing_score > 100:
                    flash('Invalid passing score. Must be between 0 and 100.', 'error')
                    return redirect(url_for('course.manage_course', course_id=course_id))
                
                # Get or create quiz
                if quiz_action == 'add':
                    # For new quiz, always create a new one
                    quiz = Quiz(lesson_id=lesson_id)
                    db.session.add(quiz)
                else:
                    # For editing, get existing quiz
                    quiz = lesson.quizzes.first()
                    if not quiz:
                        quiz = Quiz(lesson_id=lesson_id)
                        db.session.add(quiz)
                
                # Update quiz details
                quiz.title = quiz_title
                quiz.description = request.form.get('quiz_description', '').strip()
                quiz.passing_score = passing_score
                
                # Handle questions
                if 'questions[]' in request.form:
                    print("DEBUG: Form data received:")
                    print("Questions:", request.form.getlist('questions[]'))
                    print("Question IDs:", request.form.getlist('question_ids[]'))
                    print("Deleted Question IDs:", request.form.getlist('deleted_question_ids[]'))
                    print("Deletion only:", request.form.get('deletion_only'))
                    
                    # Get existing questions
                    existing_questions = {str(q.id): q for q in quiz.questions}  # Convert IDs to strings
                    print("DEBUG: Existing questions:", [q.id for q in quiz.questions])
                    
                    # Get deleted question IDs
                    deleted_question_ids = []
                    for ids in request.form.getlist('deleted_question_ids[]'):
                        if ids:  # Only process non-empty strings
                            deleted_question_ids.extend([id.strip() for id in ids.split(',') if id.strip()])
                    print("DEBUG: Deleted question IDs:", deleted_question_ids)
                    
                    # Delete marked questions first
                    for q_id in deleted_question_ids:
                        if q_id in existing_questions:
                            print(f"DEBUG: Deleting question {q_id}")
                            db.session.delete(existing_questions[q_id])
                            del existing_questions[q_id]
                    
                    # If this is a deletion-only operation or no questions left, commit and return
                    if request.form.get('deletion_only') == 'true' or not request.form.getlist('questions[]'):
                        try:
                            db.session.commit()
                            print("DEBUG: All questions deleted successfully")
                            flash('Quiz questions updated successfully!', 'success')
                            return redirect(url_for('course.manage_course', course_id=course_id))
                        except Exception as e:
                            print("DEBUG: Error committing changes:", str(e))
                            db.session.rollback()
                            raise
                    
                    # Process remaining questions
                    questions = request.form.getlist('questions[]')
                    question_ids = request.form.getlist('question_ids[]')
                    
                    for i, (question_text, question_id) in enumerate(zip(questions, question_ids)):
                        print(f"DEBUG: Processing question {i}:")
                        print(f"  Text: {question_text}")
                        print(f"  ID: {question_id}")
                        
                        question_text = question_text.strip()
                        if not question_text:
                            continue
                            
                        # Get options for this question
                        options = [opt.strip() for opt in request.form.getlist(f'options_{i}[]') if opt.strip()]
                        correct_answer = request.form.get(f'correct_{i}')
                        print(f"  Options: {options}")
                        print(f"  Correct answer: {correct_answer}")
                        
                        # Skip validation if this is a deletion-only operation
                        if not options and not correct_answer and deleted_question_ids:
                            continue
                            
                        # Validate this question's data
                        if not options:
                            flash(f'Question {i+1} must have at least one option.', 'error')
                            return redirect(url_for('course.manage_course', course_id=course_id))
                        if not correct_answer or correct_answer not in options:
                            flash(f'Question {i+1} must have a valid correct answer selected.', 'error')
                            return redirect(url_for('course.manage_course', course_id=course_id))
                            
                        # Handle new or existing question
                        if question_id.startswith('new_'):
                            print(f"  Creating new question")
                            question = Question(
                                quiz_id=quiz.id,
                                question_text=question_text,
                                question_type='multiple_choice',
                                options=options,
                                correct_answer=correct_answer,
                                points=1
                            )
                            db.session.add(question)
                        else:
                            # Convert question_id to string for comparison
                            question_id = str(question_id)
                            if question_id in existing_questions:
                                print(f"  Updating existing question {question_id}")
                                question = existing_questions[question_id]
                                question.question_text = question_text
                                question.options = options
                                question.correct_answer = correct_answer
                    
                    try:
                        db.session.commit()
                        print("DEBUG: Changes committed successfully")
                    except Exception as e:
                        print("DEBUG: Error committing changes:", str(e))
                        db.session.rollback()
                        raise
                
                db.session.commit()
                flash('Quiz ' + ('created' if quiz_action == 'add' else 'updated') + ' successfully!', 'success')
                return redirect(url_for('course.manage_course', course_id=course_id))
                
            except Exception as e:
                db.session.rollback()
                flash('Error ' + ('creating' if quiz_action == 'add' else 'updating') + ' quiz: ' + str(e), 'error')
                return redirect(url_for('course.manage_course', course_id=course_id))
        
        elif action == 'delete_quiz':
            try:
                quiz_id = request.form.get('quiz_id', type=int)
                quiz = Quiz.query.get_or_404(quiz_id)
                lesson = quiz.lesson
                if lesson.course_id != course_id:
                    return jsonify({'error': 'Invalid quiz'}), 400
                # Delete all questions and attempts associated with this quiz
                Question.query.filter_by(quiz_id=quiz.id).delete()
                QuizAttempt.query.filter_by(quiz_id=quiz.id).delete()
                db.session.delete(quiz)
                db.session.commit()
                return jsonify({'success': True})
            except Exception as e:
                import traceback; traceback.print_exc()
                db.session.rollback()
                return jsonify({'error': str(e)}), 500
        elif action == 'delete_lesson':
            try:
                lesson_id = request.form.get('lesson_id', type=int)
                lesson = Lesson.query.get_or_404(lesson_id)
                if lesson.course_id != course_id:
                    return jsonify({'error': 'Invalid lesson'}), 400
                db.session.delete(lesson)
                db.session.commit()
                return jsonify({'success': True})
            except Exception as e:
                import traceback; traceback.print_exc()
                db.session.rollback()
                return jsonify({'error': str(e)}), 500
    
    # Get all lessons for this course
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    
    return render_template('course/manage.html',
                         title='Manage Course',
                         course=course,
                         lessons=lessons)

@bp.route('/<int:course_id>/lesson/<int:lesson_id>/delete')
@login_required
def delete_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if user is the teacher of this course
    if not current_user.is_teacher or course.teacher_id != current_user.id:
        flash('You do not have permission to delete this lesson.', 'error')
        return redirect(url_for('course.view', course_id=course_id))
    
    if lesson.course_id != course_id:
        flash('Invalid lesson.', 'error')
        return redirect(url_for('course.view', course_id=course_id))
    
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully!', 'success')
    return redirect(url_for('course.manage_course', course_id=course_id))

@bp.route('/<int:course_id>/lesson/<int:lesson_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_lesson(course_id, lesson_id):
    course = Course.query.get_or_404(course_id)
    lesson = Lesson.query.get_or_404(lesson_id)
    
    if lesson.course_id != course_id:
        flash('Invalid lesson.', 'error')
        return redirect(url_for('course.view', course_id=course_id))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'manage_quiz':
            try:
                # Validate required fields
                quiz_title = request.form.get('quiz_title', '').strip()
                if not quiz_title:
                    flash('Quiz title is required.', 'error')
                    return redirect(url_for('course.manage_lesson', course_id=course_id, lesson_id=lesson_id))
                
                passing_score = request.form.get('passing_score', type=int)
                if passing_score is None or passing_score < 0 or passing_score > 100:
                    flash('Invalid passing score. Must be between 0 and 100.', 'error')
                    return redirect(url_for('course.manage_lesson', course_id=course_id, lesson_id=lesson_id))
                
                # Get or create quiz
                quiz = lesson.quizzes.first()
                if not quiz:
                    quiz = Quiz(lesson_id=lesson_id)
                    db.session.add(quiz)
                
                # Update quiz details
                quiz.title = quiz_title
                quiz.description = request.form.get('quiz_description', '').strip()
                quiz.passing_score = passing_score
                
                # Delete existing questions
                Question.query.filter_by(quiz_id=quiz.id).delete()
                
                # Add new questions
                questions = request.form.getlist('questions[]')
                for i, question_text in enumerate(questions):
                    question_text = question_text.strip()
                    if not question_text:
                        continue
                    # Get options for this question
                    options = [opt.strip() for opt in request.form.getlist(f'options_{i}[]') if opt.strip()]
                    correct_answer = request.form.get(f'correct_{i}')
                    if not options:
                        flash(f'Question {i+1} must have at least one option.', 'error')
                        return redirect(url_for('course.manage_lesson', course_id=course_id, lesson_id=lesson_id))
                    if not correct_answer or correct_answer not in options:
                        flash(f'Question {i+1} must have a valid correct answer selected.', 'error')
                        return redirect(url_for('course.manage_lesson', course_id=course_id, lesson_id=lesson_id))
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=question_text,
                        question_type='multiple_choice',
                        options=options,
                        correct_answer=correct_answer,
                        points=1
                    )
                    db.session.add(question)
                
                db.session.commit()
                flash('Quiz updated successfully!', 'success')
                return redirect(url_for('course.manage_lesson', course_id=course_id, lesson_id=lesson_id))
                
            except Exception as e:
                db.session.rollback()
                flash('Error updating quiz: ' + str(e), 'error')
                return redirect(url_for('course.manage_lesson', course_id=course_id, lesson_id=lesson_id))
    
    return render_template('course/manage_lesson.html',
                         title='Manage Lesson',
                         course=course,
                         lesson=lesson)

@bp.route('/<int:course_id>/quiz/questions')
@login_required
def get_quiz_questions(course_id):
    course = Course.query.get_or_404(course_id)
    if not current_user.is_teacher or course.teacher_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    quiz_id = request.args.get('quiz_id', type=int)
    lesson_id = request.args.get('lesson_id', type=int)
    quiz = None
    if quiz_id:
        quiz = Quiz.query.get(quiz_id)
    elif lesson_id:
        lesson = Lesson.query.get_or_404(lesson_id)
        if lesson.course_id != course_id:
            return jsonify({'error': 'Invalid lesson'}), 400
        quiz = lesson.quizzes.first()
    if not quiz:
        return jsonify({'questions': []})
    questions = []
    for question in quiz.questions:
        questions.append({
            'id': question.id,
            'question_text': question.question_text,
            'options': question.options,
            'correct_answer': question.correct_answer
        })
    return jsonify({'questions': questions}) 