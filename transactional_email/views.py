from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404, JsonResponse
from django.shortcuts import render, reverse, get_object_or_404
from .models import MailConfig, TemplateVersion
from .utils import issue


@login_required
@user_passes_test(lambda u: u.is_staff)
def index(request):
    configs = MailConfig.objects.all().order_by('name')
    context = {'configs': configs}
    return render(request, 'transactional_email_web/overview.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def test_mail(request):
    name = request.POST.get('config')
    email = request.POST.get('recipient')
    config = MailConfig.objects.get(name=name)
    version = TemplateVersion.objects.active(config.template.name)
    issue(name, email, version.test_data)
    return JsonResponse({'status': 'ok'})
