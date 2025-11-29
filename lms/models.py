from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_courses')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ('student', 'course')
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"
    
    def update_progress(self):
        """Calculate and update course progress based on completed items"""
        course = self.course
        student = self.student
        
        # Get all modules in course
        modules = course.modules.all()
        if not modules.exists():
            self.progress = 0
            self.save()
            return 0
        
        total_items = 0
        completed_items = 0
        
        # Count lessons
        for module in modules:
            lessons = module.lessons.all()
            total_items += lessons.count()
            completed_items += LessonProgress.objects.filter(
                student=student,
                lesson__in=lessons,
                is_completed=True
            ).count()
        
        # Count assignments
        assignments = course.assignments.all()
        total_items += assignments.count()
        completed_items += AssignmentSubmission.objects.filter(
            student=student,
            assignment__in=assignments
        ).exclude(marks__isnull=True).count()
        
        # Count quizzes
        quizzes = course.quizzes.all()
        total_items += quizzes.count()
        completed_items += QuizAttempt.objects.filter(
            student=student,
            quiz__in=quizzes,
            is_completed=True
        ).count()
        
        # Calculate progress
        if total_items > 0:
            self.progress = round((completed_items / total_items) * 100, 2)
        else:
            self.progress = 0
        
        self.save()
        
        # Auto-award course completion badge if 100%
        if self.progress == 100:
            self._award_course_completion_badge()
        
        return self.progress
    
    def _award_course_completion_badge(self):
        """Award course completion badge"""
        badge, created = Badge.objects.get_or_create(
            badge_type='course_complete',
            defaults={
                'name': 'Course Completion',
                'description': f'Completed {self.course.title}',
                'icon': '🎓'
            }
        )
        StudentBadge.objects.get_or_create(
            student=self.student,
            badge=badge,
            course=self.course,
            defaults={'is_instructor_awarded': False}
        )

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    attachment = models.FileField(upload_to='assignment_files/', null=True, blank=True)
    due_date = models.DateTimeField()
    max_marks = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    text_answer = models.TextField(blank=True)
    file_submission = models.FileField(upload_to='submissions/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('assignment', 'student')
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.IntegerField(default=30)
    max_marks = models.IntegerField(default=100)
    pass_marks = models.IntegerField(default=40)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    marks = models.IntegerField(default=1)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"

class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} - Attempt"

class QuizAnswer(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('attempt', 'question')
    
    def __str__(self):
        return f"Answer for {self.question}"

class Badge(models.Model):
    BADGE_TYPES = (
        ('module_complete', 'Module Completion'),
        ('course_complete', 'Course Completion'),
        ('quiz_master', 'Quiz Master'),
        ('assignment_ace', 'Assignment Ace'),
        ('perfect_score', 'Perfect Score'),
    )
    
    name = models.CharField(max_length=100)
    description = models.TextField()
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES)
    icon = models.CharField(max_length=50, default='🏆')
    
    def __str__(self):
        return self.name

class StudentBadge(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    module = models.ForeignKey(Module, on_delete=models.CASCADE, null=True, blank=True)
    awarded_at = models.DateTimeField(auto_now_add=True)
    awarded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='awarded_badges')
    is_instructor_awarded = models.BooleanField(default=False)
    note = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-awarded_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.badge.name}"

# Profile Models
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    total_courses_enrolled = models.IntegerField(default=0)
    total_courses_completed = models.IntegerField(default=0)
    total_modules_completed = models.IntegerField(default=0)
    total_badges_earned = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def update_stats(self):
        """Update profile statistics"""
        self.total_courses_enrolled = Enrollment.objects.filter(student=self.user).count()
        self.total_courses_completed = Enrollment.objects.filter(student=self.user, progress=100).count()
        self.total_modules_completed = ModuleProgress.objects.filter(student=self.user, is_completed=True).count()
        self.total_badges_earned = StudentBadge.objects.filter(student=self.user).count()
        self.save()

class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    total_courses_created = models.IntegerField(default=0)
    total_students = models.IntegerField(default=0)
    total_badges_awarded = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Instructor Profile"
    
    def update_stats(self):
        """Update instructor statistics"""
        self.total_courses_created = Course.objects.filter(instructor=self.user).count()
        self.total_students = Enrollment.objects.filter(course__instructor=self.user).values('student').distinct().count()
        self.total_badges_awarded = StudentBadge.objects.filter(awarded_by=self.user, is_instructor_awarded=True).count()
        self.save()

# Progress Tracking Models
class LessonProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ('student', 'lesson')
        ordering = ['lesson__order']
    
    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"
    
    def mark_complete(self):
        """Mark lesson as completed"""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()
            # Check if module is completed
            self.check_module_completion()
    
    def check_module_completion(self):
        """Check if all lessons in module are completed"""
        module = self.lesson.module
        module_progress, created = ModuleProgress.objects.get_or_create(
            student=self.student,
            module=module
        )
        module_progress.update_completion()

class ModuleProgress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='module_progress')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    completion_percentage = models.FloatField(default=0.0)
    
    class Meta:
        unique_together = ('student', 'module')
        ordering = ['module__order']
    
    def __str__(self):
        return f"{self.student.username} - {self.module.title}"
    
    def update_completion(self):
        """Update module completion status"""
        # Check lessons
        total_lessons = self.module.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            student=self.student,
            lesson__module=self.module,
            is_completed=True
        ).count()
        
        # Check quizzes (if any)
        module_quizzes = Quiz.objects.filter(course=self.module.course)
        completed_quizzes = QuizAttempt.objects.filter(
            student=self.student,
            quiz__in=module_quizzes,
            is_completed=True
        ).count()
        
        # Check assignments (if any)
        module_assignments = Assignment.objects.filter(course=self.module.course)
        completed_assignments = AssignmentSubmission.objects.filter(
            student=self.student,
            assignment__in=module_assignments
        ).exclude(marks__isnull=True).count()
        
        # Calculate total requirements
        total_requirements = total_lessons
        completed_requirements = completed_lessons
        
        if total_requirements > 0:
            self.completion_percentage = (completed_requirements / total_requirements) * 100
        
        # Mark as completed if all requirements met
        if total_lessons > 0 and completed_lessons == total_lessons:
            if not self.is_completed:
                self.is_completed = True
                self.completed_at = timezone.now()
                self.save()
                # Award badge automatically
                self.award_module_badge()
        else:
            self.save()
    
    def award_module_badge(self):
        """Automatically award badge when module is completed"""
        from django.db.models.signals import post_save
        # Create or get module completion badge
        badge, created = Badge.objects.get_or_create(
            badge_type='module_complete',
            defaults={
                'name': f'{self.module.title} Completion',
                'description': f'Completed all lessons in {self.module.title}',
                'icon': '🎓'
            }
        )
        
        # Award badge if not already awarded
        StudentBadge.objects.get_or_create(
            student=self.student,
            badge=badge,
            module=self.module,
            course=self.module.course,
            defaults={
                'is_instructor_awarded': False
            }
        )
        
        # Update student profile stats
        if hasattr(self.student, 'student_profile'):
            self.student.student_profile.update_stats()

class Discussion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

class DiscussionReply(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reply to {self.discussion.title}"
