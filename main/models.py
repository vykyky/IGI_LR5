from django.db import models
from django.urls import reverse
from users.models import Client, Doctor, DoctorCategory, DoctorSpecialization
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
  
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("main:service_list_by_category", args=[self.slug])
    
    
class Service(models.Model):
    category = models.ForeignKey(Category, related_name='services', 
                                 on_delete=models.CASCADE) # если удаляется категория, удаляются все ее продукты
    
    #PROTECT  сначала надо удалить все продукты потом уже категорию
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(upload_to='services/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) # чисел после запятой
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("main:service_detail", args=[self.id, self.slug])
    
    def get_absolute_url_for_update(self):
        return reverse('main:service_update', args=[str(self.id)])

    def get_absolute_url_for_delete(self):
        return reverse('main:service_delete', args=[str(self.id)])


class Question(models.Model):
    content = models.TextField()
    date = models.DateTimeField(null=True, blank=True)
    answer = models.ForeignKey('Answer', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.content

    def get_absolute_url_to_add(self):
        return reverse('main:add_answer', kwargs={'pk': self.pk})


class Answer(models.Model):
    content = models.TextField()
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.content


class Vacancy(models.Model):
    doctor_specialization = models.ForeignKey(DoctorSpecialization, on_delete=models.CASCADE)
    doctor_category = models.ForeignKey(DoctorCategory, on_delete=models.SET_NULL, null=True, blank=True) 
    number_of_this_position = models.IntegerField()
    vacancy_description = models.TextField()

    def get_absolute_url_for_delete(self):
        return reverse('main:delete_vacancy', kwargs={'pk': self.pk})

    def get_absolute_url_for_update(self):
        return reverse('main:update_vacancy', kwargs={'pk': self.pk})

    def __str__(self):
        return f'{self.doctor_specialization.__str__()} {self.number_of_this_position}'

    class Meta:
        verbose_name = 'Vacancy'
        verbose_name_plural = 'Vacancies'


class Review(models.Model):
    author = models.ForeignKey(Client, on_delete=models.CASCADE)
    rate = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField()
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.author.__str__()}'


class PromoCode(models.Model):
    name = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=255)
    discount_percentage = models.IntegerField(default=None)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.code


class Bonus(models.Model):
    name = models.CharField(max_length=255, null=True)
    code = models.CharField(max_length=255)
    discount_percentage = models.IntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = 'Bonus'
        verbose_name_plural = 'Bonuses'


class Company(models.Model):
    name = models.CharField(max_length=255)
    video = models.FileField(upload_to='images/', null=True, blank=True)
    logo = models.ImageField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'


class CompanyStory(models.Model):
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=255)
    content = models.TextField()
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Company story'
        verbose_name_plural = 'Company stories'


class News(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_source = models.ImageField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'



class DoctorSchedule(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='available_times')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    class Meta:
        unique_together = ('doctor', 'start_time')
        ordering = ['start_time']

    def __str__(self):
        return f"{self.doctor} — {self.start_time.strftime('%d.%m %H:%M')}"
    
class Appointment(models.Model):
    user = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    service = models.ForeignKey('main.Service', on_delete=models.CASCADE)
    scheduled_time = models.ForeignKey(DoctorSchedule, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} записан к {self.doctor} на {self.scheduled_time.start_time}"