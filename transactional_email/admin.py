from textwrap import shorten
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.conf.urls import url
from django.db.models import TextField
from django.forms import Textarea
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import format_html
from .models import Template, TemplateVersion, MailConfig, EmailLog


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'created')
    search_fields = ('name',)


@admin.register(TemplateVersion)
class TemplateVersionAdmin(admin.ModelAdmin):
    list_display = ('template', 'name', 'active', 'updated', 'show_actions')
    list_filter = ('active',)
    search_fields = ('template__name', 'name')
    autocomplete_fields = ('template',)
    save_as = True
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 20, 'cols': 120})},
        JSONField: {'widget': Textarea(attrs={'rows': 20, 'cols': 120})},
    }

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<id>.+)/view$',
                self.admin_site.admin_view(self.raw_view),
                name='template-version-view',
            ),
        ]
        return custom_urls + urls

    def raw_view(self, request, id, *args, **kwargs):
        from django.template import Template, Context
        template_version = TemplateVersion.objects.get(pk=id)
        t = Template(template_version.content)
        c = Context(template_version.test_data)
        return HttpResponse(t.render(c))

    def show_actions(self, obj: EmailLog):
        return format_html(
            '<a href="{url}" target="_blank">View</a>',
            url=reverse('admin:template-version-view', args=[obj.pk])
        )
    show_actions.short_description = 'Actions'


@admin.register(MailConfig)
class MailConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'template', 'show_description', 'updated')
    search_fields = ('template__name', 'name', 'description')
    autocomplete_fields = ('template',)

    def show_description(self, obj: MailConfig):
        if obj.description:
            return shorten(obj.description, 30, placeholder='...')
        return ''
    show_description.short_description = 'Description'


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['when', 'from_email', 'to_email', 'subject', 'service',
                    'ok', 'show_actions']
    list_filter = ['ok', 'service']
    readonly_fields = ['when', 'from_email', 'to_email', 'subject', 'body',
                       'ok', 'service', 'message_id']
    search_fields = ['subject', 'body', 'from_email', 'to_email']

    def has_delete_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request):
        return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<id>.+)/view$',
                self.admin_site.admin_view(self.raw_view),
                name='transactional-email-log-view',
            ),
        ]
        return custom_urls + urls

    def raw_view(self, request, id, *args, **kwargs):
        record = EmailLog.objects.get(pk=id)
        return HttpResponse(record.body)

    def show_actions(self, obj: EmailLog):
        return format_html(
            '<a href="{url}" target="_blank">View</a>',
            url=reverse('admin:transactional-email-log-view', args=[obj.pk])
        )
    show_actions.short_description = 'Actions'
