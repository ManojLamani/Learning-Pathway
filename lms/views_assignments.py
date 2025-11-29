from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Course, Assignment, AssignmentSubmission, Enrollment, StudentBadge, Badge
from .forms import AssignmentForm, AssignmentSubmissionForm, GradeAssignmentForm, AwardBadgeForm

# Assignment Views
@login_required
def assignment_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.course = course
            assignment.save()
            messages.success(request, 'Assignment created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = AssignmentForm()
    
    return render(request, 'lms/assignment_form.html', {'form': form, 'course': course})

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    course = assignment.course
    
    context = {'assignment': assignment, 'course': course}
    
    if request.user.role == 'student':
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return HttpResponseForbidden()
        
        try:
            submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user)
            context['submission'] = submission
        except AssignmentSubmission.DoesNotExist:
            context['submission'] = None
    
    elif request.user.role == 'instructor':
        if course.instructor != request.user:
            return HttpResponseForbidden()
        
        submissions = AssignmentSubmission.objects.filter(assignment=assignment)
        context['submissions'] = submissions
    
    return render(request, 'lms/assignment_detail.html', context)

@login_required
def assignment_edit(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if assignment.course.instructor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment updated successfully!')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'lms/assignment_form.html', {'form': form, 'assignment': assignment, 'course': assignment.course})

@login_required
def assignment_delete(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if assignment.course.instructor != request.user:
        return HttpResponseForbidden()
    
    course_id = assignment.course.id
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'Assignment deleted successfully!')
        return redirect('course_detail', course_id=course_id)
    
    return render(request, 'lms/assignment_confirm_delete.html', {'assignment': assignment})

@login_required
def assignment_submit(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.user.role != 'student':
        return HttpResponseForbidden()
    
    if not Enrollment.objects.filter(student=request.user, course=assignment.course).exists():
        return HttpResponseForbidden()
    
    submission, created = AssignmentSubmission.objects.get_or_create(
        assignment=assignment,
        student=request.user
    )
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentSubmissionForm(instance=submission)
    
    return render(request, 'lms/assignment_submit.html', {
        'form': form,
        'assignment': assignment,
        'submission': submission
    })

@login_required
def assignment_grade(request, submission_id):
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    
    if submission.assignment.course.instructor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = GradeAssignmentForm(request.POST, instance=submission)
        if form.is_valid():
            graded_submission = form.save(commit=False)
            graded_submission.graded_at = timezone.now()
            graded_submission.save()
            messages.success(request, 'Assignment graded successfully!')
            return redirect('assignment_detail', assignment_id=submission.assignment.id)
    else:
        form = GradeAssignmentForm(instance=submission)
    
    return render(request, 'lms/assignment_grade.html', {
        'form': form,
        'submission': submission,
        'assignment': submission.assignment
    })

@login_required
def award_badge_to_student(request, student_id, course_id):
    if request.user.role != 'instructor':
        return HttpResponseForbidden()
    
    from .models import User
    student = get_object_or_404(User, id=student_id, role='student')
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    if request.method == 'POST':
        form = AwardBadgeForm(request.POST)
        if form.is_valid():
            badge = form.cleaned_data['badge']
            
            # Check if already awarded
            if not StudentBadge.objects.filter(student=student, badge=badge, course=course).exists():
                StudentBadge.objects.create(
                    student=student,
                    badge=badge,
                    course=course,
                    awarded_by=request.user
                )
                messages.success(request, f'Badge "{badge.name}" awarded to {student.username}!')
            else:
                messages.info(request, 'This badge has already been awarded to this student for this course.')
            
            return redirect('course_detail', course_id=course.id)
    else:
        form = AwardBadgeForm()
    
    return render(request, 'lms/award_badge.html', {
        'form': form,
        'student': student,
        'course': course
    })
