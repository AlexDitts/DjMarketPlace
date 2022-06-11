from django.urls import path
from app_markets.views import *
from django.utils.translation import gettext_lazy as _

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('goods_list', GoodsListView.as_view(extra_context={'title': _('Goods list'),
                                                            'head': _('Goods list')}), name='goods_list'),
    path('goods_detail/<int:pk>', GoodsDetailView.as_view(), name='goods_detail'),
    path('cart/', ItemsCartListView.as_view(extra_context={'title': _('cart'),
                                                           'head': _('Market cart')}
                                            ), name='cart'),
    path('report_list/', ReportListView.as_view(), name='report_list')
]
