from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Course, Module, Lesson
from .forms import ModuleForm, LessonForm

# Module Views
@login_required
def module_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.save()
            messages.success(request, 'Module created successfully!')
            return redirect('course_detail', course_id=course.id)
    else:
        form = ModuleForm()
    
    return render(request, 'lms/module_form.html', {'form': form, 'course': course})

@login_required
def module_edit(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if module.course.instructor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = ModuleForm(request.POST, instance=module)
        if form.is_valid():
            form.save()
            messages.success(request, 'Module updated successfully!')
            return redirect('course_detail', course_id=module.course.id)
    else:
        form = ModuleForm(instance=module)
    
    return render(request, 'lms/module_form.html', {'form': form, 'module': module, 'course': module.course})

@login_required
def module_delete(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if module.course.instructor != request.user:
        return HttpResponseForbidden()
    
    course_id = module.course.id
    if request.method == 'POST':
        module.delete()
        messages.success(request, 'Module deleted successfully!')
        return redirect('course_detail', course_id=course_id)
    
    return render(request, 'lms/module_confirm_delete.html', {'module': module})

# Lesson Views
@login_required
def lesson_create(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if module.course.instructor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.module = module
            lesson.save()
            messages.success(request, 'Lesson created successfully!')
            return redirect('course_detail', course_id=module.course.id)
    else:
        form = LessonForm()
    
    return render(request, 'lms/lesson_form.html', {'form': form, 'module': module})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course = lesson.module.course
    
    # Check access
    if request.user.role == 'student':
        from .models import Enrollment
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return HttpResponseForbidden()
    elif request.user.role == 'instructor':
        if course.instructor != request.user:
            return HttpResponseForbidden()
    
    return render(request, 'lms/lesson_detail.html', {'lesson': lesson, 'course': course})

@login_required
def lesson_edit(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.module.course.instructor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lesson updated successfully!')
            return redirect('lesson_detail', lesson_id=lesson.id)
    else:
        form = LessonForm(instance=lesson)
    
    return render(request, 'lms/lesson_form.html', {'form': form, 'lesson': lesson, 'module': lesson.module})

@login_required
def lesson_delete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if lesson.module.course.instructor != request.user:
        return HttpResponseForbidden()
    
    course_id = lesson.module.course.id
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, 'Lesson deleted successfully!')
        return redirect('course_detail', course_id=course_id)
    
    return render(request, 'lms/lesson_confirm_delete.html', {'lesson': lesson})
