from django.contrib import admin
from .models import *


class GoodsAdmin(admin.ModelAdmin):
    list_display = ('name',)


class MarketAdmin(admin.ModelAdmin):
    list_display = ('title',)


class ItemGoodsMarketAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'goods', 'price', 'market', 'quantity')


class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user',)


class ItemCartAdmin(admin.ModelAdmin):
    list_display = ('item_goods', 'cart', 'quantity')


class PurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('goods', 'date', 'quantity')


admin.site.register(GoodsModel, GoodsAdmin)
admin.site.register(MarketModel, MarketAdmin)
admin.site.register(ItemGoodsMarketModel, ItemGoodsMarketAdmin)
admin.site.register(CartModel, CartAdmin)
admin.site.register(ItemCartModel, ItemCartAdmin)
admin.site.register(PurchaseHistory, PurchaseHistoryAdmin)


# Register your models here.
