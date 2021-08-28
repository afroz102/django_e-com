from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View

from .forms import CheckoutForm
from .models import Address, Item, Order, OrderItem


import stripe
stripe.api_key = settings.STRIPE_API_KEY


# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token


class HomeView(ListView):
    model = Item
    paginate_by = 10
    context_object_name = "items"
    template_name = 'core/home-page.html'


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {
            'form': form,
        }
        return render(self.request, 'core/checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                # print(form.cleaned_data)
                # print("The form is valid")
                payment_option = form.cleaned_data.get('payment_option')
                Address.objects.create(
                    user=self.request.user,
                    street_address=form.cleaned_data.get('street_address'),
                    apartment_address=form.cleaned_data.get(
                        'apartment_address'),
                    country=form.cleaned_data.get('country'),
                    state=form.cleaned_data.get('state'),
                    zip=form.cleaned_data.get('zip'),
                )
                # TODO add redirected to payment options
                return redirect('core:checkout')
            else:
                # print(self.request.POST)
                print("The form is not valid")
                messages.warning(self.request, 'Checkout failed.')
                return redirect('core:checkout')
        except Order.DoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('core:order-summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        context = {}
        return render(self.request, 'core/payment.html', context)

    def post(self, *args, **kwargs):
        stripe.Charge.create(
            amount=2000,
            currency="usd",
            source="tok_amex",
            description="My First Test Charge (created for API docs)",
        )
        return redirect('/')


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'order_obj': order,
            }
            return render(self.request, 'core/order_summary.html', context)
        except Order.DoesNotExist:
            messages.info(self.request, 'You do not have any active order.')
            return redirect('/')

    # model = Order
    # template_name = 'core/order_summary.html'


class ItemDetailView(DetailView):
    model = Item
    context_object_name = "item"
    template_name = 'core/item_details.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user)
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    # print("order_qs: ", order_qs)

    # Check if order exists
    if order_qs.exists():
        order = order_qs[0]

        # Check if order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
            # print("Order item updated")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
            # print("Order item created")
    else:
        ordered_date = timezone.now()

        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date
        )
        order.items.add(order_item)
        # print("Order and Order item created")
        messages.info(request, "This item was added to your cart.")
        return redirect('core:order-summary')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # order_item, created = OrderItem.objects.get_or_create(item=item)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    # Check if order exists
    if order_qs.exists():
        order = order_qs[0]

        # Check if order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.get(
                item=item, user=request.user, ordered=False)
            order.items.remove(order_item)
            order_item.delete()
            # print("Order item removed")
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            # Add a message saying that the Order does not contain order item
            # print("the Order does not contain order item")
            messages.info(request, "This item was not in your cart")
            return redirect("core:order-summary")

    else:
        # Add a message saying that the user does not have an order
        # print('the user does not have an order')
        messages.info(request, "You do not have an active order")
        return redirect("core:order-summary")

    # return redirect('core:product', slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)
