from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)


class BuyerStatus(models.Model):
    """Модель статуса покупателя. Зависит от общей суммы покупок пользователя. Сумма покупок - поле total_expenses во вторичной
    модели Profile"""
    status = models.CharField(max_length=20, verbose_name=_('buyer status'))

    def __str__(self):
        return self.status


class Profile(models.Model):
    """Модель, для дополнительных полей юзера."""
    balance = models.DecimalField(default=0,
                                  max_digits=10,
                                  decimal_places=2,
                                  verbose_name=_('balance'),
                                  validators=[MinValueValidator(0.0, message=_("balance can't be less than 0"))])

    user = models.OneToOneField(User,
                                blank=True,
                                null=True,
                                verbose_name=_('user'),
                                on_delete=models.CASCADE,
                                related_name='profile')

    status = models.ForeignKey(BuyerStatus,
                               null=True,
                               verbose_name=_('status'),
                               on_delete=models.DO_NOTHING,
                               related_name='profile')
    total_expenses = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('total expenses'), default=0)

    def check_status(self):
        """Метод проверяет значение общих трат пользователя и если они превысили очередную границу, то присваивает
        пользователю следующий статус"""
        total_expenses = self.total_expenses
        if 0 <= inttotal_expenses <= 10000:
            status_id = 1
        elif 10000 < total_expenses <= 50000:
            status_id = 2
        elif 50000 < total_expenses <= 200000:
            status_id = 3
        else:
            status_id = 4
        if self.status_id != status_id:
            self.status_id = status_id
            logger.info(f'Produced user status promotion to {self.status}')
            self.save(update_fields=['status_id'])
        return None
#
    def change_balance(self, value):
        """Метод обновляет значение поля balance. Используется при пополнении кошелька (value будет положительное)
         или при покупках (уменьшение value будет отрицательное)"""
        self.balance += value
        self.save(update_fields=['balance'])
        return None

    def change_total_expenses(self, expenses):
        """Метод обновляет значение поля total_expenses. """
        self.total_expenses += expenses
        self.save(update_fields=['total_expenses'])
        return None
