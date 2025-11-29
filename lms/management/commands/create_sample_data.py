from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from lms.models import Course, Module, Lesson, Assignment, Quiz, Question

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample course data for testing'

    def handle(self, *args, **options):
        # Create instructor if doesn't exist
        instructor, created = User.objects.get_or_create(
            username='instructor',
            defaults={
                'email': 'instructor@example.com',
                'role': 'instructor',
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        if created:
            instructor.set_password('password123')
            instructor.save()
            self.stdout.write('Created instructor user')

        # Create student if doesn't exist
        student, created = User.objects.get_or_create(
            username='student',
            defaults={
                'email': 'student@example.com',
                'role': 'student',
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        )
        if created:
            student.set_password('password123')
            student.save()
            self.stdout.write('Created student user')

        # Create course
        course, created = Course.objects.get_or_create(
            title='Introduction to Python Programming',
            defaults={
                'description': 'Learn the fundamentals of Python programming language',
                'instructor': instructor,
                'is_published': True
            }
        )
        course.instructor = instructor
        course.save()
        
        if created:
            self.stdout.write('Created sample course')

        # Create modules
        module1, _ = Module.objects.get_or_create(
            course=course,
            title='Python Basics',
            defaults={
                'description': 'Introduction to Python syntax and basic concepts',
                'order': 1
            }
        )

        module2, _ = Module.objects.get_or_create(
            course=course,
            title='Control Structures',
            defaults={
                'description': 'Learn about loops, conditionals, and control flow',
                'order': 2
            }
        )

        # Create lessons
        lesson1, _ = Lesson.objects.get_or_create(
            module=module1,
            title='Variables and Data Types',
            defaults={
                'content': 'In this lesson, you will learn about variables and different data types in Python...',
                'order': 1
            }
        )

        lesson2, _ = Lesson.objects.get_or_create(
            module=module1,
            title='Functions',
            defaults={
                'content': 'Learn how to define and use functions in Python...',
                'order': 2
            }
        )

        # Create assignment
        assignment, _ = Assignment.objects.get_or_create(
            course=course,
            title='Python Basics Assignment',
            defaults={
                'description': 'Complete the following Python exercises to demonstrate your understanding...',
                'due_date': '2025-12-31 23:59:59',
                'max_marks': 100
            }
        )

        # Create quiz
        quiz, _ = Quiz.objects.get_or_create(
            course=course,
            title='Python Basics Quiz',
            defaults={
                'description': 'Test your knowledge of Python basics',
                'duration_minutes': 30,
                'max_marks': 20,
                'pass_marks': 12
            }
        )

        # Create questions
        questions_data = [
            {
                'quiz': quiz,
                'question_text': 'Which of the following is a valid Python variable name?',
                'option_a': '1variable',
                'option_b': 'variable-1',
                'option_c': 'variable_1',
                'option_d': 'variable 1',
                'correct_answer': 'C',
                'marks': 2,
                'order': 1
            },
            {
                'quiz': quiz,
                'question_text': 'What is the output of print(2 ** 3)?',
                'option_a': '6',
                'option_b': '8',
                'option_c': '9',
                'option_d': 'None of the above',
                'correct_answer': 'B',
                'marks': 2,
                'order': 2
            }
        ]

        for q_data in questions_data:
            Question.objects.get_or_create(
                quiz=q_data['quiz'],
                question_text=q_data['question_text'],
                defaults=q_data
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created sample course data\n'
                'Instructor credentials: instructor / password123\n'
                'Student credentials: student / password123'
            )
        )
