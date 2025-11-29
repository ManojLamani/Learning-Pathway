from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone
from .models import Course, Quiz, Question, QuizAttempt, QuizAnswer, Enrollment
from .forms import QuizForm, QuestionForm

# Quiz Views
@login_required
def quiz_create(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.save()
            messages.success(request, 'Quiz created successfully!')
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm()
    
    return render(request, 'lms/quiz_form.html', {'form': form, 'course': course})

@login_required
def quiz_detail(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    
    context = {'quiz': quiz, 'course': course}
    
    if request.user.role == 'student':
        if not Enrollment.objects.filter(student=request.user, course=course).exists():
            return HttpResponseForbidden()
        
        attempts = QuizAttempt.objects.filter(quiz=quiz, student=request.user).order_by('-started_at')
        context['attempts'] = attempts
        context['questions'] = quiz.questions.all()
    
    elif request.user.role == 'instructor':
        if course.instructor != request.user:
            return HttpResponseForbidden()
        
        context['questions'] = quiz.questions.all()
        context['attempts'] = QuizAttempt.objects.filter(quiz=quiz)
    
    return render(request, 'lms/quiz_detail.html', context)

@login_required
def quiz_edit(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.course.instructor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, 'Quiz updated successfully!')
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'lms/quiz_form.html', {'form': form, 'quiz': quiz, 'course': quiz.course})

@login_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.course.instructor != request.user:
        return HttpResponseForbidden()
    
    course_id = quiz.course.id
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, 'Quiz deleted successfully!')
        return redirect('course_detail', course_id=course_id)
    
    return render(request, 'lms/quiz_confirm_delete.html', {'quiz': quiz})

# Question Views
@login_required
def question_create(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if quiz.course.instructor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question created successfully!')
            return redirect('quiz_detail', quiz_id=quiz.id)
    else:
        form = QuestionForm()
    
    return render(request, 'lms/question_form.html', {'form': form, 'quiz': quiz})

@login_required
def question_edit(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.quiz.course.instructor != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully!')
            return redirect('quiz_detail', quiz_id=question.quiz.id)
    else:
        form = QuestionForm(instance=question)
    
    return render(request, 'lms/question_form.html', {'form': form, 'question': question, 'quiz': question.quiz})

@login_required
def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.quiz.course.instructor != request.user:
        return HttpResponseForbidden()
    
    quiz_id = question.quiz.id
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('quiz_detail', quiz_id=quiz_id)
    
    return render(request, 'lms/question_confirm_delete.html', {'question': question})

# Quiz Attempt Views
@login_required
def quiz_take(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if request.user.role != 'student':
        return HttpResponseForbidden()
    
    if not Enrollment.objects.filter(student=request.user, course=quiz.course).exists():
        return HttpResponseForbidden()
    
    # Check if student has already attempted this quiz
    existing_attempt = QuizAttempt.objects.filter(
        quiz=quiz,
        student=request.user,
        is_completed=True
    ).first()
    
    if existing_attempt:
        messages.warning(request, 'You have already completed this quiz. You can only attempt each quiz once.')
        return redirect('quiz_result', attempt_id=existing_attempt.id)
    
    # Check for incomplete attempt
    incomplete_attempt = QuizAttempt.objects.filter(
        quiz=quiz,
        student=request.user,
        is_completed=False
    ).first()
    
    if incomplete_attempt:
        # Continue existing attempt
        return redirect('quiz_attempt', attempt_id=incomplete_attempt.id)
    
    # Create new attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        student=request.user
    )
    
    return redirect('quiz_attempt', attempt_id=attempt.id)

@login_required
def quiz_attempt(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    
    if attempt.is_completed:
        return redirect('quiz_result', attempt_id=attempt.id)
    
    questions = attempt.quiz.questions.all()
    
    if request.method == 'POST':
        # Save answers
        score = 0
        total_marks = 0
        
        for question in questions:
            selected_answer = request.POST.get(f'question_{question.id}')
            if selected_answer:
                is_correct = selected_answer == question.correct_answer
                QuizAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_answer=selected_answer,
                    is_correct=is_correct
                )
                
                if is_correct:
                    score += question.marks
                total_marks += question.marks
        
        # Update attempt
        attempt.score = score
        attempt.submitted_at = timezone.now()
        attempt.is_completed = True
        attempt.save()
        
        messages.success(request, 'Quiz submitted successfully!')
        return redirect('quiz_result', attempt_id=attempt.id)
    
    return render(request, 'lms/quiz_attempt.html', {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'questions': questions
    })

@login_required
def quiz_result(request, attempt_id):
    attempt = get_object_or_404(QuizAttempt, id=attempt_id)
    
    # Check access
    if request.user.role == 'student' and attempt.student != request.user:
        return HttpResponseForbidden()
    elif request.user.role == 'instructor' and attempt.quiz.course.instructor != request.user:
        return HttpResponseForbidden()
    
    answers = attempt.answers.all().select_related('question')
    
    return render(request, 'lms/quiz_result.html', {
        'attempt': attempt,
        'quiz': attempt.quiz,
        'answers': answers
    })
