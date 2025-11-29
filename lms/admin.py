from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Course, Enrollment, Module, Lesson, Assignment,
    AssignmentSubmission, Quiz, Question, QuizAttempt, QuizAnswer,
    Badge, StudentBadge, Discussion, DiscussionReply
)

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'profile_picture', 'bio')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'profile_picture', 'bio')}),
    )
    
    def save_model(self, request, obj, form, change):
        """Custom save method to validate email before saving"""
        email = form.cleaned_data.get('email')
        if email:
            # Check if email ends with a valid domain extension
            valid_domains = ['.com', '.org', '.edu', '.gov', '.net', '.io', '.co', '.ai', '.tech', '.in']
            if not any(email.lower().endswith(domain) for domain in valid_domains):
                from django.forms import ValidationError
                raise ValidationError(
                    'Please enter a valid email address ending with a proper domain (e.g., .com, .org, .edu, etc.)'
                )
        super().save_model(request, obj, form, change)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'progress')
    list_filter = ('enrolled_at',)
    search_fields = ('student__username', 'course__title')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'created_at')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'order', 'created_at')
    list_filter = ('module__course', 'created_at')
    search_fields = ('title', 'content')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'max_marks', 'created_at')
    list_filter = ('course', 'due_date', 'created_at')
    search_fields = ('title', 'description')

@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at', 'marks', 'graded_at')
    list_filter = ('submitted_at', 'graded_at')
    search_fields = ('student__username', 'assignment__title')

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'duration_minutes', 'max_marks', 'pass_marks')
    list_filter = ('course', 'created_at')
    search_fields = ('title', 'description')

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'correct_answer', 'marks', 'order')
    list_filter = ('quiz',)
    search_fields = ('question_text',)

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'started_at', 'submitted_at', 'score', 'is_completed')
    list_filter = ('is_completed', 'started_at', 'submitted_at')
    search_fields = ('student__username', 'quiz__title')

@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_answer', 'is_correct')
    list_filter = ('is_correct',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'icon')
    list_filter = ('badge_type',)
    search_fields = ('name', 'description')

@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ('student', 'badge', 'course', 'awarded_at', 'awarded_by')
    list_filter = ('awarded_at', 'badge__badge_type')
    search_fields = ('student__username', 'badge__name')

@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'user', 'created_at', 'is_pinned')
    list_filter = ('is_pinned', 'created_at', 'course')
    search_fields = ('title', 'content')

@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('discussion', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)
