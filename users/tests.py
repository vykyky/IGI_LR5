from django.test import TestCase
from django.urls import reverse
from .models import *
from django.utils import timezone
# Create your tests here.

class DoctorSpecializationModelTest(TestCase):
    def setUp(self):
        self.spec = DoctorSpecialization.objects.create(
            name="Cardiology",
            salary=5000,
            description="Heart specialist"
        )

    def test_creation(self):
        self.assertEqual(self.spec.name, "Cardiology")
        self.assertEqual(self.spec.salary, 5000)
        self.assertEqual(self.spec.description, "Heart specialist")

    def test_str_representation(self):
        self.assertEqual(str(self.spec), "Cardiology")

    def test_get_absolute_urls(self):
        self.assertEqual(
            self.spec.get_absolute_url_for_delete(),
            reverse('users:delete_doctor_specialization', kwargs={'pk': self.spec.pk})
        )
        self.assertEqual(
            self.spec.get_absolute_url_for_update(),
            reverse('users:update_doctor_specialization', kwargs={'pk': self.spec.pk})
        )

class DoctorCategoryModelTest(TestCase):
    def setUp(self):
        self.category = DoctorCategory.objects.create(
            name="Senior",
            salary_multiplier=1.5
        )

    def test_creation(self):
        self.assertEqual(self.category.name, "Senior")
        self.assertEqual(float(self.category.salary_multiplier), 1.5)

    def test_unique_name(self):
        with self.assertRaises(Exception):
            DoctorCategory.objects.create(name="Senior", salary_multiplier=1.2)

    def test_url_methods(self):
        self.assertEqual(
            self.category.get_absolute_url_for_delete(),
            reverse('users:delete_doctor_category', kwargs={'pk': self.category.pk})
        )

class DepartmentModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(
            name="Surgery",
            number=101,
            floor=1  
        )

    def test_creation(self):
        self.assertEqual(self.dept.name, "Surgery")
        self.assertEqual(self.dept.number, 101)
        self.assertEqual(self.dept.floor, 1)

    def test_str_representation(self):
        self.assertEqual(str(self.dept), "Surgery")

class MyUserModelTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username="doctor1",
            email="doctor1@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
            patronymic="Smith",
            telephone="+375291234567"
        )

    def test_creation(self):
        self.assertEqual(self.user.username, "doctor1")
        self.assertEqual(self.user.email, "doctor1@example.com")
        self.assertEqual(self.user.telephone, "+375291234567")

    def test_full_name_property(self):
        self.assertEqual(self.user.full_name, "Doe John Smith")

    def test_delete_url(self):
        self.assertEqual(
            self.user.get_absolute_url_for_delete(),
            reverse('users:delete_user', kwargs={'pk': self.user.pk})
        )

class ClientModelTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username="client1",
            email="client1@example.com"
        )
        self.client = Client.objects.create(
            user=self.user,
            birth_date=timezone.now().date(),
            address="123 Main St"
        )

    def test_creation(self):
        self.assertEqual(self.client.user.username, "client1")
        self.assertEqual(self.client.address, "123 Main St")

    def test_one_to_one_relation(self):
        with self.assertRaises(Exception):
            Client.objects.create(
                user=self.user,
                birth_date=timezone.now().date()
            )


class DoctorModelTest(TestCase):
    def setUp(self):
        self.user = MyUser.objects.create_user(
            username="doctor2",
            email="doctor2@example.com"
        )
        self.category = DoctorCategory.objects.create(name="Junior")
        self.specialization = DoctorSpecialization.objects.create(
            name="Neurology",
            salary=4000
        )
        self.department = Department.objects.create(
            name="Neurology Dept", 
            number=201,
            floor=2  # Добавляем обязательное поле
        )
        
        self.doctor = Doctor.objects.create(
            user=self.user,
            birth_date=timezone.now().date(),
            category=self.category,
            specialization=self.specialization,
            department=self.department
        )

    def test_creation(self):
        self.assertEqual(self.doctor.user.username, "doctor2")
        self.assertEqual(self.doctor.category.name, "Junior")
        self.assertEqual(self.doctor.specialization.name, "Neurology")
        self.assertEqual(self.doctor.department.floor, 2)  # Проверяем этаж

    def test_update_url(self):
        self.assertEqual(
            self.doctor.get_absolute_url_for_update(),
            reverse('users:update_doctor', kwargs={'pk': self.doctor.pk})
        )

    def test_department_relation(self):
        self.assertEqual(self.doctor.department.name, "Neurology Dept")


class ModelRelationsTest(TestCase):
    def test_doctor_client_relations(self):
        # Создаем пользователей
        doctor_user = MyUser.objects.create_user(
            username="dr_smith", 
            email="dr@example.com"
        )
        client_user = MyUser.objects.create_user(
            username="patient1", 
            email="patient@example.com"
        )
        
        # Создаем связанные объекты
        department = Department.objects.create(
            name="Cardiology", 
            number=301,
            floor=3  # Добавляем обязательное поле
        )
        category = DoctorCategory.objects.create(name="Middle")
        specialization = DoctorSpecialization.objects.create(
            name="Cardiologist", 
            salary=6000
        )
        
        doctor = Doctor.objects.create(
            user=doctor_user,
            birth_date="1980-01-01",
            category=category,
            specialization=specialization,
            department=department
        )
        
        client = Client.objects.create(
            user=client_user,
            birth_date="1990-05-15",
            address="456 Oak St"
        )
        
        self.assertEqual(doctor.user.email, "dr@example.com")
        self.assertEqual(client.user.username, "patient1")
        self.assertEqual(doctor.department.number, 301)
        self.assertEqual(doctor.department.floor, 3) 