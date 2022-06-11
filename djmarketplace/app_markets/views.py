import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView
from .models import *
from .forms import *
from django.db import transaction
from django.db.models import Sum, Q
from django.contrib.auth.mixins import LoginRequiredMixin
import logging

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    """Класс вью - главная страница"""
    template_name = 'app_markets/index.html'


class GoodsListView(ListView):
    """Класс вью для отображения списка товаров и магазинов в которых они продаются"""
    queryset = ItemGoodsMarketModel.objects.select_related('goods').select_related('market').defer('quantity',
                                                                                                   'code').all()
    template_name = 'app_markets/goods_list.html'


class GoodsDetailView(DetailView):
    """Класс вью для отображения подробного описания товара."""
    template_name = 'app_markets/goods_detail.html'

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return ItemGoodsMarketModel.objects.select_related('market').select_related('goods').get(pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({'form': QuantityForm()})
        return context

    # @login_required(login_url='users/login')
    def post(self, request, pk):
        if not self.request.user.id:
            print(self.request.user.id)
            return redirect(reverse_lazy('login'))
        form = QuantityForm(request.POST)
        user = self.request.user
        goods_in_market = self.get_object()
        check_cart = CartModel.objects.get_or_create(user=user)
        cart = check_cart[0]
        has_cart = check_cart[1]
        balance = user.profile.balance
        quantity_in_market = goods_in_market.quantity
        if form.is_valid():
            quantity = form.cleaned_data.get('quantity')
            if quantity_in_market < quantity:
                return HttpResponse('Не достаточно количества товара в магазине')
            total_cost = quantity * goods_in_market.price + cart.total_cost
            if balance < total_cost:
                return HttpResponse('Не достаточно средств на вашем балансе')
            cart.total_cost = total_cost
            cart.save()
            ItemCartModel.objects.create(cart=cart,
                                         item_goods=self.get_object(),
                                         quantity=quantity)
            logger.info('Goods added to cart')
            return redirect(reverse_lazy('goods_list'))
        return render(request, 'app_markets/goods_detail.html', context=self.get_context_data())


class ItemsCartListView(LoginRequiredMixin, ListView):
    """Класс вью, для отображения содержания корзины"""
    template_name = 'app_markets/cart.html'
    login_url = reverse_lazy('login')

    def get_queryset(self):
        if hasattr(self.request.user, 'cart'):
            queryset = ItemCartModel.objects.select_related('cart', 'item_goods__goods', 'item_goods__market').filter(
                cart_id=self.request.user.cart.id)
            return queryset
        return None

    def post(self, request):
        """Метод пост производит оплату товаров, находящихся в корзине по нажатию кнопки. При этом с кошелька
        пользователя списывается значение равное общей стоимости товаров, находящикся в корзине - cart.total_cost.
        Кроме того из соответствующего магазина списывается соответствующее количество товара.
        Для каждого товара в корзине после оплаты создаётся запись в модели "история покупок".
        После оплаты меняется значение поля profile.total_expense, проверяется преодоление порога следующего
        статуса. Если порог преодолён, то пользователю присваивается очередной статус."""
        self.queryset = self.get_queryset()
        with transaction.atomic():
            PurchaseHistory.objects.bulk_create([PurchaseHistory(goods_id=item_cart.item_goods_id,
                                                                 quantity=item_cart.quantity)
                                                 for item_cart in self.queryset])
            objs = []
            for item_cart in self.queryset:
                objs.append(item_cart.item_goods.write_off_store(item_cart.quantity))
            ItemGoodsMarketModel.objects.bulk_update(objs, ('quantity',))
            profile = self.request.user.profile
            total_cost = self.request.user.cart.total_cost
            profile.change_balance(-total_cost)
            logger.info("Funds have been debited from the user's balance")
            profile.change_total_expenses(total_cost)
            profile.check_status()
            self.request.user.cart.delete()
        return redirect(reverse_lazy('index'))


class ReportListView(ListView):
    """Класс вью - отчёт о самых продаваемых товарах. Если указать период времени, будет список самых продаваемых
    товаров за этот период, если не указывать, то за всё время."""
    template_name = 'app_markets/report_list.html'

    def get_queryset(self):
        if not self.queryset:
            queryset = GoodsModel.objects.all().annotate(
                total_quantity=Sum('item_goods__purchase_history__quantity')).order_by('-total_quantity').only('id',
                                                                                                               'name')
            return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = {**super().get_context_data(), 'form': DatePeriodForm()}
        return context

    def post(self, request):
        form = DatePeriodForm(request.POST)
        if form.is_valid():
            start_period = form.cleaned_data.get('start_period')
            end_period = form.cleaned_data.get('end_period')
            zero_time = datetime.time()
            start_period = datetime.datetime.combine(start_period, zero_time)
            end_period = datetime.datetime.combine(end_period, zero_time)
            self.queryset = GoodsModel.objects.filter(Q(item_goods__purchase_history__date__gte=start_period)
                                                      & Q(item_goods__purchase_history__date__lte=end_period)).annotate(
                total_quantity=Sum('item_goods__purchase_history__quantity')).order_by('-total_quantity').only('id',
                                                                                                               'name')
            self.object_list = self.queryset
            context = self.get_context_data(object_list=self.object_list)
            return self.render_to_response(context)
