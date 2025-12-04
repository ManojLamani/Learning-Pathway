from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import (
    User, Course, Module, Lesson, Assignment, AssignmentSubmission,
    Quiz, Question, QuizAnswer, Badge, StudentBadge,
    StudentProfile, InstructorProfile, LessonProgress, ModuleProgress
)

class UserRegisterForm(forms.Form):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
    ]
    
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, label='I am a')
    first_name = forms.CharField(max_length=150, required=False, label='Full name')
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True, label='Password')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email already exists
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('This email is already registered.')
            # Check if email ends with a valid domain extension
            valid_domains = ['.com', '.org', '.edu', '.gov', '.net', '.io', '.co', '.ai', '.tech', '.in']
            if not any(email.lower().endswith(domain) for domain in valid_domains):
                raise forms.ValidationError(
                    'Please enter a valid email address ending with a proper domain (e.g., .com, .org, .edu, etc.)'
                )
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # Check minimum length
            if len(password) < 8:
                raise forms.ValidationError('Password must be at least 8 characters long.')
            # Check if password contains both letters and numbers
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError('Password must contain at least one number.')
            if not any(char.isalpha() for char in password):
                raise forms.ValidationError('Password must contain at least one letter.')
        return password
    
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data.get('first_name', ''),
            role=self.cleaned_data['role']
        )
        return user

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'thumbnail', 'is_published']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'content', 'video_url', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class AssignmentForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-input',
            'id': 'due_date_input'
        }),
        input_formats=['%Y-%m-%d'],
        help_text='Assignment due date (cannot be in the past)'
    )
    
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'attachment', 'due_date', 'max_marks']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'attachment':
                self.fields[field].widget.attrs.update({'class': 'form-input'})
    
    def clean_due_date(self):
        """Validate that due date is not in the past"""
        from django.utils import timezone
        from datetime import datetime
        
        due_date = self.cleaned_data.get('due_date')
        if due_date:
            # Convert date to datetime for comparison
            due_datetime = datetime.combine(due_date, datetime.min.time())
            due_datetime = timezone.make_aware(due_datetime)
            
            # Get current date (start of today)
            today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            if due_datetime < today:
                raise forms.ValidationError('Due date cannot be in the past. Please select today or a future date.')
        
        return due_date

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['text_answer', 'file_submission']
        widgets = {
            'text_answer': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Enter your answer here...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text_answer'].widget.attrs.update({'class': 'form-input'})

class GradeAssignmentForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['marks', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide feedback...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'duration_minutes', 'max_marks', 'pass_marks']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'marks', 'order']
        widgets = {
            'question_text': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-input'})

class AwardBadgeForm(forms.ModelForm):
    note = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional note for the student...'}),
        required=False
    )
    
    class Meta:
        model = StudentBadge
        fields = ['badge', 'note']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['badge'].widget.attrs.update({'class': 'form-input'})
        self.fields['note'].widget.attrs.update({'class': 'form-input'})
