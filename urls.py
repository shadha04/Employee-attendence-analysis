"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('reg/',views.reg,name='reg'),
    path('',views.log,name='log'),
    path('employee/',views.employee,name='employee'),
    path('admin_home/',views.admin,name='admin_home'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('department/',views.department,name='department'),
    path('dep_del/<int:id>',views.dep_del,name='dep_del'),
    path('edit_dep/<int:id>',views.edit_dep,name='edit_dep'),
    path('total_dep/',views.edit_dep,name='total_dep'),
    path('approve/',views.approve,name='approve'),
    path('view_emp/', views.view_emp, name='view_emp'),
    path('attendance/',views.attendance,name='attendance'),
    path('leave/',views.leave,name='leave'),
    path('select/<int:id>',views.select,name='select'),    
    path('edit_emp/<int:id>',views.emp_edit,name='edit_emp'),    
    path('del_emp/<int:id>',views.del_emp,name='del_emp'),  
    path('emp_attendence/',views.emp_attendence,name='emp_attendence'),
    path('apply_leave/',views.apply_leave,name='apply_leave'),
    path('my_leave/',views.my_leave,name='my_leave'),
    path('edit_profile/',views.edit_profile,name='edit_profile'),
    path('view_profile/',views.view_profile,name='view_profile'),
    path('attendence_history/',views.attendence_history,name='attendence_history'),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
