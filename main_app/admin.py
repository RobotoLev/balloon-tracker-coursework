from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from . import models

# Register your models here.


"""
Description for the code below.
* `list_display` stands for the list of fields to show in the table
* `fieldsets` stands for the internal page markup of an entry 
More detailed information can be found in Django documentation.
"""


class UserAdmin(DjangoUserAdmin):
    model = models.User

    list_display = ("username", "rooms_layout", "first_name", "last_name", "is_staff")
    fieldsets = (
        (None, {'fields': ('rooms_layout',)}),
    ) + DjangoUserAdmin.fieldsets


admin.site.register(models.User, UserAdmin)


@admin.register(models.Contest)
class ContestAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'test_system', 'admin')


@admin.register(models.Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'contest', 'problem_index', 'author', 'time_from_start', 'verdict')


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('submission', 'balloon_color', 'room', 'place', 'author_name', 'volunteer', 'done')
