from django.contrib import admin
from .models import *

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_granted=True)

make_refund_accepted.short_description = 'Update Order To refund granted'


def order_completed(modeladmin,request,queryset):
    queryset.update(completed=True)

order_completed.short_description = 'Order Completed'

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'item',
                    'quantity',
                    'ordered'
    ]

    list_display_links = [
                'user',
                'item'

    ]

    list_filter = ['user',
                    'item',
                    'quantity',
                    'ordered'
                    ]

    search_fields = [
            'user__username',

    ]

class OrderAdmin(admin.ModelAdmin):
    list_display = [ 'user',
                    'ordered',
                    'status',
                    'street_address',
                    'apartment_address',
                    'city',
                    'phone'

 
    ]

    list_display_links = [
                'user',

    ]

    list_filter = [
                    'ordered',
                    'status',
                    'user'
                    ]

    search_fields = [
            'id',
            'user__username',
            'ref_code'
    ]

    actions = [make_refund_accepted]

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'city',
        'phone',
        'default',
    ]

    list_filter = ['default','street_address','apartment_address','city']
    search_fields = ['user__username','street_address','apartment_address','city']

    actions = [order_completed]


# class GalleryImagAdmin(admin.StackedInline):
#     model = GalleryImage

# @admin.register(Gallery)
# class GalleryAdmin(admin.ModelAdmin):
#     inlines = [GalleryImagAdmin]
    
#     class Meta:
#         model = Gallery

# @admin.register(GalleryImage)
# class GalleryImageAdmin(admin.ModelAdmin):
#     pass

admin.site.index_title = "Linder's Cuisine"
admin.site.site_header = "Linder's Cuisine Admin"
admin.site.register(Item)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Refund)
admin.site.register(Contact)
admin.site.register(Carousel)
admin.site.register(About)
admin.site.register(Footer)
admin.site.register(Services)
admin.site.register(Gallery)