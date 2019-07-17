from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import render, reverse, get_object_or_404
from django.views import View
from .models import MailConfig, Template, TemplateVersion, EmailLog
from . import conf
from . import utils


@login_required
@user_passes_test(lambda u: u.is_staff)
def mail_configs(request):
    configs_all = MailConfig.objects.all().order_by('name')
    context = {
        'menu': 'mail_configs',
        'configs': configs_all
    }
    return render(request, 'transactional_email_web/mail_configs.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def templates(request):
    templates_all = Template.objects.all().order_by('name')
    context = {
        'menu': 'templates',
        'templates': templates_all
    }
    return render(request, 'transactional_email_web/templates.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def logs(request):
    logs_all = EmailLog.objects.all().order_by('-when')
    context = {
        'menu': 'logs',
        'logs': logs_all
    }
    return render(request, 'transactional_email_web/logs.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def log(request, pk: int):
    _log = get_object_or_404(EmailLog, pk=pk)
    context = {
        'menu': 'logs',
        'log': _log
    }
    return render(request, 'transactional_email_web/log.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def preview(request, pk: int):
    version = get_object_or_404(TemplateVersion, pk=pk)
    context = {
        'menu': 'templates',
        'version': version
    }
    return render(request, 'transactional_email_web/preview.html', context)


class AuthMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user    # type: User
        return user.is_staff


class EmailLogsView(AuthMixin, View):
    def get(self, request, pk: int):
        log = EmailLog.objects.get(pk=pk)
        return HttpResponse(log.body)

    def post(self, request):
        """
        Sends a test mail. Template will be rendered with test data.
        """
        name = request.POST.get('config')
        email = request.POST.get('recipient')
        config = MailConfig.objects.get(name=name)
        version = TemplateVersion.objects.active(config.template.name)
        pk = utils.issue(name, email, version.test_data)
        return JsonResponse({'id': pk})


class TemplatesView(AuthMixin, View):
    def delete(self, request, pk: int):
        utils.delete(pk)
        return JsonResponse({'status': 'ok'})


class TemplateVersionsView(AuthMixin, View):
    def put(self, request, pk: int):
        instance = TemplateVersion.objects.get(pk=pk)
        instance.active = True
        instance.save()
        return JsonResponse({'id': pk})

    def post(self, request, pk: int):
        pk = TemplateVersion.objects.duplicate(pk)
        return JsonResponse({'id': pk})


class TemplateVersionPreviewView(AuthMixin, View):
    def get(self, request, pk: int):
        version = TemplateVersion.objects.get(pk=pk)
        name = version.version_name
        rendered = utils.render_version(name, version.test_data)
        return HttpResponse(rendered)
