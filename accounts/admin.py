from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

# Register your models here.


# display each one of the flowwig values next to each user
# based on models/Account mandatory properties
class AccountAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name',
                    'username', 'last_login', 'is_active', 'date_joined')
    
    #links the user can tap to swtich windows
    list_display_links=('email', 'first_name', 'last_name')
    readonly_fields=('last_login', 'date_joined')
    ordering=('date_joined',)
    
    # needed fields, it hides the user's password once inside its info
    filter_horizontal = ()  # () blanks
    list_filter = ()
    fieldsets = ()


admin.site.register(Account, AccountAdmin)
