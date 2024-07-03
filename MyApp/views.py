# views.py
import json
from io import BytesIO

from django.db.models import Max
from reportlab.pdfgen import canvas

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from MyApp.models import Result, Student, Grade, Notification
from MyApp.serializers import ResultSerializer, GradeSerializer, NotificationSerializer


@csrf_exempt  # Consider adding CSRF protection if appropriate for your application
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')

            if User.objects.filter(**{"email": email}).exists():
                user = User.objects.get(email=email)
                student = Student.objects.get(user=user)
                user = authenticate(username=user.username, password=password)
                if user is not None:
                    login(request, user)
                    return JsonResponse({
                        'success': 'Login successful',
                        'first_name': student.first_name,
                        'last_name': student.last_name,
                        'matric_no': student.matric_no,
                        'email': student.email,
                        'program': student.programme,
                        "user_id": user.id},
                        status=200)
                else:
                    return JsonResponse({'error': 'Invalid credentials'}, status=401)
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            first_name = data.get('first_name').strip()
            last_name = data.get('last_name').strip()
            email = data.get('email').strip()
            matric_no = data.get('matric_no').strip()
            programme = data.get('program').strip()
            level = data.get('level').strip()
            password = data.get('password').strip()
            if User.objects.filter(email=email).exists() or User.objects.filter(username=matric_no).exists():
                return JsonResponse({'error': "User already exists"}, status=400)
            else:
                user = User.objects.create_user(username=matric_no, email=email, password=password)
                Student.objects.create(user=user, first_name=first_name,
                                      last_name=last_name, email=email, matric_no=matric_no,
                                      programme=programme, level=level)
                return JsonResponse({'success': "Registration successful"}, status=200)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def forgot_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email').strip()

            if User.objects.filter(**{"email": email}).exists():
                user = User.objects.get(email=email)
                data = {
                    'user_id': user.id,
                    'success': "Proceed to change password",
                }
                return JsonResponse(data, status=200)
            else:
                data = {
                    'error': "User does not exist",
                }
                # Redirect to dashboard page
                return JsonResponse(data, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def retrieve_password(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            user_id = data.get('user_id').strip()
            user = User.objects.get(id=int(user_id))
            password = data.get('password').strip()
            user.set_password(password)
            user.save()
            data = {
                'success': "Password change successful",
            }
            # Redirect to dashboard page
            return JsonResponse(data, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def logout_user(request):
    # logout user
    logout(request)
    # redirect to login page
    return JsonResponse({}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_notifications(request):
    notifications = Notification.objects.all()
    serializer = NotificationSerializer(notifications, many=True)
    return Response({'notifications': serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_current_semester_results(request, matric_no):
    """
  API view function to retrieve all results for the current user for the most current session and semester.
  """
    try:
        # Get the current user
        user = Student.objects.get(matric_no=matric_no)
    except (ValueError, Student.DoesNotExist):
        return Response({'error': 'Student does not exist'})

    # Get the most current session (assuming sessions are represented by strings)
    result_latest_session = Result.objects.filter(student=user).aggregate(Max('session'))['session__max']
    grade_latest_session = Grade.objects.filter(student=user).aggregate(Max('session'))['session__max']

    # Get all results for the user in the current session
    user_results = Result.objects.filter(student=user, session=result_latest_session)
    user_grade = Grade.objects.filter(student=user, session=grade_latest_session)

    # Filter results further to include only the most current semester
    # (assuming semesters are represented by strings)
    result_latest_semester = Result.objects.order_by('-semester').first().semester
    grade_latest_semester = Grade.objects.order_by('-semester').first().semester

    current_semester_results = user_results.filter(semester=result_latest_semester)
    current_semester_grade = user_grade.get(semester=grade_latest_semester)

    # Serialize the results data
    result_serializer = ResultSerializer(current_semester_results, many=True)
    # grade_serializer = GradeSerializer(current_semester_grade, many=True)

    all_results = []

    for result in current_semester_results:
        all_results.append(
            {
                'course_name': result.course.course_name,
                'course_code': result.course.course_code,
                'score': result.score,
            }
        )

    return JsonResponse({
        'results': all_results,
        'grade': current_semester_grade.gpa,
        'session': result_latest_session,
        'semester': result_latest_semester
    }, status=200, safe=False)


@api_view(['POST'])
def send_feedback(request):
    """
  API view function to receive and send feedback/complaints via email.
  """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        user_id = data.get('user_id')
        subject = data.get('subject')
        message = data.get('content')

        user = User.objects.get(id=int(user_id))
        student = Student.objects.get(user=user)
        subject = f"Feedback/Complaint from {student.matric_no}: {subject}"

        # Validate data (optional)
        if not user_id or not subject or not message:
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        # Send email
        try:
            send_mail(subject, message, 'support@yourdomain.com', [user.email])  # Replace with your support email
            return Response({'success': 'Feedback sent successfully!'})
        except Exception as e:
            return Response({'error': f'An error occurred: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def get_and_send_current_semester_results_pdf(request, matric_no):
    """
  API view function to retrieve, convert to PDF, and send a student's current semester results via email.
  """
    try:
        # Get the student
        student = Student.objects.get(matric_no=matric_no)
    except (ValueError, Student.DoesNotExist):
        return Response({'error': 'Student does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # Get the most current session (assuming sessions are represented by strings)
    current_session = Result.objects.latest('session').session

    # Get all results for the user in the current session
    user_results = Result.objects.filter(student=student, session=current_session)

    # Filter results further to include only the most current semester
    # (assuming semesters are represented by strings)
    most_recent_semester = Result.objects.latest('semester').semester
    current_semester_results = user_results.filter(semester=most_recent_semester)

    # Serialize the results data (optional)
    # serializer = ResultSerializer(current_semester_results, many=True)

    # Generate PDF content
    pdf_buffer = BytesIO()
    p = canvas.Canvas(pdf_buffer)

    # Add title and header information
    p.drawString(100, 700, f"Student Results - {student.matric_no}")
    p.drawString(100, 680, f"Semester: {most_recent_semester} - Session: {current_session}")

    # Add table headers
    p.drawString(50, 650, "Course Code")
    p.drawString(200, 650, "Course Name")
    p.drawString(400, 650, "Score")

    # Write results data into the PDF
    y_position = 630
    for result in current_semester_results:
        p.drawString(50, y_position, result.course.course_code)
        p.drawString(200, y_position, result.course.course_name)
        p.drawString(400, y_position, str(result.score))
        y_position -= 20

    p.save()
    pdf_data = pdf_buffer.getvalue()
    pdf_buffer.close()

    # Send email with PDF attachment
    email = EmailMessage(
        subject=f"Your {most_recent_semester} Semester Results ({current_session})",
        body=f"Hi {student.first_name},\nPlease find your current semester results attached.",
        from_email="noreply@yourdomain.com",  # Replace with your email
        to=[student.email],  # Replace with field containing student email
    )
    email.attach(f"results_{student.matric_no}.pdf", pdf_data, 'application/pdf')
    try:
        email.send()
        return Response({'success': 'Results sent successfully!'})
    except Exception as e:
        return Response({'error': f'An error occurred sending email: {e}'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
