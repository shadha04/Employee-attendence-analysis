from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Department(models.Model):
    name=models.CharField(max_length=200)

class Log(AbstractUser):
    usertype=models.CharField(max_length=20)
    
class Employee(models.Model):
    employee=models.ForeignKey(Log,on_delete=models.CASCADE)
    department=models.ForeignKey(Department,on_delete=models.CASCADE)
    phno=models.IntegerField()
    image=models.ImageField(upload_to='media/',blank=True,null=True)
    address=models.TextField(max_length=300)
    reg_date=models.DateField(auto_now_add=True)
    approve_date=models.DateTimeField(null=True,blank=True)


class Attendence(models.Model):
    CHOICE=[
        ('Present','Present'),
        ('Absent','Absent'),
        ('Pending','Pending'),
    ]
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
    date=models.DateField()
    time=models.TimeField(null=True,blank=True)
    status=models.CharField(max_length=20,choices=CHOICE,default='Pending')
    half_day=models.BooleanField(default=False)


class Leave(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
    reason=models.TextField()
    start_date=models.DateField(blank=True,null=True)
    end_date=models.DateField(blank=True,null=True)
    status=models.CharField(max_length=20,default='Pending')