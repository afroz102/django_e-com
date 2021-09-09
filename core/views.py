import random
import string

from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View

from .forms import CheckoutForm, CouponForm, PaymentForm, RefundForm
from .models import (
    Address, Coupon, Item, Order, OrderItem, Payment, Refund, UserProfile
)


import stripe
stripe.api_key = settings.STRIPE_API_KEY


# `source` is obtained with Stripe.js; see
# https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token


def create_ref_code():
    return ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=20
    ))


class HomeView(ListView):
    model = Item
    paginate_by = 10
    context_object_name = "items"
    template_name = 'core/home-page.html'


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update({
                    'default_billing_address': billing_address_qs[0]
                })
            return render(self.request, "core/checkout-page.html", context)
        except Order.DoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:home")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    # print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default \
                            shipping address available")
                        return redirect('core:checkout')
                else:
                    # print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    # shipping_state = form.cleaned_data.get(
                    #     'shipping_state')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([
                        shipping_address1,
                        shipping_country,
                        shipping_zip
                    ]):
                        # state=shipping_state,
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(self.request, "Please fill \
                            in the required shipping address fields")

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    # print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default \
                            billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_country = form.cleaned_data.get(
                        'billing_country')
                    # billing_state = form.cleaned_data.get(
                    #     'billing_state')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([
                        billing_address1,
                        billing_country,
                        billing_zip
                    ]):
                        # state=billing_state,
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(self.request, "Please fill in the\
                             required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except Order.DoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")
        # form = CheckoutForm(self.request.POST)
        # try:
        #     order = Order.objects.get(user=self.request.user, ordered=False)
        #     if form.is_valid():
        #         # print(form.cleaned_data)
        #         # print("The form is valid")
        #         payment_option = form.cleaned_data.get('payment_option')
        #         Address.objects.create(
        #             user=self.request.user,
        #             street_address=form.cleaned_data.get('street_address'),
        #             apartment_address=form.cleaned_data.get(
        #                 'apartment_address'),
        #             country=form.cleaned_data.get('country'),
        #             state=form.cleaned_data.get('state'),
        #             zip=form.cleaned_data.get('zip'),
        #         )
        #         if payment_option == 'S':
        #             return redirect('core:payment', payment_option='stripe')
        #         elif payment_option == 'P':
        #             return redirect('core:payment', payment_option='paypal')
        #         else:
        #             messages.warning(
        #                 self.request, 'Invalid payment option selected.')
        #             return redirect('core:checkout')#     else:
        #         # print(self.request.POST)
        #         # print("The form is not valid")
        #         messages.warning(
        #             self.request,
        #             'Checkout failed. Please fill all the valid fields.'
        #         )
        #         return redirect('core:checkout')
        # except Order.DoesNotExist:
        #     messages.warning(self.request, 'You do not have an active order')
        #     return redirect('core:order-summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY': settings.PUBLISHABLE_KEY
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "core/payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')

            print("Token: ", token)

            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and (
                        userprofile.stripe_customer_id is not None):
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total_price() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the
                    #  token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id,
                        description="stripe demo charge",
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total_price()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")
            except stripe.error.CardError as e:
                # Since it's a decline, stripe.error.CardError will be caught
                messages.warning(self.request, f"{e.user_message}")

                # from github code
                error_body = e.json_body
                err = error_body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")

                print('Status is: %s' % e.http_status)
                print('Code is: %s' % e.code)
                # param is '' in this case
                print('Param is: %s' % e.param)
                print('Message is: %s' % e.user_message)
            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                print("Rate limit Error>>>>>>", e)
                messages.warning(self.request, "Rate limit error")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print("Invalid Parameters>>>>>>", e)
                messages.warning(self.request, "Invalid Parameters")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                print("Authentication Error >>>>>>", e)
                messages.warning(self.request, "Not Authenticated")
                return redirect('/')

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                print("Network Error >>>>>>", e)
                messages.warning(self.request, "Network error")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                print("Something stripe error >>>>>>", e)
                messages.warning(self.request, "Something went wrong. \
                    You were not charged. Please try again.")
                return redirect("/")
            except Exception as e:
                # Something else happened, completely unrelated to Stripe
                # send an email to ourselves
                print("Your code is not working >>>>>>", e)
                messages.warning(
                    self.request,
                    "A serious error occurred. We have been notifed."
                )

            return redirect('/')

    # def get(self, *args, **kwargs):
    #     order = Order.objects.get(user=self.request.user, ordered=False)
    #     couponform = CouponForm()
    #     if order.billing_address:
    #         context = {
    #             'order': order,
    #             'DISPLAY_COUPON_FORM': False,
    #             'STRIPE_PUBLIC_KEY': settings.PUBLISHABLE_KEY,
    #             "couponform": couponform,
    #             "DISPLAY_COUPON_FORM": False,
    #         }
    #         return render(self.request, 'core/payment.html', context)
    #     else:
    #         messages.warning(
    #             self.request, "You have not added a billing address")
    #         return redirect("core:checkout")
    # def post(self, *args, **kwargs):
    #     # print("request: ", self.request)
    #     loggedInUser = self.request.user
    #     order = Order.objects.get(user=loggedInUser, ordered=False)
    #     amount = int(order.get_total_price()) * 100
    #     token = self.request.POST.get('stripeToken')
    #     print("token: ", token)
    #     try:
    #         # Use Stripe's library to make requests...
    #         stripeCharge = stripe.Charge.create(
    #             amount=amount,  # in cents
    #             currency="usd",
    #             source=token,
    #             description="My First Test Charge",
    #         )
    #         paymentObj = Payment.objects.create(
    #             user=loggedInUser,
    #             stripe_payment_id=stripeCharge['id'],
    #             amount=amount,
    #         )
    #         order.ordered = True
    #         order.payment = paymentObj
    #         order.ref_code = create_ref_code()
    #         order.save()
    #         # update all many to many fields  of OrderItem in Order model
            # that item has been ordered
    #         order_items = order.items.all()
    #         order_items.update(ordered=True)
    #         for order_item in order_items:
    #             order_item.save()
    #         messages.success(self.request, 'Your order was successful!')
    #         return redirect('/')


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


# def add_coupon(request):
#     code = request.POST.get('code')
#     try:
#         coupon = Coupon.objects.get(code=code)
#     except Coupon.DoesNotExist:
#         messages.info(request, 'This coupon does not exists.')
#         return redirect('core:checkout')
#
#     try:
#         order = Order.objects.get(user=request.user, ordered=False)
#         order.coupon = coupon
#         order.save()
#         messages.success(request, "Coupon applied successfully!!")
#         return redirect('core:checkout')
#
#     except Order.DoesNotExist:
#         messages.info(request, 'You do not have an active order')
#         return redirect('core:checkout')


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except Coupon.DoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except Order.DoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "core/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except Order.DoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")
