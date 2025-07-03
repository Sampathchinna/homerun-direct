from django.contrib import admin
from .models import Language, Location, Currency, PaymentProcessor, CompanyType ,SubscriptionPlan

admin.site.register(Language)
admin.site.register(Currency)
admin.site.register(PaymentProcessor)
admin.site.register(Location)
admin.site.register(CompanyType)
admin.site.register(SubscriptionPlan)
