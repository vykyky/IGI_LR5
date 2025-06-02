from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.urls import reverse

class DoctorSpecialization(models.Model):
    name = models.CharField(max_length=255)
    salary = models.IntegerField()
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Doctor Specialization"
        verbose_name_plural = "Doctor Specializations"

    def __str__(self):
        return self.name

    def get_absolute_url_for_delete(self):
        return reverse('users:delete_doctor_specialization', kwargs={'pk': self.pk})

    def get_absolute_url_for_update(self):
        return reverse('users:update_doctor_specialization', kwargs={'pk': self.pk})

class DoctorCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    salary_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0)

    class Meta:
        verbose_name = "Doctor Category"
        verbose_name_plural = "Doctor Categories"

    def __str__(self):
        return self.name
    def get_absolute_url_for_delete(self):
        return reverse('users:delete_doctor_category', kwargs={'pk': self.pk})

    def get_absolute_url_for_update(self):
        return reverse('users:update_doctor_category', kwargs={'pk': self.pk})


class Department(models.Model):
    name = models.CharField("Name", max_length=50)
    number = models.IntegerField("Number", default=None)
    floor = models.IntegerField("floor", default=None)

    def __str__(self):
        return self.name
    

class MyUser(AbstractUser):
    patronymic = models.CharField("Отчество", max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    username = models.CharField(unique=True)
    telephone = models.CharField(max_length=13, null=True, default='+375290000000')

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return ' '.join(filter(None, parts))

    def get_absolute_url_for_delete(self):
        return reverse('users:delete_user', kwargs={'pk': self.pk})
    
    def __str__(self):
        return self.username

class Client(models.Model):
    birth_date = models.DateField()
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.user.username
    

class Doctor(models.Model):
    birth_date = models.DateField()
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    category =  models.ForeignKey(DoctorCategory, on_delete=models.SET_NULL, null=True)
    specialization = models.ForeignKey(DoctorSpecialization, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, default=None)
    services = models.ManyToManyField('main.Service') 
   
    def get_absolute_url_for_update(self):
        return reverse('users:update_doctor', kwargs={'pk': self.pk})

    def __str__(self):
        return self.user.username



