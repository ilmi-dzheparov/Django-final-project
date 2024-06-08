from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import UserCreationForm
from .models import User


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    list_display = ('birth_date', 'phone', 'email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': (
            'username',
            'last_name',
            'birth_date',
            'phone',
            'avatar',
        )
        }),
        ('Permissions', {'fields': ('is_active',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'phone', 'password1', 'password2'),
        }),
    )
    search_fields = ('email', 'username', 'last_name')
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, CustomUserAdmin)
