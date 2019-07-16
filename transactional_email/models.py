from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .conf import TEMPLATE_PREFIX


class Template(models.Model):
    """
    Defines a template which can contains various versions. Only 1 version can
    be active. The active version will be loaded by the database template
    loader.
    """
    name = models.CharField(
        unique=True,
        max_length=255,
        default=TEMPLATE_PREFIX,
        help_text=f'Example: "transactional_email/welcome.html"'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return f'{self.name}'

    def save(self, *args, **kwargs):
        """
        Prefix the name with TEMPLATE_PREFIX if the name doesn't start with
        it.
        """
        if self.pk is None:
            if not self.name.startswith(TEMPLATE_PREFIX):
                self.name = f'{TEMPLATE_PREFIX}{self.name}'
        super(Template, self).save(*args, **kwargs)

    def versions(self):
        return self.templateversion_set.all().order_by('-active', '-created')


def _default_name():
    return f'v{now().strftime("%Y-%m-%d-%H:%M:%S:%f")}'


class TemplateVersionManager(models.Manager):
    def reset_active(self, instance) -> None:
        """
        Set active=False for all instance with the same template. Except for
        the instance itself.
        """
        super().get_queryset() \
            .filter(template=instance.template, active=True)\
            .exclude(pk=instance.pk)\
            .update(active=False)

    def active(self, template_name: str):
        qs = super().get_queryset()
        return qs.get(template__name=template_name, active=True)

    def duplicate(self, pk: int):
        obj = super().get(pk=pk)
        obj.name = _default_name()
        obj.pk = None
        obj.save()
        return obj.pk


class TemplateVersion(models.Model):
    """
    Version of a template. Only 1 version can be active
    """
    template = models.ForeignKey(
        Template,
        on_delete=models.PROTECT
    )
    name = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        default=_default_name,
        help_text='Unique name for this template version',
        verbose_name='Version Name'
    )
    active = models.BooleanField(
        default=False,
        help_text='Active version'
    )
    content = models.TextField(
        blank=True,
        help_text='Content of the e-mail template'
    )
    test_data = JSONField(
        null=False,
        blank=False,
        default=dict,
        help_text='JSON structure with test data view and send test e-mails'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    objects = TemplateVersionManager()

    class Meta:
        ordering = ('-active', '-updated')
        unique_together = ('template', 'name')

    def __str__(self):
        return f'Version: {self.name} ({self.template.name})'


class MailConfig(models.Model):
    template = models.ForeignKey(
        Template,
        on_delete=models.PROTECT
    )
    name = models.CharField(
        null=False,
        blank=False,
        unique=True,
        max_length=255,
        help_text='Name of this mail configuration. Eg: admin.notification',
    )
    description = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        help_text='More verbose description about the Transactional E-mail'
    )
    subject = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        help_text='Subject of the e-mail'
    )
    from_email = models.CharField(
        null=False,
        blank=False,
        max_length=255,
        help_text='From e-mail. Example: Jeffrey Lebowski '
                  '<jeffrey@dudeism.com>'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ('-name', '-updated')

    def __str__(self):
        return f'MailConfig: {self.name} ({self.pk})'


class EmailLog(models.Model):
    """
    Model to store all the outgoing emails.
    """
    when = models.DateTimeField(
        null=False,
        auto_now_add=True
    )
    from_email = models.EmailField(
        null=False,
        blank=False
    )
    to_email = models.EmailField(
        null=False,
        blank=False,
    )
    subject = models.CharField(
        null=False,
        max_length=128,
    )
    body = models.TextField(
        null=False,
    )
    ok = models.BooleanField(
        null=False,
        default=True,
        help_text=''
    )
    service = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        help_text='Which services was used to send this e-mail. '
                  'Eg: sendgrid, mailgun, etc'
    )
    message_id = models.CharField(
        null=True,
        blank=True,
        max_length=255,
        help_text='Optional message ID assigned by the service.'
    )

    class Meta:
        ordering = ['-when']

    @property
    def service_short(self):
        if self.service:
            arr = self.service.split('.')
            return '.'.join(arr[len(arr)-2:])
        return None


@receiver(post_save,
          sender=TemplateVersion,
          dispatch_uid='update_template_version')
def signal_update_active(sender, instance: TemplateVersion, **kwargs):
    """
    If the current instance is set to active this signal will set all other
    instances with the same template to active=False
    """
    if instance.active:
        TemplateVersion.objects.reset_active(instance)
