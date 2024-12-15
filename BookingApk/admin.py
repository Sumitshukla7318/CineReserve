from django.contrib import admin
from . models import Theater,Screen,WeeklySchedule,Slot,Unavailability


admin.site.register(Theater)
admin.site.register(Screen)
admin.site.register(WeeklySchedule)
admin.site.register(Slot)
admin.site.register(Unavailability)
