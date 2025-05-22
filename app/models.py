from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')  # 'admin', 'teacher', 'student'
    bio = db.Column(db.Text)
    profile_image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    courses = db.relationship('Course', backref='teacher', lazy='dynamic')
    enrolled_courses = db.relationship('Enrollment', backref='student', lazy='dynamic')
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'bio': self.bio,
            'profile_image': self.profile_image,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'course_count': self.courses.count(),
            'enrollment_count': self.enrolled_courses.count(),
            'quiz_attempt_count': self.quiz_attempts.count()
        }

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    level = db.Column(db.String(20))  # beginner, intermediate, advanced
    duration = db.Column(db.Integer)  # in hours
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    lessons = db.relationship('Lesson', backref='course', lazy='dynamic')
    students = db.relationship('Enrollment', backref='course', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'duration': self.duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'teacher_id': self.teacher_id,
            'teacher_name': self.teacher.username if self.teacher else None,
            'student_count': self.students.count()
        }

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    video_url = db.Column(db.String(200))
    order = db.Column(db.Integer)
    duration = db.Column(db.Integer)  # in minutes
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    quizzes = db.relationship('Quiz', backref='lesson', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'video_url': self.video_url,
            'order': self.order,
            'duration': self.duration,
            'course_id': self.course_id
        }

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)  # Progress percentage
    completed_lessons = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrolled_at': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'progress': self.progress,
            'completed_lessons': self.completed_lessons,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'student_name': self.student.username if self.student else None,
            'course_title': self.course.title if self.course else None
        }

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, default='Quiz')
    description = db.Column(db.Text, default='')
    passing_score = db.Column(db.Integer, default=70)  # Passing score in percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    questions = db.relationship('Question', backref='quiz', lazy='dynamic', cascade='all, delete-orphan')
    attempts = db.relationship('QuizAttempt', back_populates='quiz', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'title': self.title,
            'description': self.description,
            'passing_score': self.passing_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'question_count': self.questions.count(),
            'attempt_count': self.attempts.count()
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False, default='')
    question_type = db.Column(db.String(20), nullable=False, default='multiple_choice')  # 'multiple_choice', 'true_false'
    options = db.Column(db.JSON, default=list)  # For multiple choice questions
    correct_answer = db.Column(db.String(500), nullable=False, default='')
    points = db.Column(db.Integer, default=1)

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float)  # Score in percentage
    answers = db.Column(db.JSON)  # Store user's answers
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    passed = db.Column(db.Boolean)
    quiz = db.relationship('Quiz', back_populates='attempts', lazy='joined')
    previous_best_score = None  # Property to store previous best score

    def calculate_score(self):
        if not self.answers:
            return 0
        
        total_points = 0
        earned_points = 0
        
        for question in self.quiz.questions:
            total_points += question.points
            user_answer = self.answers.get(str(question.id))
            if user_answer == question.correct_answer:
                earned_points += question.points
        
        self.score = (earned_points / total_points) * 100 if total_points > 0 else 0
        self.passed = self.score >= self.quiz.passing_score
        self.completed_at = datetime.utcnow()
        return self.score

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id)) 