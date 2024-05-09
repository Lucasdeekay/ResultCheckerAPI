# views.py
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response

from MyApp.models import Result, Student
from MyApp.serializers import ResultSerializer


@csrf_exempt  # Consider adding CSRF protection if appropriate for your application
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            email = data.get('email')
            password = data.get('password')

            if User.objects.filter(**{"email": email}).exists():
                username = User.objects.get(email=email).username
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return JsonResponse({'success': 'Login successful', 'username': user.username}, status=200)
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
            username = data.get('username').strip()
            first_name = data.get('first_name').strip()
            last_name = data.get('last_name').strip()
            email = data.get('email').strip()
            matric_number = data.get('matric_number').strip()
            programme = data.get('programme').strip()
            level = data.get('level').strip()
            password = data.get('password').strip()
            if Student.objects.filter(**{"username": username, "email": email}).exists():
                return JsonResponse({'error': "User already exists"}, status=400)
            else:
                Student.object.create_user(username=username, password=password, first_name=first_name, last_name=last_name, email=email, matric_number=matric_number, programme=programme, level=level)
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
    current_session = Result.objects.latest('session').session

    # Get all results for the user in the current session
    user_results = Result.objects.filter(student=user, session=current_session)

    # Filter results further to include only the most current semester
    # (assuming semesters are represented by strings)
    most_recent_semester = Result.objects.latest('semester').semester
    current_semester_results = user_results.filter(semester=most_recent_semester)

    # Serialize the results data
    serializer = ResultSerializer(current_semester_results, many=True)
    return Response(serializer.data)
