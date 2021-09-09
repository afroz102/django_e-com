from django.contrib import admin

from .models import Address, Coupon, Item, Order, OrderItem, Payment, Refund, UserProfile

"""
     This function updates the order model in django custum admin just
     like custom select and delete row in django admin
"""


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


# Default name is just the name of the function
make_refund_accepted.short_description = 'Update orders to refund granted'


# Customizing admin panel
class OrderAdmin(admin.ModelAdmin):
    # Displays the list of all the fields mentioned in django admin panel row
    list_display = [
        'user', 'ordered', 'being_delivered', 'received', 'refund_requested',
        'refund_granted', 'shipping_address', 'billing_address',
        'payment', 'coupon'
    ]

    # displays all the foreign key, on-to-one fields, ... with links
    list_display_links = [
        'user', 'shipping_address', 'billing_address', 'payment', 'coupon'
    ]

    # all the list we can filter by. in the right corner in django admin panel
    list_filter = [
        'ordered', 'being_delivered', 'received', 'refund_requested',
        'refund_granted'
    ]

    # searchable fields in the admin panel on top
    search_fields = [
        'user__username', 'ref_code'
    ]

    # allows to update order just like custom delete method in admin panel
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'street_address', 'apartment_address', 'country', 'zip',
        'address_type', 'default'
    ]
    list_filter = ['default', 'address_type']

    # user__username looks for field username in user model
    search_fields = [
        'user__username', 'street_address', 'apartment_address',
        'zip', 'country'
    ]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(UserProfile)
