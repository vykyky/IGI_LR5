# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import ClientRegistrationForm
from .models import MyUser, Client, DoctorCategory, DoctorSpecialization
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .forms import *
from django.urls import reverse_lazy
from django.contrib.auth.hashers import make_password
from datetime import timezone, datetime, timedelta
from main.models import Appointment
from django.utils.dateparse import parse_date
from collections import defaultdict
import logging

logger = logging.getLogger('myapp')

class LoginView(View):
    template_name = 'users/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('main:home')

    def get(self, request):
        logger.debug("LoginView GET called")

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        logger.debug("LoginView POST called with data: %s", request.POST)

        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request, username=data['username'], password=data['password'])
            if user:
                login(request, user)
                logger.info(f"User '{data['username']}' logged in successfully")

                return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    success_url = reverse_lazy('users:login')

    def get(self, request):
        logger.info(f"User logged out")
        logout(request)
        return redirect(self.success_url)

class ClientRegistrationView(View):
    template_name = 'users/register.html'
    form_class = ClientRegistrationForm
    success_url = reverse_lazy('users:login')

    def get(self, request):
        logger.debug("ClientRegistrationView GET called")
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        logger.debug("ClientRegistrationView POST called with data: %s", request.POST)
        form = self.form_class(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            birth_date = data['birth_date']
                       
            user = MyUser.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                patronymic=data.get('patronymic', ''),
                email=data['email'],
                telephone=data['telephone'],
                username=data['username'],
                password=make_password(data['password1']),
            )
            logger.info(f"New client user created: {user.username}")

            client = form.save(commit=False)
            client.user = user
            client.birth_date = birth_date
            client.save()

            logger.info(f"Client profile saved for user: {user.username}")
            return redirect('users:login')
        return render(request, self.template_name, {'form': form})

class DoctorRegistrationView(View):
    template_name = 'users/register.html'
    form_class = DoctorRegistrationForm
    success_url = reverse_lazy('users:doctors')

    def get(self, request):
        logger.debug("DoctorRegistrationView GET called")
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        logger.debug("DoctorRegistrationView POST called with data: %s", request.POST)

        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            birth_date = data['birth_date']
            
            user = MyUser.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                patronymic=data.get('patronymic', ''),
                email=data['email'],
                telephone=data['telephone'],
                username=data['username'],
                password=make_password(data['password1']),
                is_staff=True,
            )

            doctor = form.save(commit=False)
            doctor.user = user
            doctor.birth_date = birth_date
            doctor.image = data.get('image')  
            doctor.save()

            logger.info(f"Doctor profile saved for user: {user.username}")
            if 'services' in form.cleaned_data:
                doctor.services.set(form.cleaned_data['services'])
                logger.debug(f"Doctor services set for user: {user.username}")

            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


def delete_user(request, pk):
    user = MyUser.objects.get(pk=pk)

    user.delete()
    logger.info(f"User '{user.username}' with id={pk} deleted")
    return redirect('main:home')

class DoctorsView(View):
    template_name = "users/doctors.html"

    def get(self, request):
        logger.debug("DoctorsView GET called")

        doctors = Doctor.objects.all()
        selected_doctor_id = request.GET.get('doctor_id')
        date_str = request.GET.get('date')
        selected_doctor = None
        appointments = []

        if selected_doctor_id:
            selected_doctor = Doctor.objects.get(id=selected_doctor_id)
            appointments = Appointment.objects.filter(doctor=selected_doctor).select_related('user', 'service', 'scheduled_time')

            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                    appointments = appointments.filter(scheduled_time__start_time__date=date_obj)
                except ValueError:
                    logger.warning(f"Invalid date format received in DoctorsView: {date_str}")
                    pass  

        context = {
            'doctors': doctors,
            'selected_doctor': selected_doctor,
            'appointments': appointments,
            'selected_date': date_str,
        }
        return render(request, self.template_name, context)


class ClientsView(View):
    def get(self, request):
        logger.debug("ClientsView GET called")
        clients = Client.objects.select_related('user')
        client_id = request.GET.get('client_id')
        date_start_str = request.GET.get('date_start')
        date_end_str = request.GET.get('date_end')

        selected_client = None
        selected_start = None
        selected_end = None
        appointments = []
        grouped_appointments = {}  
        total_sum = 0 

        if client_id:
            try:
                selected_client = clients.get(id=client_id)
                appointments = Appointment.objects.filter(user=selected_client)\
                    .select_related('doctor__user', 'service', 'scheduled_time')\
                    .order_by('scheduled_time__start_time')

                selected_start = parse_date(date_start_str) if date_start_str else None
                selected_end = parse_date(date_end_str) if date_end_str else None

                filtered = appointments
                if selected_start:
                    filtered = filtered.filter(scheduled_time__start_time__date__gte=selected_start)
                if selected_end:
                    filtered = filtered.filter(scheduled_time__start_time__date__lte=selected_end)

                grouped_appointments = defaultdict(lambda: {'appointments': [], 'total_price': 0})
                for appt in filtered:
                    doctor_name = appt.doctor.user.full_name
                    grouped_appointments[doctor_name]['appointments'].append(appt)
                    grouped_appointments[doctor_name]['total_price'] += appt.service.price

                total_sum = sum(group['total_price'] for group in grouped_appointments.values())
                logger.info(f"Appointments retrieved for client id={client_id} with total sum {total_sum}")
                
            except Client.DoesNotExist:
                logger.warning(f"Client with id={client_id} does not exist")
                selected_client = None

        return render(request, 'users/clients.html', {
            'clients': clients,
            'selected_client': selected_client,
            'appointments': appointments,
            'grouped_appointments': dict(grouped_appointments),
            'selected_start': selected_start,
            'selected_end': selected_end,
            'total_sum': total_sum,
        })

class DoctorAttributesView(View):
    template_name = "users/doctor_attributes.html"

    def get(self, request):
        logger.debug("DoctorAttributesView GET called")
        context = {
            'doctor_specializations': DoctorSpecialization.objects.all(),
            'doctor_categories': DoctorCategory.objects.all(),
            }
        return render(request, self.template_name, context)


class AddDoctorSpecializationView(View):
    template_name = "main/additional/add_something.html"
    form_class = DoctorSpecializationForm
    success_url = reverse_lazy('users:doctor_attributes')

    def get(self, request):
        logger.info(f"User {request.user} accessed AddDoctorSpecializationView GET")

        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            logger.info(f"User {request.user} created DoctorSpecialization ")
            return redirect(self.success_url)

        return render(request, self.template_name, {'form': form})


def update_doctor_specialization(request, pk):
    doctor_specialization = DoctorSpecialization.objects.get(pk=pk)

    if request.method == "GET":
        logger.info(f"User {request.user} accessed update_doctor_specialization GET pk={pk}")
        form = DoctorSpecializationForm(initial={
            'name': doctor_specialization.name,
            'salary': doctor_specialization.salary,
            'description': doctor_specialization.description,
        })

        context = {'form': form}
        return render(request, "main/additional/add_something.html", context)

    else:
        form = DoctorSpecializationForm(request.POST)

        if form.is_valid():
            doctor_specialization.name = form.cleaned_data['name']
            doctor_specialization.salary = form.cleaned_data['salary']
            doctor_specialization.description = form.cleaned_data['description']
            doctor_specialization.save()
            logger.info(f"User {request.user} updated DoctorSpecialization id={pk}")

            return redirect('users:doctor_attributes')


        return render(request, "main/additional/add_something.html", {'form': form})


def delete_doctor_specialization(request, pk):
    doctor_specialization = DoctorSpecialization.objects.get(pk=pk)
    doctor_specialization.delete()
    logger.info(f"User {request.user} deleted DoctorSpecialization pk={pk}")
    return redirect('users:doctor_attributes')


class AddDoctorCategoryView(View):
    template_name = "main/additional/add_something.html"
    form_class = DoctorCategoryForm
    success_url = reverse_lazy('users:doctor_attributes')

    def get(self, request):
        logger.info(f"User {request.user} accessed AddDoctorCategoryView GET")
        context = {'form': self.form_class}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()
            logger.info(f"User {request.user} created DoctorCategory ")
            return redirect(self.success_url)


        return render(request, self.template_name, {'form': form})


def update_doctor_category(request, pk):
    doctor_category = DoctorCategory.objects.get(pk=pk)

    if request.method == "GET":
        logger.info(f"User {request.user} accessed update_doctor_category GET id={pk}")

        form = DoctorCategoryForm(initial={
            'name': doctor_category.name,
            'salary_multiplier': doctor_category.salary_multiplier,
        })

        context = {'form': form}
        return render(request, "main/additional/add_something.html", context)

    else:
        form = DoctorCategoryForm(request.POST, instance=doctor_category)

        if form.is_valid():
            doctor_category.name = form.cleaned_data['name']
            doctor_category.salary_multiplier = form.cleaned_data['salary_multiplier']
            doctor_category.save()
            logger.info(f"User {request.user} updated DoctorCategory id={pk}")
            return redirect('users:doctor_attributes')


        return render(request, "main/additional/add_something.html", {'form': form})

def delete_doctor_category(request, pk):
    doctor_category = DoctorCategory.objects.get(pk=pk)
    doctor_category.delete()
    logger.info(f"User {request.user} deleted DoctorCategory id={pk}")
    return redirect('users:doctor_attributes')

def update_doctor(request, pk):
    doctor = Doctor.objects.get(pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
        if form.is_valid():
            logger.info(f"User {request.user} updated Doctor id={pk}")
            form.save()
            return redirect('users:doctors')  
    else:
        logger.info(f"User {request.user} accessed update_doctor GET id={pk}")
        form = DoctorForm(instance=doctor)
    return render(request, 'main/additional/add_something.html', {'form': form})