from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from accounts.forms import UserRegisterForm


User = get_user_model()


class LoginViewTests(TestCase):
    def setUp(self):
        """Создаем тестового пользователя"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

    def test_login_get(self):
        """
        Тестируем GET-запрос
        """
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')

    def test_login_post_success(self):
        """
        Тестируем успешный вход
        """
        response = self.client.post(reverse('accounts:login'), {
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('accounts:account', kwargs={'pk': self.user.pk}))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_post_invalid_credentials(self):
        """
        Тестируем неверные учетные данные
        """
        response = self.client.post(reverse('accounts:login'), {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, "Не получилось войти, проверьте логин или пароль")

    def test_login_post_missing_email(self):
        """
        Тестируем отсутствие email
        """
        response = self.client.post(reverse('accounts:login'), {
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, "Необходимо ввести электронную почту")

    def test_login_post_missing_password(self):
        """
        Тестируем отсутствие пароля
        """
        response = self.client.post(reverse('accounts:login'), {
            'email': 'test@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
        self.assertContains(response, "Необходимо ввести пароль")


class CustomRegistrationViewTests(TestCase):
    def setUp(self):
        self.url = reverse('accounts:registration')  # Замените на ваш URL для регистрации
        self.valid_data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'testuser@example.com'
        }
        self.invalid_data = {
            'username': '',
            'password': 'password123',
            'email': 'testuser@example.com'
        }
        self.existing_user = User.objects.create_user(
            username='existinguser',
            password='password123',
            email='testuser@example.com'
        )

    def test_registration_form_display(self):
        """
        Тестируем GET-запрос
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registration_form.html')
        self.assertIsInstance(response.context['form'], UserRegisterForm)

    def test_registration_email_already_exists(self):
        """
        Тестируем попытку регистрации с существующим email
        """
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'Этот e-mail уже используется.')

    def test_registration_success(self):
        """
        Тестируем POST-запрос
        """
        self.existing_user.delete()
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('accounts:login'))
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_registration_invalid_data(self):
        """
        Ошибка для пустого поля username
        """
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertEqual(response.status_code, 200)  # Форма должна быть повторно отрендерена
        self.assertFormError(response, 'form', 'username', 'Обязательное поле.')


class PersonalAccountViewTests(TestCase):

    def setUp(self):
        # Создание тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )

    def test_access_for_authenticated_user(self):
        """
         Проверка, что аутентифицированный пользователь может смотреть страницу и она работает
        """
        self.client.login(email='testuser@example.com', password='testpassword')
        response = self.client.get(reverse('accounts:account', args=[self.user.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.user)
        self.assertTemplateUsed(response, 'accounts/account.html')

    def test_redirect_for_anonymous_user(self):
        """
        Проверка, что неаутентифицированный пользователь перенаправляется на страницу входа
        """
        response = self.client.get(reverse('accounts:account', args=[self.user.pk]))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("accounts:account", args=[self.user.pk])}')
