from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    User, StudentProfile, InstructorProfile, 
    ModuleProgress, StudentBadge, Enrollment,
    AssignmentSubmission, QuizAttempt, LessonProgress
)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created"""
    if created:
        if instance.role == 'student':
            StudentProfile.objects.create(user=instance)
        elif instance.role == 'instructor':
            InstructorProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved"""
    if instance.role == 'student' and hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    elif instance.role == 'instructor' and hasattr(instance, 'instructor_profile'):
        instance.instructor_profile.save()

@receiver(post_save, sender=ModuleProgress)
def check_module_completion_badge(sender, instance, created, **kwargs):
    """Award badge when module is completed"""
    if instance.is_completed and not created:
        # This is handled in the model's award_module_badge method
        pass

@receiver(post_save, sender=StudentBadge)
def update_profiles_on_badge_award(sender, instance, created, **kwargs):
    """Update profiles when badge is awarded"""
    if created:
        # Update student profile
        if hasattr(instance.student, 'student_profile'):
            instance.student.student_profile.update_stats()
        
        # Update instructor profile if manually awarded
        if instance.is_instructor_awarded and instance.awarded_by:
            if hasattr(instance.awarded_by, 'instructor_profile'):
                instance.awarded_by.instructor_profile.update_stats()

@receiver(post_save, sender=Enrollment)
def update_student_profile_on_enrollment(sender, instance, created, **kwargs):
    """Update student profile when enrolled in course"""
    if created:
        if hasattr(instance.student, 'student_profile'):
            instance.student.student_profile.update_stats()
        # Initialize progress
        instance.update_progress()

# Update progress when assignments are graded
from django.db.models.signals import post_save
from .models import AssignmentSubmission, QuizAttempt

@receiver(post_save, sender=AssignmentSubmission)
def update_progress_on_assignment(sender, instance, **kwargs):
    """Update course progress and award badges when assignment is graded"""
    if instance.marks is not None:
        from .models import Badge, StudentBadge
        
        # Update course progress
        enrollment = Enrollment.objects.filter(
            student=instance.student,
            course=instance.assignment.course
        ).first()
        if enrollment:
            enrollment.update_progress()
        
        # Award badge for completing assignment (any score)
        completion_badge = Badge.objects.filter(
            badge_type='assignment_ace',
            name='Assignment Completed'
        ).first()
        
        if not completion_badge:
            completion_badge = Badge.objects.create(
                name='Assignment Completed',
                badge_type='assignment_ace',
                description='Completed an assignment',
                icon='✅'
            )
        
        StudentBadge.objects.get_or_create(
            student=instance.student,
            badge=completion_badge,
            course=instance.assignment.course,
            defaults={'is_instructor_awarded': False}
        )
        
        # Auto-award Assignment Ace badge for 90%+ score
        percentage = (instance.marks / instance.assignment.max_marks) * 100
        if percentage >= 90:
            ace_badge = Badge.objects.filter(
                badge_type='assignment_ace',
                name='Assignment Ace'
            ).first()
            
            if not ace_badge:
                ace_badge = Badge.objects.create(
                    name='Assignment Ace',
                    badge_type='assignment_ace',
                    description='Scored 90%+ on assignment',
                    icon='📝'
                )
            
            StudentBadge.objects.get_or_create(
                student=instance.student,
                badge=ace_badge,
                course=instance.assignment.course,
                defaults={'is_instructor_awarded': False}
            )

@receiver(post_save, sender=QuizAttempt)
def update_progress_on_quiz(sender, instance, **kwargs):
    """Update course progress and award badges when quiz is completed"""
    if instance.is_completed:
        from .models import Badge, StudentBadge
        
        # Update course progress
        enrollment = Enrollment.objects.filter(
            student=instance.student,
            course=instance.quiz.course
        ).first()
        if enrollment:
            enrollment.update_progress()
        
        # Award badge for completing quiz (any score)
        completion_badge = Badge.objects.filter(
            badge_type='quiz_master',
            name='Quiz Completed'
        ).first()
        
        if not completion_badge:
            completion_badge = Badge.objects.create(
                name='Quiz Completed',
                badge_type='quiz_master',
                description='Completed a quiz',
                icon='✅'
            )
        
        StudentBadge.objects.get_or_create(
            student=instance.student,
            badge=completion_badge,
            course=instance.quiz.course,
            defaults={'is_instructor_awarded': False}
        )
        
        # Auto-award Quiz Master badge for 90%+ score
        if instance.score and instance.quiz.max_marks:
            percentage = (instance.score / instance.quiz.max_marks) * 100
            if percentage >= 90:
                master_badge = Badge.objects.filter(
                    badge_type='quiz_master',
                    name='Quiz Master'
                ).first()
                
                if not master_badge:
                    master_badge = Badge.objects.create(
                        name='Quiz Master',
                        badge_type='quiz_master',
                        description='Scored 90%+ on quiz',
                        icon='🧠'
                    )
                
                StudentBadge.objects.get_or_create(
                    student=instance.student,
                    badge=master_badge,
                    course=instance.quiz.course,
                    defaults={'is_instructor_awarded': False}
                )
            
            # Auto-award Perfect Score badge for 100%
            if percentage == 100:
                perfect_badge = Badge.objects.filter(
                    badge_type='perfect_score',
                    name='Perfect Score'
                ).first()
                
                if not perfect_badge:
                    perfect_badge = Badge.objects.create(
                        name='Perfect Score',
                        badge_type='perfect_score',
                        description='Achieved 100% score',
                        icon='💯'
                    )
                
                StudentBadge.objects.get_or_create(
                    student=instance.student,
                    badge=perfect_badge,
                    course=instance.quiz.course,
                    defaults={'is_instructor_awarded': False}
                )


@receiver(post_save, sender=LessonProgress)
def update_progress_on_lesson(sender, instance, **kwargs):
    """Update course progress when lesson is completed"""
    if instance.is_completed:
        enrollment = Enrollment.objects.filter(
            student=instance.student,
            course=instance.lesson.module.course
        ).first()
        if enrollment:
            enrollment.update_progress()
