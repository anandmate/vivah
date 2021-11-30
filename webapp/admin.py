from django.contrib import admin
from .models import *
from import_export.admin import ImportExportActionModelAdmin

# Register your models here.


@admin.register(Profile, Candidate, Event, Event_enroll, Favorite, Seen, Feedback, Gallary)
class ViewAdmin(ImportExportActionModelAdmin):
    pass
