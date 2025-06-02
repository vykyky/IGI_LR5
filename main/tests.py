from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from users.models import MyUser, Client, Doctor, DoctorCategory, DoctorSpecialization, Department
from .models import *
import tempfile
from PIL import Image
import datetime

def get_temporary_image():
    """Создает временное изображение для тестов"""
    image = Image.new('RGB', (100, 100))
    tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(tmp_file, 'jpeg')
    tmp_file.seek(0)
    return tmp_file

class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Терапия',
            slug='terapiya'
        )

    def test_creation(self):
        self.assertEqual(self.category.name, 'Терапия')
        self.assertEqual(self.category.slug, 'terapiya')


    def test_get_absolute_url(self):
        url = self.category.get_absolute_url()
        self.assertEqual(url, reverse('main:service_list_by_category', args=['terapiya']))

class ServiceModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Анализы', slug='analizy')
        self.service = Service.objects.create(
            category=self.category,
            name='Общий анализ крови',
            slug='obshiy-analiz-krovi',
            price=50.00
        )

    def test_creation(self):
        self.assertEqual(self.service.name, 'Общий анализ крови')
        self.assertEqual(self.service.price, 50.00)

    def test_get_absolute_urls(self):
        self.assertEqual(
            self.service.get_absolute_url(),
            reverse('main:service_detail', args=[self.service.id, 'obshiy-analiz-krovi'])
        )
        self.assertEqual(
            self.service.get_absolute_url_for_update(),
            reverse('main:service_update', args=[str(self.service.id)])
        )

class QuestionAnswerModelTest(TestCase):
    def setUp(self):
        self.answer = Answer.objects.create(
            content='Это тестовый ответ',
            date=timezone.now()
        )
        self.question = Question.objects.create(
            content='Это тестовый вопрос?',
            date=timezone.now(),
            answer=self.answer
        )

    def test_question_creation(self):
        self.assertEqual(self.question.content, 'Это тестовый вопрос?')
        self.assertEqual(self.question.answer.content, 'Это тестовый ответ')

    def test_answer_creation(self):
        self.assertEqual(self.answer.content, 'Это тестовый ответ')

    def test_question_url(self):
        url = self.question.get_absolute_url_to_add()
        self.assertEqual(url, reverse('main:add_answer', kwargs={'pk': self.question.pk}))

class VacancyModelTest(TestCase):
    def setUp(self):
        self.specialization = DoctorSpecialization.objects.create(
            name='Хирург',
            salary=100000
        )
        self.category = DoctorCategory.objects.create(
            name='Высшая',
            salary_multiplier=1.5
        )
        self.vacancy = Vacancy.objects.create(
            doctor_specialization=self.specialization,
            doctor_category=self.category,
            number_of_this_position=2,
            vacancy_description='Требуется хирург высшей категории'
        )

    def test_creation(self):
        self.assertEqual(self.vacancy.doctor_specialization.name, 'Хирург')
        self.assertEqual(self.vacancy.number_of_this_position, 2)

    def test_url_methods(self):
        self.assertEqual(
            self.vacancy.get_absolute_url_for_update(),
            reverse('main:update_vacancy', kwargs={'pk': self.vacancy.pk})
        )

class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='client1',
            email='client1@example.com'
        )
        self.client = Client.objects.create(
            user=self.user,
            birth_date='1990-01-01',
            address='ул. Тестовая, 1'
        )
        self.review = Review.objects.create(
            author=self.client,
            rate=5,
            content='Отличный сервис!',
            date=timezone.now()
        )

    def test_creation(self):
        self.assertEqual(self.review.rate, 5)
        self.assertEqual(self.review.author.user.username, 'client1')

class PromoCodeBonusModelTest(TestCase):
    def setUp(self):
        self.promo = PromoCode.objects.create(
            name='Летняя акция',
            code='SUMMER20',
            discount_percentage=20
        )
        self.bonus = Bonus.objects.create(
            name='Новогодний бонус',
            code='NEWYEAR30',
            discount_percentage=30
        )

    def test_promo_creation(self):
        self.assertEqual(self.promo.code, 'SUMMER20')
        self.assertTrue(self.promo.available)

    def test_bonus_creation(self):
        self.assertEqual(self.bonus.discount_percentage, 30)

class CompanyModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name='МедЦентр'
        )
        self.story = CompanyStory.objects.create(
            company=self.company,
            title='Основание компании',
            content='Наша компания была основана в 2000 году',
            date='2000-01-01'
        )

    def test_company_creation(self):
        self.assertEqual(self.company.name, 'МедЦентр')

    def test_story_creation(self):
        self.assertEqual(self.story.title, 'Основание компании')
        self.assertEqual(self.story.company.name, 'МедЦентр')

class NewsModelTest(TestCase):
    def setUp(self):
        self.news = News.objects.create(
            title='Новое оборудование',
            content='Мы закупили новое оборудование',
            date=timezone.now()
        )

    def test_creation(self):
        self.assertEqual(self.news.title, 'Новое оборудование')

class DoctorScheduleModelTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username='doctor1',
            email='doctor1@example.com'
        )
        self.specialization = DoctorSpecialization.objects.create(
            name='Терапевт',
            salary=50000
        )
        self.department = Department.objects.create(
            name='Терапия',
            number=101,
            floor=1
        )
        self.doctor = Doctor.objects.create(
            user=self.user,
            birth_date='1980-01-01',
            specialization=self.specialization,
            department=self.department
        )
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            start_time=timezone.make_aware(datetime.datetime(2023, 6, 1, 9, 0)),
            end_time=timezone.make_aware(datetime.datetime(2023, 6, 1, 10, 0))
        )

    def test_creation(self):
        self.assertEqual(self.schedule.doctor.user.username, 'doctor1')
        self.assertEqual(
            self.schedule.start_time,
            timezone.make_aware(datetime.datetime(2023, 6, 1, 9, 0))
        )

class AppointmentModelTest(TestCase):
    def setUp(self):
        # Создаем пользователей
        doctor_user = MyUser.objects.create_user(
            username='doctor2',
            email='doctor2@example.com'
        )
        client_user = MyUser.objects.create_user(
            username='client2',
            email='client2@example.com'
        )
        
        # Создаем связанные объекты
        self.specialization = DoctorSpecialization.objects.create(
            name='Кардиолог',
            salary=70000
        )
        self.department = Department.objects.create(
            name='Кардиология',
            number=201,
            floor=2
        )
        self.doctor = Doctor.objects.create(
            user=doctor_user,
            birth_date='1975-01-01',
            specialization=self.specialization,
            department=self.department
        )
        self.client = Client.objects.create(
            user=client_user,
            birth_date='1990-01-01',
            address='ул. Тестовая, 2'
        )
        self.category = Category.objects.create(
            name='Консультации',
            slug='konsultacii'
        )
        self.service = Service.objects.create(
            category=self.category,
            name='Консультация кардиолога',
            slug='konsultaciya-kardiologa',
            price=100.00
        )
        self.schedule = DoctorSchedule.objects.create(
            doctor=self.doctor,
            start_time=timezone.make_aware(datetime.datetime(2023, 6, 1, 10, 0)),
            end_time=timezone.make_aware(datetime.datetime(2023, 6, 1, 11, 0))
        )
        self.appointment = Appointment.objects.create(
            user=self.client,
            doctor=self.doctor,
            service=self.service,
            scheduled_time=self.schedule
        )

    def test_creation(self):
      
        self.assertEqual(self.appointment.service.price, 100.00)
