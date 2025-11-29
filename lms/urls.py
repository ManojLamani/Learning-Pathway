from django.urls import path
from . import views
from .views_modules import (
    module_create, module_edit, module_delete,
    lesson_create, lesson_detail, lesson_edit, lesson_delete
)
from .views_assignments import (
    assignment_create, assignment_detail, assignment_edit, assignment_delete,
    assignment_submit, assignment_grade, award_badge_to_student
)
from .views_quizzes import (
    quiz_create, quiz_detail, quiz_edit, quiz_delete,
    question_create, question_edit, question_delete,
    quiz_take, quiz_attempt, quiz_result
)

urlpatterns = [
    # Home and Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Password Reset
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:course_id>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:course_id>/delete/', views.course_delete, name='course_delete'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Modules
    path('courses/<int:course_id>/modules/create/', module_create, name='module_create'),
    path('modules/<int:module_id>/edit/', module_edit, name='module_edit'),
    path('modules/<int:module_id>/delete/', module_delete, name='module_delete'),
    
    # Lessons
    path('modules/<int:module_id>/lessons/create/', lesson_create, name='lesson_create'),
    path('lessons/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('lessons/<int:lesson_id>/edit/', lesson_edit, name='lesson_edit'),
    path('lessons/<int:lesson_id>/delete/', lesson_delete, name='lesson_delete'),
    
    # Assignments
    path('courses/<int:course_id>/assignments/create/', assignment_create, name='assignment_create'),
    path('assignments/<int:assignment_id>/', assignment_detail, name='assignment_detail'),
    path('assignments/<int:assignment_id>/edit/', assignment_edit, name='assignment_edit'),
    path('assignments/<int:assignment_id>/delete/', assignment_delete, name='assignment_delete'),
    path('assignments/<int:assignment_id>/submit/', assignment_submit, name='assignment_submit'),
    path('submissions/<int:submission_id>/grade/', assignment_grade, name='assignment_grade'),
    
    # Quizzes
    path('courses/<int:course_id>/quizzes/create/', quiz_create, name='quiz_create'),
    path('quizzes/<int:quiz_id>/', quiz_detail, name='quiz_detail'),
    path('quizzes/<int:quiz_id>/edit/', quiz_edit, name='quiz_edit'),
    path('quizzes/<int:quiz_id>/delete/', quiz_delete, name='quiz_delete'),
    path('quizzes/<int:quiz_id>/take/', quiz_take, name='quiz_take'),
    
    # Questions
    path('quizzes/<int:quiz_id>/questions/create/', question_create, name='question_create'),
    path('questions/<int:question_id>/edit/', question_edit, name='question_edit'),
    path('questions/<int:question_id>/delete/', question_delete, name='question_delete'),
    
    # Quiz Attempts
    path('attempts/<int:attempt_id>/', quiz_attempt, name='quiz_attempt'),
    path('attempts/<int:attempt_id>/result/', quiz_result, name='quiz_result'),
    
    # Badges
    path('courses/<int:course_id>/students/<int:student_id>/award-badge/', award_badge_to_student, name='award_badge'),
    path('courses/<int:course_id>/students/<int:student_id>/award-badge-manual/', views.award_badge_manual, name='award_badge_manual'),
    
    # Profiles
    path('profile/student/', views.student_profile, name='student_profile'),
    path('profile/student/<int:user_id>/', views.student_profile, name='student_profile_view'),
    path('profile/instructor/', views.instructor_profile, name='instructor_profile'),
    path('profile/instructor/<int:user_id>/', views.instructor_profile, name='instructor_profile_view'),
    
    # Progress
    path('progress/dashboard/', views.student_progress_dashboard, name='progress_dashboard'),
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
]
