from datetime import datetime
from statistics import median, mean, mode, StatisticsError
from django.db.models import Count, Sum
from collections import Counter
from django.db.models.functions import TruncMonth
from main.models import Service, Appointment, Review
from users.models import Client
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import calendar
from django.utils import timezone

def client_age_median():
    clients = Client.objects.exclude(birth_date=None)
    ages = [(datetime.now().date() - client.birth_date).days // 365 for client in clients]
    if ages:
        return round(median(ages), 3)
    else:
        return None


def client_age_mean():
    clients = Client.objects.exclude(birth_date=None)
    ages = [(datetime.now().date() - client.birth_date).days // 365 for client in clients]
    if ages:
        return  round(mean(ages), 3)
    else:
        return None

def get_clients_abc():
    return Client.objects.order_by('user__last_name')

def get_services_abc():
    services = Service.objects.filter(available=True)
    return sorted(services, key=lambda s: s.name.lower())

def total_sales_sum():
    appointments = Appointment.objects.select_related('service').all()
    total = sum(appt.service.price for appt in appointments)
    return round(total, 3)

def sales_mean():
    appointments = Appointment.objects.select_related('service').all()
    prices = [appt.service.price for appt in appointments]
    return round(mean(prices), 3) if prices else 0

def sales_median():
    appointments = Appointment.objects.select_related('service').all()
    prices = [appt.service.price for appt in appointments]
    return round(median(prices), 3) if prices else 0

def sales_mode():
    appointments = Appointment.objects.select_related('service').all()
    prices = [appt.service.price for appt in appointments]
    try:
        return round(mode(prices), 3) if prices else 0
    except StatisticsError:
        return None
    

def most_popular_service_category():
    categories = Appointment.objects.select_related('service__category').values_list('service__category__name', flat=True)
    if categories:
        most_common = Counter(categories).most_common(1)
        
        return most_common[0][0] if most_common else None
    return None

def most_profitable_service_category():
    queryset = (
        Appointment.objects
        .select_related('service__category')
        .values('service__category__name')
        .annotate(total_profit=Sum('service__price'))
        .order_by('-total_profit')
    )
    if queryset:
        return queryset[0]['service__category__name']
    return None

def most_popular_service():
    services = Appointment.objects.select_related('service').values_list('service__name', flat=True)
    if services:
        most_common = Counter(services).most_common(1)
        return most_common[0][0] if most_common else None
    return None

def service_with_max_profit():
    queryset = (
        Appointment.objects
        .values('service__name')
        .annotate(total_profit=Sum('service__price'))
        .order_by('-total_profit')
    )
    if queryset:
        return queryset[0]['service__name']
    return None


def appointments_per_month():
    data = (
        Appointment.objects
        .annotate(month=TruncMonth('scheduled_time__start_time'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    return [(item['month'].strftime('%Y-%m'), item['count']) for item in data if item['month'] is not None]

def plot_appointments_per_month():
    data = appointments_per_month()
    if not data:
        return None  

    months, counts = zip(*data)

    month_labels = []
    for ym in months:
        year, month = ym.split('-')
        month_name = calendar.month_name[int(month)] 
       
        month_labels.append(f"{month_name} {year}")

    plt.figure(figsize=(10, 5))
    plt.bar(month_labels, counts, color='skyblue')
    plt.title('Количество записей по месяцам')
    plt.xlabel('Месяц')
    plt.ylabel('Количество записей')
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic


def reviews_ratings_distribution():
    data = (
        Review.objects
        .values('rate')
        .annotate(count=Count('id'))
        .order_by('rate')
    )
    return [(item['rate'], item['count']) for item in data]

def plot_reviews():
    data = reviews_ratings_distribution()
    if not data:
        return None  
    
    rates, counts = zip(*data)

    labels = [str(rate) for rate in rates]

    plt.figure(figsize=(6,6))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title('Распределение оценок отзывов')
    plt.axis('equal')  

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')
    return graphic

def appointments_per_doctor():
    today = timezone.localdate()
    start_month = timezone.make_aware(datetime(today.year, today.month, 1))
    if today.month == 12:
        start_next_month = timezone.make_aware(datetime(today.year + 1, 1, 1))
    else:
        start_next_month = timezone.make_aware(datetime(today.year, today.month + 1, 1))
    data = (
        Appointment.objects
        .filter(scheduled_time__start_time__gte=start_month, scheduled_time__start_time__lt=start_next_month)
        .values('doctor__id', 'doctor__user__first_name', 'doctor__user__last_name')
        .annotate(count=Count('id'))
        .order_by('doctor__user__last_name')
    )
    
    return [(
        f"{item['doctor__user__last_name']} {item['doctor__user__first_name']}",
        item['count']
    ) for item in data]

def plot_appointments_per_doctor():
    data = appointments_per_doctor()
    if not data:
        return None  

    doctors, counts = zip(*data)

    plt.figure(figsize=(12, 6))
    plt.bar(doctors, counts, color='lightgreen')
    plt.title('Количество записей к врачам за текущий месяц')
    plt.xlabel('Врач')
    plt.ylabel('Количество записей')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)

    image_png = buffer.getvalue()
    graphic = base64.b64encode(image_png)
    return graphic.decode('utf-8')