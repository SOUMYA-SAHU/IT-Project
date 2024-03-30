from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Details,Course
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    return render(request,'index.html')

def signin_student(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('studentlanding_page')  # Redirect to home page after successful login
        else:
            messages.warning(request, "Invalid username or password")
            return render(request, 'signin_student.html')

    return render(request, 'signin_student.html')

def signin_teacher(request):
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
              login(request, user)
              return redirect('teacherlanding_page')  # Redirect to home page after successful login
            else:
             messages.warning(request, "Invalid username or password")
        return render(request, 'signin_teacher.html')

def signup(request):
    if request.method == "POST":
        name = request.POST['name']
        regno = request.POST['regno']
        email = request.POST['email']
        gender = request.POST['gender']
        contact_number = request.POST['contact_number']
        branch = request.POST['branch']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            messages.warning(request, "Passwords do not match.")
            return redirect('signup')  # Redirect to signup page if passwords don't match
        
        try:
            # Create the user with username as email and password
            user = User.objects.create_user(username=regno, email=email, password=password)
            
            # Create the associated details record
            details = Details.objects.create(user=user, regno=regno, name=name, email=email, gender=gender,
                                             contact_number=contact_number, branch=branch)
            
            messages.success(request, "Account created successfully.")
            return redirect('signin_student')  # Redirect to login page after successful signup
        
        except Exception as e:
            messages.error(request, f"Failed to create account: {e}")
            return redirect('signup')  # Redirect to signup page if any exception occurs
    
    return render(request, 'signup.html')

@login_required
def studentlanding_page(request):
    # Get the logged-in user's profile
    # profile = Details.objects.get(user=request.user)
    # context = {
    #     'username': profile.name,
    #     # 'profile_picture': profile.profile_picture.url if profile.profile_picture else None
    # }
    # return render(request, 'student_landingpage.html', context)
    user = request.user
    try:
        details = Details.objects.get(user=user)
    except Details.DoesNotExist:
        # Handle the case where Details record does not exist for the user
        return HttpResponse("Details record does not exist for this user.")
    announcements = Announcement.objects.filter(section__isnull=False)  # Fetch announcements with a specific section
    teacher = Teacher.objects.filter(user=user).first()
    
    if teacher:
        announcements = announcements.filter(section=teacher.section, regno__course_code=teacher.course_code)
    else:
        student_sections = StudentSection.objects.filter(regno__user=user)
        if student_sections.exists():
            sections = [section.section for section in student_sections]
            course_codes = [section.regno.course_code for section in student_sections]
            announcements = announcements.filter(section__in=sections, regno__course_code__in=course_codes)
        else:
            # If the user is not a teacher and not enrolled in any sections, return only global announcements
            announcements = Announcement.objects.filter(section__isnull=True)

    return render(request, 'student_landingpage.html', {'announcements': announcements, 'username': details.name, 'details': details})

    # Continue with the view logic using the details object
    # return render(request, 'student_landingpage.html', {'username': details.name, 'details': details})

@login_required
def teacherlanding_page(request):
        profile = Details.objects.get(user=request.user)
        context = {
            'username': profile.name,
        }
        return render(request, 'teacher_landingpage.html', context)
@login_required
def teacher_addcourse(request):
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_code = request.POST.get('course_code')
        dept = request.POST.get('dept')
        try:
            Course.objects.create(course_name=course_name, course_code=course_code, dept=dept)
            messages.success(request, 'Course added successfully.')
            return redirect('teacher_addcourse')
        except Exception as e:
            messages.error(request, f'Failed to add course. Error: {e}')
            return redirect('teacher_addcourse')      
    return render(request, 'teacher_addcourse.html')
# Create your views here.

from .models import Course, StudentCourse

@login_required
def course_dashboard(request):
    if request.user.is_authenticated:
        student = request.user.details
        student_department = student.branch
    else:
        student_department = None

    if student_department:
        available_courses = Course.objects.filter(dept=student_department).exclude(studentcourse__regno=student)
    else:
        available_courses = None

    if student:
        opted_courses = StudentCourse.objects.filter(regno=student).select_related('course_code')
    else:
        opted_courses = None

    context = {
        'available_courses': available_courses,
        'opted_courses': opted_courses
    }
    return render(request, 'course_dashboard.html', context)

def opt_course(request):
    if request.method == 'POST':
        # Get the logged-in student
        student = request.user.details
        # Get the course IDs selected by the student
        selected_course_ids = request.POST.getlist('course_id')
        # Opt each selected course for the student
        for course_id in selected_course_ids:
            course = Course.objects.get(id=course_id)
            # Check if the student has already opted for the course
            if not StudentCourse.objects.filter(regno=student, course_code=course).exists():
                # Opt the course for the student
                StudentCourse.objects.create(regno=student, course_code=course)

    # Redirect to the course dashboard after opting courses
    return redirect('course_dashboard')

def drop_course(request, course_id):
    if request.method == 'POST':
        # Get the logged-in student
        student = request.user.details
        # Get the course object
        course = Course.objects.get(id=course_id)
        # Drop the course for the student
        StudentCourse.objects.filter(regno=student, course_code=course).delete()

    # Redirect to the course dashboard after dropping a course
    return redirect('course_dashboard')


def student_detail(request):
    # Assuming the authenticated user is the teacher
    if request.user.is_authenticated:
        teacher_department = request.user.details.branch
        # Retrieve students belonging to the same department as the teacher
        student_courses = StudentCourse.objects.filter(course_code__dept=teacher_department)
    else:
        student_courses = None

    context = {
        'student_courses': student_courses
    }
    return render(request, 'student_detail.html', context)

def update_attendance(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        attendance = request.POST.get('attendance')
        if course_id and attendance:
            # Validate attendance value
            try:
                attendance = float(attendance)
                if 0 <= attendance <= 100:  # Assuming attendance is a percentage
                    # Update attendance for the course
                    StudentCourse.objects.filter(id=course_id).update(attendance=attendance)
            except ValueError:
                pass  # Invalid attendance value

    return redirect('student_detail')

def update_marks(request):
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        marks = request.POST.get('marks')
        if course_id and marks:
            # Validate marks value
            try:
                marks = float(marks)
                # Assuming marks can be any numeric value
                # You can add your validation logic here
                # Update marks for the course
                StudentCourse.objects.filter(id=course_id).update(course_marks=marks)
            except ValueError:
                pass  # Invalid marks value

    return redirect('student_detail')

from .models import Teacher, Course, StudentSection, Announcement


@login_required
def teacher_course_details(request):
    try:
        # Get the teacher associated with the current user
        teacher = Teacher.objects.get(user=request.user)
        profile = Details.objects.get(user=request.user)
        context = {
            'username': profile.name,
        }
        # Fetch courses assigned to the teacher based on the department
        courses = Course.objects.filter(dept=teacher.regno.branch)
        
        course_details = []
        for course in courses:
            # Get student courses for each course
            student_courses = StudentCourse.objects.filter(course_code=course)
            sections = []
            for student_course in student_courses:
                # Get sections for each student course
                section = StudentSection.objects.filter(regno=student_course.regno, section=teacher.section).first()
                if section:
                    sections.append(section.section)
            # Count students enrolled in each section
            section_details = []
            for section in sections:
                students_count = StudentSection.objects.filter(section=section).count()
                section_details.append({'section': section, 'students_count': students_count})
            course_details.append({'course_name': course.course_name, 'course_code': course.course_code, 'dept': course.dept, 'sections': section_details})
    except Teacher.DoesNotExist:
        # Handle the case where the teacher doesn't exist
        course_details = []
        

    return render(request, 'teacher_course_details.html', {'course_details': course_details, 'context': context})


def create_announcement(request):
    profile = Details.objects.get(user=request.user)
    context = {
            'username': profile.name,
        }
    if request.method == 'POST':
        message = request.POST.get('message')
        section = request.POST.get('section')
        course_code = request.POST.get('course_code')
        global_announcement = request.POST.get('global_announcement')
        
        if global_announcement:
            # Create a global announcement
            Announcement.objects.create(regno=request.user.details, message=message)
        elif course_code and section:
            # Create an announcement for a specific course code and section
            Announcement.objects.create(regno=request.user.details, message=message, section=section)
            
    return render(request, 'create_announcement.html',context)


# def view_specific_announcements(request):
#     user = request.user
#     announcements = Announcement.objects.filter(section__isnull=False)  # Fetch announcements with a specific section
#     teacher = Teacher.objects.filter(user=user).first()
#     if teacher:
#         announcements = announcements.filter(section=teacher.section, regno__course_code=teacher.course_code)
#     else:
#         student_sections = StudentSection.objects.filter(regno__user=user)
#         if student_sections.exists():
#             sections = [section.section for section in student_sections]
#             course_codes = [section.regno.course_code for section in student_sections]
#             announcements = announcements.filter(section__in=sections, regno__course_code__in=course_codes)
#         else:
#             # If the user is not a teacher and not enrolled in any sections, return an empty queryset
#             announcements = Announcement.objects.none()
    
#     return render(request, 'student_landingpage.html', {'announcements': announcements})

# def view_global_announcements(request):
#     announcements = Announcement.objects.filter(section__isnull=True)  # Fetch global announcements
#     return render(request, 'student_landingpage.html', {'announcements': announcements})
