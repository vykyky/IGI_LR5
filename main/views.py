from django.shortcuts import render, get_object_or_404
from .models import *
from django.utils import timezone
from datetime import datetime

from cart.forms import CartAddServiceForm
from main import functions, apis
from users.models import Doctor, Client, Department
from .forms import *
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
import tzlocal
import pytz
import calendar

import logging

logger = logging.getLogger('myapp')

# Create your views here.
# представления могут быть классовыми а могут функциональными. это второе
def service_list(request, category_slug=None):
    logger.info(f"service_list called with category_slug={category_slug}, sort={request.GET.get('sort')}")

    categories = Category.objects.all()
    services = Service.objects.filter(available=True)

    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        services = services.filter(category=category)

    sort = request.GET.get('sort')
    if sort in ['name', '-name', 'price', '-price']:
        services = services.order_by(sort)

    # то к чему мы будем обращаться в шаблоне
    return render(request, 'main/service/list.html',
                  {'category': category,
                   'categories': categories,
                   'services': services,
                   'sort': sort, })

def add_category(request):
    logger.info(f"add_category called with method={request.method}")
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            return redirect('main:service_list')
    else:
        form = CategoryForm()
    return render(request, 'main/additional/add_something.html', {
        'form': form,
    })

def add_service(request, category_slug):
    if category_slug != 'all':
        category = get_object_or_404(Category, slug=category_slug)
    else:
        category = None

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            if category:
                service.category = category
            service.save()
            return redirect(service.get_absolute_url())
    else:
        form = ServiceForm()
        if category:
            form.fields['category'].initial = category

    return render(request, 'main/additional/add_something.html', {
        'form': form,
    })

def service_detail(request, id, slug):
    service = get_object_or_404(Service, id=id, slug=slug)

    doctors = Doctor.objects.filter(services=service)
    selected_doctor = None
    available_times = []

    doctor_id = request.GET.get("doctor_id")  
    if doctor_id:
        try:
            selected_doctor = Doctor.objects.get(id=doctor_id)
            available_times = DoctorSchedule.objects.filter(
                doctor=selected_doctor,
                start_time__gt=timezone.now()
            ).exclude(
                id__in=Appointment.objects.values_list('scheduled_time_id', flat=True)
            )
        except Doctor.DoesNotExist:
            pass

    return render(request, "main/service/detail.html", {
        "service": service,
        "doctors": doctors,
        "selected_doctor": selected_doctor,
        "available_times": available_times,
        "related_services": Service.objects.filter(
            category=service.category,
            available=True
        ).exclude(id=service.id)[:4],
        "cart_service_form": CartAddServiceForm(service=service),
    })


def update_service(request, pk):
    logger.info(f"update_service called with pk={pk}, method={request.method}")
    service = get_object_or_404(Service, pk=pk)

    if request.method == "GET":
        form = ServiceForm(initial={
            'name': service.name,
            'price': service.price,
            'description': service.description,
            'image': service.image,
            'category': service.category,
        })
        logger.info(f"Rendered update form for Service id={pk}")
        return render(request, "main/additional/add_something.html", {'form': form})

    else:
        form = ServiceForm(request.POST, request.FILES)

        if form.is_valid():
            service.name = form.cleaned_data['name']
            service.price = form.cleaned_data['price']
            service.description = form.cleaned_data['description']
            if request.FILES.get('image'):
                service.image = request.FILES['image']
            service.category = form.cleaned_data['category']
            
            service.save()
            logger.info(f"Service id={pk} updated successfully")
            return redirect(service.get_absolute_url())

        return render(request, "main/additional/add_something.html", {'form': form})


def delete_service(request, pk):
    logger.info(f"delete_service called with pk={pk}")
    service = get_object_or_404(Service, pk=pk)
    service.delete()
    logger.info(f"Service id={pk} deleted successfully")
    return redirect('main:service_list')

def main_info(request):
   
    latest_news = News.objects.order_by('-date').first()
    logger.debug(f"Retrieved latest news: {latest_news}")
    context = {
        "latest_news": latest_news,
        
    }
    return render(request, 'main/additional/main_info.html', context)


def about_company(request):  
   
    company = Company.objects.first()
    logger.info(functions.most_popular_service_category())
    most_popular_service_category = functions.most_popular_service_category()
    most_profitable_service_category = functions.most_profitable_service_category()
    most_popular_service = functions.most_popular_service()
    service_with_max_profit = functions.service_with_max_profit()

    appointments_per_month_plot = functions.plot_appointments_per_month()
    reviews_plot = functions. plot_reviews()
    appointments_per_doctor_plot = functions.plot_appointments_per_doctor()
    context = {
        'company': company,
        'stories': company.stories.all() if company else [],
        'client_age_median': functions.client_age_median(),
        'client_age_mean': functions.client_age_mean(),
        'clients_sorted': functions.get_clients_abc(),  
        'services_sorted': functions.get_services_abc(), 

        'total_sales_sum': functions.total_sales_sum(),
        'sales_mean': functions.sales_mean(),
        'sales_median': functions.sales_median(),
        'sales_mode': functions.sales_mode(),

        'most_popular_service_category': most_popular_service_category,
        'most_profitable_service_category': most_profitable_service_category,
        'most_popular_service': most_popular_service,
        'service_with_max_profit': service_with_max_profit,

        'appointments_per_month_plot':  appointments_per_month_plot ,
        'reviews_plot':  reviews_plot, 
        'appointments_per_doctor_plot': appointments_per_doctor_plot,
    }

    return render(request, 'main/additional/about_company.html', context)


def news_page(request):
    news = News.objects.order_by('-date')
    logger.debug(f"Retrieved {news.count()} news items")

    context = {"news": news}

    return render(request, "main/additional/news.html", context)


def dictionary_page(request):
    questions = Question.objects.all().order_by('-date')
    logger.debug(f"Retrieved {questions.count()} questions")

    context = {"questions": questions}

    return render(request, "main/additional/dictionary.html", context)


def contacts_page(request):
    search_field = request.GET.get('search_field')
    search_value = request.GET.get('search_value')

    logger.info(f"Contacts page search - field: {search_field}, value: {search_value}")

    departments = Department.objects.all().order_by('name')
    department_data = []

    for department in departments:
        doctors = Doctor.objects.filter(department=department).select_related('user', 'specialization', 'category')

        if search_field and search_value:
            if search_field == 'last_name':
                doctors = doctors.filter(user__last_name__icontains=search_value)
            elif search_field == 'first_name':
                doctors = doctors.filter(user__first_name__icontains=search_value)
            elif search_field == 'category':
                doctors = doctors.filter(category__name__icontains=search_value)
            elif search_field == 'specialization':
                doctors = doctors.filter(specialization__name__icontains=search_value)

        if doctors.exists():
            department_data.append({
                'department': department,
                'doctors': doctors
            })

    context = {
        'department_data': department_data,
    }
    return render(request, 'main/additional/contacts.html', context)

def privacy_policy_page(request):
    cat_fact = apis.get_cat_fact()
    random_image_url = apis.get_random_dog_image()
    logger.info(f"Retrieved cat fact and dog image for privacy policy page")
    context = {
        "random_image_url": random_image_url,
        "cat_fact": cat_fact,
    }

    return render(request, "main/additional/policy.html", context)


def vacancies_page(request):
    vacancies = Vacancy.objects.all()
    logger.info(f"Retrieved {vacancies.count()} vacancies")
    context = {"vacancies": vacancies}

    return render(request, "main/additional/vacancies.html", context)


def update_vacancy(request, pk):

    vacancy = Vacancy.objects.get(pk=pk)
    logger.info(f"Updating vacancy ID: {pk}")

    if request.method == "GET":
        form = VacancyForm(initial={
            'doctor_specialization': vacancy.doctor_specialization,
            'doctor_category': vacancy.doctor_category,
            'number_of_this_position': vacancy.number_of_this_position,
            'vacancy_description': vacancy.vacancy_description,
        })

        context = {'form': form}
        return render(request, "main/additional/add_something.html", context)

    else:
        form = VacancyForm(request.POST)

        if form.is_valid():
            vacancy.doctor_specialization = form.cleaned_data['doctor_specialization']
            vacancy.doctor_category = form.cleaned_data['doctor_category']
            vacancy.number_of_this_position = form.cleaned_data['number_of_this_position']
            vacancy.vacancy_description = form.cleaned_data['vacancy_description']
            vacancy.save()
            logger.info(f"Successfully updated vacancy ID: {pk}")

            return redirect('main:vacancies')
        
        logger.warning(f"Invalid form data for vacancy ID: {pk}")
        return render(request, "main/additional/add_something.html", {'form': form})


def delete_vacancy(request, pk):
    vacancy = Vacancy.objects.get(pk=pk)
    vacancy.delete()
    logger.info(f"Deleted vacancy ID: {pk}")
    return redirect('main:vacancies')


class AddVacancyView(View):
    template_name = "main/additional/add_something.html"
    form_class = VacancyForm
    success_url = reverse_lazy('main:vacancies')

    def get(self, request):
        context = {'form': self.form_class}
        logger.debug("AddVacancyView GET request")
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        logger.debug(f"AddVacancyView POST data: {form.data}")

        if form.is_valid():
            form.save()
            logger.info("Successfully added new vacancy")
            return redirect(self.success_url)

        logger.warning(f"Invalid form data: {form.errors}")

        return render(request, self.template_name, {'form': form})

def discounts_page(request):

    all_bonuses = Bonus.objects.all()
    active_bonuses = all_bonuses.filter(available=True)
    archived_bonuses = all_bonuses.filter(available=False)

    all_promo_codes = PromoCode.objects.all()
    active_promo_codes = all_promo_codes.filter(available=True)
    archived_promo_codes = all_promo_codes.filter(available=False)

    logger.info(f"Retrieved {active_bonuses.count()} active bonuses, {archived_bonuses.count()} archived bonuses, "
                   f"{active_promo_codes.count()} active promo codes, {archived_promo_codes.count()} archived promo codes")
    
    return render(request, 'main/additional/discounts.html', {
        'active_bonuses': active_bonuses,
        'archived_bonuses': archived_bonuses,
        'active_promo_codes': active_promo_codes,
        'archived_promo_codes': archived_promo_codes,
    })
   


class ReviewsView(View):
    template_name = "main/additional/rewies.html"
    form_class = ReviewForm

    def get(self, request):
        context = {'reviews': Review.objects.all().order_by('-date')}

        if request.user.is_authenticated:
            context['form'] = self.form_class

        return render(request, self.template_name, context)

    def post(self, request):
        if not request.user.is_authenticated:
            logger.warning("Unauthorized attempt to post review")
            return redirect('users:login')
        form = self.form_class(request.POST)
        logger.debug(f"Review form data: {form.data}")

        if form.is_valid():
            review = form.save(commit=False)
            review.author = Client.objects.get(user=request.user)
            review.date = datetime.now()
            review.save()
            logger.info(f"New review added by user {request.user.id}")

        context = {'reviews': Review.objects.all().order_by('-date'), 'form': self.form_class}
        return render(request, self.template_name, context)


class AddQuestionView(View):
    template_name = "main/additional/add_something.html"
    success_url = reverse_lazy('main:dictionary')
    form_class = QuestionForm

    def get(self, request):
        context = {'form': self.form_class}
        logger.debug("AddQuestionView GET request")
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        logger.debug(f"Question form data: {form.data}")

        if form.is_valid():
            question = form.save(commit=False)
            question.date = datetime.now()
            question.save()
            logger.info(f"New question added by user {request.user.id if request.user.is_authenticated else 'anonymous'}")

            return redirect(self.success_url)

        logger.warning(f"Invalid question form data: {form.errors}")
        return render(request, self.template_name, {'form': form})


class AddAnswerView(View):
    template_name = "main/additional/add_something.html"
    success_url = reverse_lazy('main:dictionary')
    form_class = AnswerForm

    def get(self, request, pk):
        context = {'form': self.form_class}
        logger.debug(f"AddAnswerView GET request for question ID: {pk}")
        return render(request, self.template_name, context)

    def post(self, request, pk):
        form = self.form_class(request.POST)
        logger.debug(f"Answer form data for question ID {pk}: {form.data}")
        if form.is_valid():
            answer = form.save(commit=False)
            answer.date = datetime.now()
            answer.save()
            question = Question.objects.get(pk=pk)
            question.answer = answer
            question.save()
            logger.info(f"Answer added for question ID: {pk}")

            return redirect(self.success_url)

        logger.warning(f"Invalid answer form data for question ID {pk}: {form.errors}")
        return render(request, self.template_name, {'form': form})



class ProfileClientView(View):
    template_name = 'main/core/profile.html'
    context = 0

    def get(self, request):
        current_user = Client.objects.get(user=request.user)
        logger.info(f"Client profile accessed for user ID: {request.user.id}")

        tz = tzlocal.get_localzone()
        local_time = datetime.now(tz)
        utc_time = datetime.now(tz=pytz.timezone('UTC'))
        text_cal = calendar.month(local_time.year, local_time.month)

        appointments = Appointment.objects.filter(user=current_user).select_related(
            'doctor', 'service', 'scheduled_time'
        ).order_by('scheduled_time__start_time')

        self.context = {
            'current_user': current_user,
            'user_timezone': tz,
            'current_date_formatted': local_time.strftime("%d/%m/%Y %H:%M:%S"),
            'calendar_text': text_cal,
            'utc_time': utc_time.strftime("%d/%m/%Y, %H:%M:%S"),
            'appointments': appointments,
        }

        return render(request, self.template_name, self.context)


class ProfileDoctorView(View):
    template_name = 'main/core/profile.html'

    def get(self, request):
        current_user = Doctor.objects.get(user=request.user)
        services = current_user.services.all()
        logger.info(f"Doctor profile accessed for user ID: {request.user.id}")
        
        tz = tzlocal.get_localzone()
        local_time = datetime.now(tz)
        utc_time = datetime.now(tz=pytz.timezone('UTC'))
        text_cal = calendar.month(local_time.year, local_time.month)

        schedule = DoctorSchedule.objects.filter(doctor=current_user)
        appointments = Appointment.objects.filter(doctor=current_user).select_related(
            'user__user', 'service', 'scheduled_time'
        )
        total_income = sum([appointment.service.price for appointment in appointments])

        context = {
            'current_user': current_user,
            'user_timezone': tz,
            'current_date_formatted': local_time.strftime("%d/%m/%Y %H:%M:%S"),
            'calendar_text': text_cal,
            'utc_time': utc_time.strftime("%d/%m/%Y, %H:%M:%S"),
            'service_for_doctor': services,
            'schedule': schedule,
            'appointments': appointments,
            'total_income': total_income,
        }
        return render(request, self.template_name, context)

