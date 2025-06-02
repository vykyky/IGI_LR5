from users.models import Client, MyUser
import logging
from datetime import date

logger = logging.getLogger(__name__)

def create_client_if_needed(strategy, details, backend, user=None, *args, **kwargs):
    """
    Создаёт объект Client для новых пользователей, вошедших через Google.
    """
    if user and not hasattr(user, 'client'):
        logger.info(f"Создаём профиль Client для нового OAuth-пользователя: {user.username}")
        client = Client.objects.create(user=user,  birth_date=date(2000, 1, 1), address='')
        logger.info(f"Профиль Client создан для: {user.username}")