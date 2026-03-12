from django.shortcuts import render,redirect
from .models import Log,Employee,Attendence,Leave,Department
from django.http import HttpResponse
from django.contrib.auth import authenticate,login
from django.utils.timezone import now
from django.contrib import messages
from django.utils.timezone import now
from django.utils import timezone
from datetime import time, timedelta,date
from django.db.models import Case, When, IntegerField, Value
from datetime import datetime


# Create your views here.

def reg(request):
    dep = Department.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name').strip()
        email = request.POST.get('email').strip()
        address = request.POST.get('address').strip()
        phno = request.POST.get('phno').strip()
        department_id = request.POST.get('department')
        pas = request.POST.get('pass').strip()
        con = request.POST.get('conpass').strip()
        image = request.FILES.get('image')

        if Log.objects.filter(username=name).exists():
            messages.error(request, "Username already exists")
        elif Log.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
        elif pas != con:
            messages.error(request, "Passwords do not match")
        else:
         
            x = Log.objects.create_user(
                username=name,
                email=email,
                password=pas,
                is_active=False,
                usertype='pending'
            )

            department = Department.objects.get(id=department_id)

            Employee.objects.create(
                employee=x,
                department=department,
                phno=phno,
                address=address,
                image=image
            )

            messages.success(request, "Registered Successfully! Wait for admin approval.")
            return redirect('/')  
    return render(request, 'reg.html', {'departments': dep})


def log(request):
    if request.method=='POST':
        na=request.POST.get('name').strip()
        pas=request.POST.get('pass').strip()
        x=authenticate(username=na,password=pas)
        if x is not None and x.is_superuser:
            return redirect('admin_home')
        elif x is not None and x.is_active==1:
            login(request,x)
            request.session['employee']=x.id
            return redirect('employee')
        else:
            return HttpResponse('Invalid user')

    return render(request,'login.html')

def admin(request):
    return render(request,'admin.html')

def employee(request):
    return render(request,'employee.html')



def dashboard(request):

    today = now().date()
    total_emp = Employee.objects.filter(employee__usertype='employee').count()

    total_department = Department.objects.count()

    attendence_today = Attendence.objects.filter(date=today).count()

    pending_leave = Leave.objects.filter(status='Pending').count()

    dep_list = []
    departments = Department.objects.all()

    for dep in departments:

        emp_count = Employee.objects.filter(
            department=dep,
            employee__usertype='employee'
        ).count()

        dep_list.append({
            'id': dep.id,
            'name': dep.name,
            'emp_count': emp_count
        })


    emp_list = Employee.objects.select_related(
        'department','employee'
    ).filter(employee__usertype='employee')
    attendance_list = Attendence.objects.filter(
        date=today
    ).select_related(
        'employee',
        'employee__department',
        'employee__employee'
    )
    pending_leave_list = Leave.objects.filter(
        status='Pending'
    ).select_related(
        'employee',
        'employee__department',
        'employee__employee'
    )

    context = {
        'total_emp': total_emp,
        'total_department': total_department,
        'attendence': attendence_today,
        'pending_leave': pending_leave,
        'dep_list': dep_list,
        'emp_list': emp_list,
        'attendance_list': attendance_list,
        'pending_leave_list': pending_leave_list
    }

    return render(request, 'dashboard.html', context)

def department(request):
    if request.method == "POST":
        dep_name = request.POST.get("name")
        if dep_name:
            Department.objects.create(name=dep_name)
            return redirect('department')

    deps = Department.objects.all()
    dep_list = []
    for dep in deps:
        emp_count = Employee.objects.filter(employee__is_active=True,department=dep).count()
        dep_list.append({'id': dep.id, 'name': dep.name, 'emp_count': emp_count})

    return render(request, 'department.html', {'dep_list': dep_list})

def dep_del(request,id):
    dep=Department.objects.get(id=id)
    dep.delete()
    return HttpResponse("<script>window.location='/department/';</script>")

def edit_dep(request, id):
    dep = Department.objects.get(id=id)

    if request.method == 'POST':
        name = request.POST.get('name').strip()
        if Department.objects.filter(name__iexact=name).exclude(id=id).exists():
    
            error = "Department with this name already exists."
            return render(request, 'edit_dep.html', {'data': dep, 'error': error})

        dep.name = name
        dep.save()
        return redirect('department')

    return render(request, 'edit_dep.html', {'data': dep})

def approve(request):
    x=Employee.objects.filter(employee__is_active=False)
    return render(request,'approve.html',{'data':x})

def view_emp(request):
    x = Employee.objects.filter(employee__is_active=True).order_by('-approve_date')
    return render(request, 'view_emp.html', {'data': x})


def attendance(request):

    today = now().date()

    employees = Employee.objects.filter(employee__is_active=True)

    data = []

    for emp in employees:

        attendance = Attendence.objects.filter(
            employee=emp,
            date=today
        ).first()

        leave = Leave.objects.filter(
            employee=emp,
            start_date__lte=today,
            end_date__gte=today,
            status="Approved"
        ).exists()

        if leave:
            status = "Leave"
            time = "-"

        elif attendance:
            status = attendance.status
            time = attendance.time   

        else:
            status = "Pending"
            time = "-"

        data.append({
            "employee": emp,
            "date": today,
            "time": time,
            "status": status
        })

    return render(request, 'attendance.html', {'data': data})


def leave(request):

    leaves = Leave.objects.select_related('employee__employee').annotate(
        status_order=Case(
            When(status='Pending', then=Value(0)),
            When(status='Approved', then=Value(1)),
            When(status='Rejected', then=Value(2)),
            output_field=IntegerField()
        )
    ).order_by('status_order', '-start_date')


    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')

        try:
            leave = Leave.objects.get(id=leave_id)
            leave.status = action
            leave.save()
        except Leave.DoesNotExist:
            pass

        return redirect('leave')

    return render(request, 'leave.html', {'data': leaves})

def select(request,id):
    x=Employee.objects.get(id=id)
    x.employee.is_active=True
    x.employee.usertype='employee'
    x.employee.save()
    x.approve_date = timezone.now()
    x.save()
    messages.success(request, f"Employee {x.employee.username} approved successfully!")
    return redirect('approve')


def emp_edit(request,id):
    x=Employee.objects.get(id=id)
    return render(request,'edit_emp.html',{'data':x})

def del_emp(request,id):
    x=Employee.objects.get(id=id)
    x.employee.is_active=False
    x.employee.usertype='pending'
    x.employee.save()
    x.delete()
    return redirect('view_emp')


def emp_attendence(request):

    emp = Employee.objects.get(employee=request.user)

    now_time = timezone.localtime()
    today = now_time.date()

    cutoff = time(15, 0)  

    leave_today = Leave.objects.filter(
        employee=emp,
        start_date__lte=today,
        end_date__gte=today,
        status='Approved'
    ).exists()

    attendance_today = Attendence.objects.filter(
        employee=emp,
        date=today
    ).first()

    message = None
    timeout = False

    if leave_today:
    
        Attendence.objects.create(
            employee=emp,
            date=today,
            status="Leave"
        )
        message = "Leave request for today approved! You are on leave today."
    else:

        if now_time.time() > cutoff and not attendance_today:

            Attendence.objects.create(
                employee=emp,
                date=today,
                status="Absent"
            )

            timeout = True
            message = "Time out! Attendance closed. You are marked Absent."

        elif request.method == "POST" and not attendance_today and now_time.time() <= cutoff:

            Attendence.objects.create(
            employee=emp,
            date=today,
            time=timezone.localtime().time(),
            status="Present"
            )

            return redirect('emp_attendence')

        elif now_time.time() > cutoff:
            timeout = True
            message = "Time out! Attendance closed."


    show_history = request.GET.get('history') == "1"

    history = []

    if show_history:

        for i in range(3):   
            day = today - timedelta(days=i)

            attendance = Attendence.objects.filter(
                employee=emp,
                date=day
            ).first()

            leave = Leave.objects.filter(
                employee=emp,
                start_date__lte=day,
                end_date__gte=day,
                status='Approved'
            ).exists()

            if leave:
                status = "Leave"

            elif attendance:
                status = attendance.status

            elif day < today:
                status = "Absent"

            else:
                status = "Pending"

            history.append({
                "date": day,
                "status": status
            })


    context = {
        'already_marked': attendance_today,
        'leave_today': leave_today,
        'timeout': timeout,
        'message': message,
        'today': today,
        'show_history': show_history,
        'data': history
    }

    return render(request, 'emp_attendence.html', context)



def apply_leave(request):

    emp = Employee.objects.get(employee=request.user)

    if request.method == "POST":

        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        reason = request.POST.get("reason")

        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

        if start_date > end_date:
            messages.error(request, "Start date cannot be greater than end date")
            return redirect("apply_leave")

        overlap = Leave.objects.filter(
            employee=emp,
            start_date__lte=end_date,
            end_date__gte=start_date
        ).exists()

        if overlap:
            messages.error(request, "You already have a leave request during this period")
            return redirect("apply_leave")

        Leave.objects.create(
            employee=emp,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status="Pending"
        )
        messages.success(request, "Leave request submitted successfully")
        return redirect("apply_leave")

    return render(request, "apply_leave.html")

def my_leave(request):
    emp=Employee.objects.get(employee=request.user)
    data=Leave.objects.filter(employee=emp)
    return render(request,'my_leave.html',{'data':data})


def edit_profile(request):

    emp = Employee.objects.get(employee=request.user)
    departments = Department.objects.all()

    if request.method == 'POST':

        name = request.POST.get('name').strip()
        email = request.POST.get('email').strip()
        address = request.POST.get('address').strip()
        phno = request.POST.get('phno').strip()
        department_id = request.POST.get('department')
        pas = request.POST.get('pass')
        con = request.POST.get('conpass')
        image = request.FILES.get('image')

        if Log.objects.exclude(id=request.user.id).filter(username=name).exists():
            messages.error(request, "Username already exists")

        elif pas and pas != con:
            messages.error(request, "Passwords do not match")

        else:

            emp.employee.username = name
            emp.employee.email = email
            emp.phno = phno
            emp.address = address

            if department_id:
                emp.department = Department.objects.get(id=department_id)

            if image:
                emp.image = image

            if pas:
                emp.employee.set_password(pas)

            emp.employee.save()
            emp.save()

            messages.success(request, "Profile updated successfully")
            return redirect('view_profile')

    context = {
        'data': emp,
        'departments': departments
    }

    return render(request, 'edit_profile.html', context)

def view_profile(request):
    x=Employee.objects.get(employee=request.user)
    return render(request,'view_profile.html',{'data':x})


def attendence_history(request):

    start_date = date(2026, 3, 10)
    today = now().date()

    employees = Employee.objects.filter(employee__is_active=True)

    data = []

    day = today

    while day >= start_date:

        for emp in employees:

            attendance = Attendence.objects.filter(
                employee=emp,
                date=day
            ).first()

            leave = Leave.objects.filter(
                employee=emp,
                start_date__lte=day,
                end_date__gte=day,
                status="Approved"
            ).exists()

            if leave:
                status = "Leave"
                time = None

            elif attendance:
                status = attendance.status
                time = attendance.time

            else:

                if day == today:
                    status = "Pending"
                else:
                    status = "Absent"

                time = None

            data.append({
                "employee": emp,
                "date": day,
                "time": time,
                "status": status
            })

        day -= timedelta(days=1)

    return render(request,'attendence_history.html',{'data':data})