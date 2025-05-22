import random
from app import create_app, db
from app.models import User, Course, Lesson, Quiz, Question

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create users
    teacher = User(username='teacher1', email='teacher1@example.com', role='teacher')
    teacher.set_password('password')
    student = User(username='student1', email='student1@example.com', role='student')
    student.set_password('password')
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('admin123')
    db.session.add_all([teacher, student, admin])
    db.session.commit()

    # Create courses
    categories = ['Programming', 'Design', 'Business']
    levels = ['beginner', 'intermediate', 'advanced']
    for i in range(1, 4):
        course = Course(
            title=f"Course {i}",
            description=f"Description for Course {i}",
            category=random.choice(categories),
            level=random.choice(levels),
            duration=random.randint(10, 30),
            teacher_id=teacher.id
        )
        db.session.add(course)
        db.session.commit()

        # Create lessons for each course
        for j in range(1, 4):
            lesson = Lesson(
                title=f"Lesson {j} of Course {i}",
                content=f"Content for Lesson {j} of Course {i}",
                video_url="https://www.youtube.com/embed/dQw4w9WgXcQ",
                order=j,
                duration=random.randint(10, 60),
                course_id=course.id
            )
            db.session.add(lesson)
            db.session.commit()

            # Create quiz for each lesson
            quiz = Quiz(
                lesson_id=lesson.id,
                title=f"Quiz for Lesson {j} of Course {i}",
                description=f"Test your knowledge about Lesson {j} of Course {i}",
                passing_score=70
            )
            db.session.add(quiz)
            db.session.commit()

            # Create questions for each quiz
            for k in range(1, 4):
                options = ["Option A", "Option B", "Option C", "Option D"]
                correct_answer = random.choice(options)
                q = Question(
                    quiz_id=quiz.id,
                    question_text=f"What is the answer to question {k} in Lesson {j} of Course {i}?",
                    question_type='multiple_choice',
                    options=options,
                    correct_answer=correct_answer,
                    points=1
                )
                db.session.add(q)
            db.session.commit()

    print("Dummy data created!") 