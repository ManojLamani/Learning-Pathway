from django.core.management.base import BaseCommand
from lms.models import Badge

class Command(BaseCommand):
    help = 'Create default badges for the LMS'

    def handle(self, *args, **options):
        badges_data = [
            {
                'name': 'Module Completion',
                'description': 'Awarded for completing a module',
                'badge_type': 'module_complete',
                'icon': '📘'
            },
            {
                'name': 'Course Completion',
                'description': 'Awarded for completing a course',
                'badge_type': 'course_complete',
                'icon': '🎓'
            },
            {
                'name': 'Quiz Master',
                'description': 'Awarded for scoring well on quizzes',
                'badge_type': 'quiz_master',
                'icon': '🧠'
            },
            {
                'name': 'Assignment Ace',
                'description': 'Awarded for excellent assignment performance',
                'badge_type': 'assignment_ace',
                'icon': '📝'
            },
            {
                'name': 'Perfect Score',
                'description': 'Awarded for achieving a perfect score',
                'badge_type': 'perfect_score',
                'icon': '💯'
            }
        ]

        created_count = 0
        for badge_data in badges_data:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} badges'
            )
        )
