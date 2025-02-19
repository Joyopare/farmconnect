from django.contrib import admin
from .models import Farmer, Customer, Order, Review, AdminDashboard,Product

admin.site.register(Farmer)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(AdminDashboard)
admin.site.register(Product)
