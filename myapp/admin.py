from django.contrib import admin
from .models import Contact, User, Event, BookEvent
# Register your models here.
admin.site.register(Contact)
admin.site.register(User)
admin.site.register(Event)
admin.site.register(BookEvent)