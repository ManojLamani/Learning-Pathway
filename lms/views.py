from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q, Count, Avg
from .models import (
    User, Course, Enrollment, Module, Lesson, Assignment,
    AssignmentSubmission, Quiz, Question, QuizAttempt, QuizAnswer,
    Badge, StudentBadge, Discussion, DiscussionReply,
    StudentProfile, InstructorProfile, LessonProgress, ModuleProgress
)
from .forms import (
    UserRegisterForm, CourseForm, ModuleForm, LessonForm,
    AssignmentForm, AssignmentSubmissionForm, GradeAssignmentForm,
    QuizForm, QuestionForm, AwardBadgeForm
)

# Home and Authentication Views
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    courses = Course.objects.filter(is_published=True)[:6]
    return render(request, 'lms/home.html', {'courses': courses})

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate and login the user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                role_display = 'Instructor' if user.role == 'instructor' else 'Student'
                messages.success(request, f'Welcome {username}! Your {role_display} account has been created.')
                return redirect('dashboard')
        else:
            # Add form errors to messages for debugging
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = UserRegisterForm()
    
    return render(request, 'lms/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    role_display = 'Instructor' if user.role == 'instructor' else 'Student'
                    messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Your account is inactive. Please contact support.')
            else:
                # Check if user exists to provide better error message
                user_exists = User.objects.filter(username=username).exists()
                if user_exists:
                    messages.error(request, 'Invalid password. Please try again or use "Forgot password?"')
                else:
                    messages.error(request, f'No account found with username "{username}". Please check your username or register.')
        else:
            messages.error(request, 'Please provide username and password.')
    
    return render(request, 'lms/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

# Dashboard Views
@login_required
def dashboard(request):
    # Debug: Print user role
    print(f"DEBUG: User {request.user.username} has role: {request.user.role}")
    
    if request.user.role == 'instructor':
        print(f"DEBUG: Redirecting to instructor dashboard")
        return instructor_dashboard(request)
    else:
        print(f"DEBUG: Redirecting to student dashboard")
        return student_dashboard(request)

@login_required
def instructor_dashboard(request):
    # Ensure user is instructor
    if request.user.role != 'instructor':
        messages.error(request, 'Access denied. This page is for instructors only.')
        return redirect('home')
    
    courses = Course.objects.filter(instructor=request.user)
    total_students = Enrollment.objects.filter(course__instructor=request.user).count()
    total_assignments = Assignment.objects.filter(course__instructor=request.user).count()
    total_quizzes = Quiz.objects.filter(course__instructor=request.user).count()
    
    context = {
        'courses': courses,
        'total_students': total_students,
        'total_assignments': total_assignments,
        'total_quizzes': total_quizzes,
    }
    return render(request, 'lms/instructor_dashboard.html', context)

@login_required
def student_dashboard(request):
    # Ensure user is student
    if request.user.role != 'student':
        messages.error(request, 'Access denied. This page is for students only.')
        return redirect('home')
    
    # Get enrolled courses
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    # Get available courses (published and not enrolled)
    enrolled_course_ids = enrollments.values_list('course_id', flat=True)
    available_courses = Course.objects.filter(is_published=True).exclude(id__in=enrolled_course_ids)[:6]
    
    # Get assignments from enrolled courses
    recent_assignments = Assignment.objects.filter(
        course__enrollments__student=request.user
    ).order_by('-due_date')[:5]
    
    # Get quizzes from enrolled courses
    recent_quizzes = Quiz.objects.filter(
        course__enrollments__student=request.user
    ).order_by('-created_at')[:5]
    
    # Get earned badges
    earned_badges = StudentBadge.objects.filter(student=request.user).select_related('badge')
    
    # Stats
    total_enrollments = enrollments.count()
    total_assignments = Assignment.objects.filter(course__enrollments__student=request.user).count()
    total_quizzes = Quiz.objects.filter(course__enrollments__student=request.user).count()
    
    context = {
        'enrollments': enrollments,
        'available_courses': available_courses,
        'recent_assignments': recent_assignments,
        'recent_quizzes': recent_quizzes,
        'earned_badges': earned_badges,
        'total_enrollments': total_enrollments,
        'total_assignments': total_assignments,
        'total_quizzes': total_quizzes,
    }
    return render(request, 'lms/student_dashboard.html', context)

# Course Views
@login_required
def course_list(request):
    if request.user.role == 'instructor':
        courses = Course.objects.filter(instructor=request.user)
        enrolled_course_ids = []
    else:
        courses = Course.objects.filter(is_published=True)
        # Get list of enrolled course IDs for this student
        enrolled_course_ids = list(Enrollment.objects.filter(
            student=request.user
        ).values_list('course_id', flat=True))
    
    return render(request, 'lms/course_list.html', {
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids
    })

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role == 'student':
        enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        context = {
            'course': course,
            'enrolled': enrolled,
            'modules': course.modules.all(),
            'assignments': course.assignments.all(),
            'quizzes': course.quizzes.all(),
        }
    else:
        if course.instructor != request.user:
            return HttpResponseForbidden()
        context = {
            'course': course,
            'modules': course.modules.all(),
            'assignments': course.assignments.all(),
            'quizzes': course.quizzes.all(),
            'enrollments': course.enrollments.all(),
        }
    
    return render(request, 'lms/course_detail.html', context)

@login_required
def course_create(request):
    if request.user.role != 'instructor':
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm()
    
    return render(request, 'lms/course_form.html', {'form': form})

@login_required
def course_edit(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = CourseForm(instance=course)
    
    return render(request, 'lms/course_form.html', {'form': form, 'course': course})

@login_required
def course_delete(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('course_list')
    return render(request, 'lms/course_confirm_delete.html', {'course': course})

@login_required
def enroll_course(request, course_id):
    if request.user.role != 'student':
        return HttpResponseForbidden()
    
    course = get_object_or_404(Course, id=course_id, is_published=True)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    
    if created:
        messages.success(request, f'Successfully enrolled in {course.title}')
    else:
        messages.info(request, 'You are already enrolled in this course')
    
    return redirect('course_detail', course_id=course.id)


# Password Reset Views
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

def password_reset_request(request):
    """Request password reset"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Create reset link
            reset_link = request.build_absolute_uri(
                f'/password-reset-confirm/{uid}/{token}/'
            )
            
            # For development, just show the link
            messages.success(
                request, 
                f'Password reset link (for development): {reset_link}'
            )
            
            # In production, send email:
            # send_mail(
            #     'Password Reset Request',
            #     f'Click here to reset your password: {reset_link}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [email],
            #     fail_silently=False,
            # )
            
            return redirect('password_reset_done')
        except User.DoesNotExist:
            messages.error(request, 'No user found with that email address.')
    
    return render(request, 'lms/password_reset.html')

def password_reset_done(request):
    """Password reset email sent confirmation"""
    return render(request, 'lms/password_reset_done.html')

def password_reset_confirm(request, uidb64, token):
    """Confirm password reset with token"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 and password1 == password2:
                user.set_password(password1)
                user.save()
                messages.success(request, 'Your password has been reset successfully!')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
        
        return render(request, 'lms/password_reset_confirm.html', {
            'validlink': True,
            'uidb64': uidb64,
            'token': token
        })
    else:
        messages.error(request, 'The password reset link is invalid or has expired.')
        return render(request, 'lms/password_reset_confirm.html', {'validlink': False})

def password_reset_complete(request):
    """Password reset complete"""
    return render(request, 'lms/password_reset_complete.html')


# Profile Views
@login_required
def student_profile(request, user_id=None):
    """View student profile"""
    if user_id:
        student = get_object_or_404(User, id=user_id, role='student')
    else:
        student = request.user
    
    # Get or create profile
    profile, created = StudentProfile.objects.get_or_create(user=student)
    if created:
        profile.update_stats()
    
    # Get enrolled courses
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    
    # Get completed modules
    completed_modules = ModuleProgress.objects.filter(
        student=student,
        is_completed=True
    ).select_related('module', 'module__course')
    
    # Get earned badges
    earned_badges = StudentBadge.objects.filter(student=student).select_related('badge', 'course', 'awarded_by')
    
    # Get progress statistics
    total_lessons = LessonProgress.objects.filter(student=student).count()
    completed_lessons = LessonProgress.objects.filter(student=student, is_completed=True).count()
    
    context = {
        'student': student,
        'profile': profile,
        'enrollments': enrollments,
        'completed_modules': completed_modules,
        'earned_badges': earned_badges,
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
    }
    
    return render(request, 'lms/student_profile.html', context)

@login_required
def instructor_profile(request, user_id=None):
    """View instructor profile"""
    if user_id:
        instructor = get_object_or_404(User, id=user_id, role='instructor')
    else:
        instructor = request.user
        # Ensure current user is instructor
        if instructor.role != 'instructor':
            messages.error(request, 'Access denied. This page is for instructors only.')
            return redirect('home')
    
    # Get or create profile
    profile, created = InstructorProfile.objects.get_or_create(user=instructor)
    if created:
        profile.update_stats()
    
    # Get created courses
    courses = Course.objects.filter(instructor=instructor)
    
    # Get students
    students = User.objects.filter(
        enrollments__course__instructor=instructor
    ).distinct()
    
    # Get badges awarded by instructor
    awarded_badges = StudentBadge.objects.filter(
        awarded_by=instructor,
        is_instructor_awarded=True
    ).select_related('student', 'badge', 'course')
    
    context = {
        'instructor': instructor,
        'profile': profile,
        'courses': courses,
        'students': students,
        'awarded_badges': awarded_badges,
    }
    
    return render(request, 'lms/instructor_profile.html', context)

@login_required
def award_badge_manual(request, student_id, course_id):
    """Manually award badge to student"""
    if request.user.role != 'instructor':
        return HttpResponseForbidden()
    
    student = get_object_or_404(User, id=student_id, role='student')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    # Check if student is enrolled
    if not Enrollment.objects.filter(student=student, course=course).exists():
        messages.error(request, 'Student is not enrolled in this course.')
        return redirect('course_detail', course_id=course_id)
    
    if request.method == 'POST':
        form = AwardBadgeForm(request.POST)
        if form.is_valid():
            badge = form.cleaned_data['badge']
            note = form.cleaned_data.get('note', '')
            
            # Create badge award
            student_badge, created = StudentBadge.objects.get_or_create(
                student=student,
                badge=badge,
                course=course,
                defaults={
                    'awarded_by': request.user,
                    'is_instructor_awarded': True,
                    'note': note
                }
            )
            
            if created:
                messages.success(request, f'Badge "{badge.name}" awarded to {student.get_full_name() or student.username}!')
            else:
                messages.info(request, 'Student already has this badge.')
            
            return redirect('course_detail', course_id=course_id)
    else:
        form = AwardBadgeForm()
    
    context = {
        'form': form,
        'student': student,
        'course': course,
    }
    
    return render(request, 'lms/award_badge.html', context)

@login_required
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as completed"""
    if request.user.role != 'student':
        return HttpResponseForbidden()
    
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check if student is enrolled in the course
    if not Enrollment.objects.filter(student=request.user, course=lesson.module.course).exists():
        messages.error(request, 'You must be enrolled in this course.')
        return redirect('course_detail', course_id=lesson.module.course.id)
    
    # Get or create lesson progress
    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson
    )
    
    # Mark as complete
    progress.mark_complete()
    
    messages.success(request, f'Lesson "{lesson.title}" marked as complete!')
    
    # Redirect back to lesson or course
    return redirect('lesson_detail', lesson_id=lesson_id)

@login_required
def student_progress_dashboard(request):
    """Student progress dashboard"""
    if request.user.role != 'student':
        return HttpResponseForbidden()
    
    # Get profile
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if created:
        profile.update_stats()
    
    # Get all enrollments with progress
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    # Get module progress for each enrollment
    progress_data = []
    for enrollment in enrollments:
        modules = Module.objects.filter(course=enrollment.course)
        module_progress = []
        
        for module in modules:
            progress, created = ModuleProgress.objects.get_or_create(
                student=request.user,
                module=module
            )
            if created:
                progress.update_completion()
            
            module_progress.append({
                'module': module,
                'progress': progress
            })
        
        progress_data.append({
            'enrollment': enrollment,
            'module_progress': module_progress
        })
    
    # Get recent badges
    recent_badges = StudentBadge.objects.filter(student=request.user).order_by('-awarded_at')[:5]
    
    context = {
        'profile': profile,
        'progress_data': progress_data,
        'recent_badges': recent_badges,
    }
    
    return render(request, 'lms/student_progress_dashboard.html', context)
