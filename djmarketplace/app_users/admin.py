from django.contrib import admin
from app_users.models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('balance', 'user', 'status', 'user_id')


class BuyerStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')


admin.site.register(Profile, ProfileAdmin)
admin.site.register(BuyerStatus, BuyerStatusAdmin)
