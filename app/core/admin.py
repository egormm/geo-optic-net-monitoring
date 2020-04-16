from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.gis.admin import OSMGeoAdmin as BaseGeoAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


class GeoAdmin(BaseGeoAdmin):
    """Admin page, based on OpenStreetMaps,
     with defaults, aimed on Spas-Klepiki"""

    default_lon = 4472225.42343
    default_lat = 7387466.79942
    default_zoom = 15


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Box, GeoAdmin)
admin.site.register(models.Wire, GeoAdmin)
