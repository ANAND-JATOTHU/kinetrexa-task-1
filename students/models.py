from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class StudentManager(models.Manager):
    def get_active_students(self):
        return self.filter(is_active=True)

class Student(TimeStampedModel):
    roll_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)
    gpa = models.DecimalField(max_digits=4, decimal_places=2)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = StudentManager()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_grade(self):
        if self.gpa >= 3.5:
            return 'A'
        elif self.gpa >= 3.0:
            return 'B'
        elif self.gpa >= 2.0:
            return 'C'
        elif self.gpa >= 1.0:
            return 'D'
        else:
            return 'F'

    def __str__(self):
        return f"{self.roll_number} - {self.get_full_name()}"
