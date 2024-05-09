from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Student(AbstractUser):
    last_name = models.CharField(max_length=250)
    first_name = models.CharField(max_length=250)
    matric_no = models.CharField(max_length=12)
    email = models.EmailField()
    programme = models.CharField(max_length=50, choices=[
        ('Computer Science', 'Computer Science'),
        ('Software Engineering', 'Software Engineering'),
        ('Cyber Security', 'Cyber Security'),
        ('Biochemistry', 'Biochemistry'),
        ('Industrial Chemistry', 'Industrial Chemistry'),
        ('Business Administration', 'Business Administration'),
        ('Mass Communication', 'Mass Communication'),
        ('Criminology', 'Criminology'),
        ('Microbiology', 'Microbiology'),
        ('Economics', 'Economics'),
        ('Accounting', 'Accounting'),
    ])
    level = models.CharField(max_length=3, choices=[
        ('100', '100'),
        ('200', '200'),
        ('300', '300'),
        ('400', '400'),
    ])

    def __str__(self):
        return f"{self.last_name} {self.first_name}"


class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=255)

    def __str__(self):
        return self.course_code + " - " + self.course_name


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10, choices=[
        ('alpha', 'Alpha'),
        ('omega', 'Omega'),
    ])
    session = models.CharField(max_length=10, choices=[
        ('2023/2024', '2023/2024'),
        ('2024/2025', '2024/2025'),
        ('2025/2026', '2025/2026'),
        ('2026/2027', '2026/2027'),
    ])
    score = models.FloatField()

    class Meta:
        unique_together = (
        ('student', 'course', 'semester'),)  # Ensures a student can only have one result for a course in a semester

    def __str__(self):
        return f"{self.student.matric_number} - {self.course.course_code} ({self.semester} {self.session}) - {self.score}"


class Notification(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
