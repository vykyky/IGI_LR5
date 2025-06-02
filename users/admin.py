from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *


admin.site.register(MyUser)
admin.site.register(DoctorSpecialization)
admin.site.register(DoctorCategory)
admin.site.register(Doctor)
admin.site.register(Client)
admin.site.register(Department)

