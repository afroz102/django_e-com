# from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField


CATEGORY_CHOISES = (
    ('S', 'Shirt'),
    ('SW', 'Sport Wear'),
    ('OW', 'OutWear'),
)
LABEL_CHOISES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger'),
)

# discount_price is the price after discount


class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True)
    description = models.TextField()
    category = models.CharField(
        max_length=2, choices=CATEGORY_CHOISES, default='S')
    label = models.CharField(max_length=2, choices=LABEL_CHOISES, default='P')
    slug = models.SlugField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:product', kwargs={
            'slug': self.slug,
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.item.price * self.quantity

    def get_total_discount_item_price(self):
        return self.item.discount_price * self.quantity

    def get_amount_saved(self):
        return self.get_total_item_price()-self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    items = models.ManyToManyField(OrderItem)

    ordered = models.BooleanField(default=False)
    start_date = models.DateField(auto_now_add=True)
    ordered_date = models.DateField()

    billing_address = models.ForeignKey(
        'Address', on_delete=models.SET_NULL, null=True)
    billing_address = models.ForeignKey(
        'Address', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total


class Address(models.Model):
    # ADDRESS_CHOICES = (
    #     ('B', 'Billing'),
    #     ('S', 'Shipping'),
    # )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    state = models.CharField(max_length=50)
    zip = models.CharField(max_length=10)
    # address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    # default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    stripe_payment_id = models.CharField(max_length=50)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
