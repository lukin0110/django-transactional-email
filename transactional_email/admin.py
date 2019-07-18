from textwrap import shorten, fill
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.admin import SimpleListFilter
from django.db.models import TextField
from django.forms import Textarea
from django.urls import reverse
from django.utils.html import format_html
from .models import Template, TemplateVersion, MailConfig, EmailLog


class SuperUserMixin(object):
    """
    Templates, TemplateVersion & MailConfigs should not be managed from the
    Admin panel (only Super Users). The custom views must be used to manage
    templates & configs.
    """
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin, SuperUserMixin):
    list_display = ('pk', 'name', 'created')
    search_fields = ('name',)


@admin.register(TemplateVersion)
class TemplateVersionAdmin(admin.ModelAdmin, SuperUserMixin):
    list_display = ('pk', 'template', 'name', 'active', 'updated', 'show_actions')
    list_display_links = ('pk', 'template')
    list_filter = ('active',)
    search_fields = ('template__name', 'name')
    autocomplete_fields = ('template',)
    save_as = True
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 120})},
        JSONField: {'widget': Textarea(attrs={'rows': 20, 'cols': 120})},
    }

    def show_actions(self, obj: EmailLog):
        return format_html(
            '<a href="{url}" target="_blank">View</a>',
            url=reverse('transactional_email.versions.preview', args=[obj.pk])
        )
    show_actions.short_description = 'Actions'


@admin.register(MailConfig)
class MailConfigAdmin(admin.ModelAdmin, SuperUserMixin):
    list_display = ('pk', 'name', 'template', 'show_description', 'updated')
    list_display_links = ('pk', 'name')
    search_fields = ('template__name', 'name', 'description')
    autocomplete_fields = ('template',)

    def show_description(self, obj: MailConfig):
        if obj.description:
            return shorten(obj.description, 30, placeholder='...')
        return ''
    show_description.short_description = 'Description'


class ServiceFilter(SimpleListFilter):
    title = 'service'
    parameter_name = 'service2'

    def lookups(self, request, model_admin):
        services = EmailLog.objects.order_by('service').distinct('service')
        return [(
            s.service if s.service else '_NONE_',
            s.service_short if s.service_short else '-'
        ) for s in services]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '_NONE_':
            return queryset.filter(service__isnull=True)
        if value:
            return queryset.filter(service=self.value())


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['when', 'from_email', 'to_email', 'subject', 'ok',
                    'service_short', 'show_message_id',  'show_actions']
    list_filter = (ServiceFilter, 'ok')
    readonly_fields = ['when', 'from_email', 'to_email', 'subject', 'body',
                       'ok', 'service', 'message_id']
    search_fields = ['subject', 'body', 'from_email', 'to_email']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def show_message_id(self, obj: EmailLog) -> str:
        if obj.message_id:
            return shorten(fill(obj.message_id, 20, break_long_words=True), width=23, placeholder='...')
        return ''
    show_message_id.short_description = 'Message ID'

    def show_service(self, obj: EmailLog):
        if obj.service:
            arr = obj.service.split('.')
            return '.'.join(arr[len(arr)-2:])
        return None
    show_service.short_description = 'Service'

    def show_actions(self, obj: EmailLog):
        return format_html(
            '<a href="{url}" target="_blank">View</a>',
            url=reverse('transactional_email.emails.view', args=[obj.pk])
        )
    show_actions.short_description = 'Actions'
