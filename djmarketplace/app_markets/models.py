from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class GoodsModel(models.Model):
    """Модель товаров"""
    name = models.CharField(max_length=50, verbose_name=_('name'))

    def __str__(self):
        return self.name


class CartModel(models.Model):
    """Модель корзыны"""
    user = models.OneToOneField(User,
                                verbose_name=_('buyer'),
                                on_delete=models.DO_NOTHING,
                                related_name='cart')
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('total cost'), default=0)

    def __str__(self):
        return f'cart_of_user {self.user.username}'


class ItemCartModel(models.Model):
    """Модель товаров в корзине."""
    item_goods = models.ForeignKey('ItemGoodsMarketModel',
                                   verbose_name=_('goods_in_market'),
                                   null=True,
                                   blank=True,
                                   on_delete=models.CASCADE,
                                   related_name='goods_in_market')
    cart = models.ForeignKey(CartModel,
                             null=True,
                             blank=True,
                             on_delete=models.CASCADE,
                             verbose_name=_('cart'),
                             related_name='item_cart')
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))


class MarketModel(models.Model):
    """Модель магазинов"""
    title = models.CharField(max_length=50, verbose_name=_('title'))

    def __str__(self):
        return self.title


class ItemGoodsMarketModel(models.Model):
    """Модель товаров в магазине"""
    market = models.ForeignKey(MarketModel,
                               null=True,
                               blank=True,
                               verbose_name=_('market'),
                               on_delete=models.CASCADE,
                               related_name='item_market')
    goods = models.ForeignKey(GoodsModel,
                              null=True,
                              blank=True,
                              verbose_name=_('item goods market'),
                              on_delete=models.CASCADE,
                              related_name='item_goods')
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    code = models.CharField(max_length=10, null=True, verbose_name=_('code'))
    price = models.DecimalField(max_digits=10, default=0, decimal_places=2, verbose_name=_('price'))

    def write_off_store(self, quantity):
        """Метод возвращает объект с изменённым значением поля "количество товара в магазине",
         сохранение объекта происходит во вью с помощью bulk_update"""
        self.quantity -= quantity
        return self


class PurchaseHistory(models.Model):
    """Модель история покупок. Связана FK с позицией товара в магазине, имеет поля 'quantity', и 'date'. """
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    date = models.DateTimeField(auto_now_add=True)
    goods = models.ForeignKey(ItemGoodsMarketModel,
                              null=True,
                              blank=True,
                              verbose_name=_('goods'),
                              on_delete=models.DO_NOTHING,
                              related_name='purchase_history')