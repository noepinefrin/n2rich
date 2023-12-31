from collections.abc import Iterable
from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)

from .validators import gene_list_validator
from .helperfunctions import string_parser, get_upload_path

import os

# User Manager Model
class UserManager(BaseUserManager):
    """
    Manager class for users.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

# User Model

class User(PermissionsMixin, AbstractBaseUser):
    """
    Default user class.
    """
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

# EnrichmentRecordModel
class EnrichmentRecordModel(models.Model):
    """
    Enrichment Records for analysed genes saved from `url:analysis/`.
    """
    ENRICHMENT_CHOICES = (
        ('Transcription', 'Transcription'),
        ('Pathways', 'Pathways'),
        ('Ontologies', 'Ontologies'),
        ('Diseases/Drugs', 'Diseases/Drugs'),
        ('Cell Types', 'Cell Types')
    )

    IS_PUBLIC_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private')
    )

    analysed_at = models.DateTimeField(auto_now_add=True)
    enrichment_field = models.CharField(max_length=30, choices=ENRICHMENT_CHOICES, blank=False, null=False, default=ENRICHMENT_CHOICES[2][1], help_text='Select field which your biomarker candidates will enriched.')
    description = models.CharField(max_length=280, help_text='Write a recollective description for enrichment analysis up to 280 character.', null=True, blank=True)
    gene_list = models.CharField(max_length=500, help_text='Copy your biomarker candidates up to 100 genes.', validators=[gene_list_validator])
    gene_count = models.PositiveSmallIntegerField('gene_c', blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    task_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    shareable = models.CharField('shareable', max_length=30, choices=IS_PUBLIC_CHOICES, blank=False, null=False, default=IS_PUBLIC_CHOICES[0][1], help_text='Your results can be viewed by everyone if is selected public. Otherwise, It requires sign in.')
    complete = models.BooleanField('complete', default=False)
    success = models.BooleanField('success', default=False)
    result = models.FileField('result', upload_to=get_upload_path, null=True, blank=True)
    is_active = models.BooleanField('is_active', default=False)

    def __str__(self):
        return f'{len(self.listed_genes)} genes analyzed at {self.enrichment_field} field.'

    @property
    def listed_genes(self) -> list:
        """
        Returns parsed genes as list.
        """
        return string_parser(self.gene_list)

    @property
    def get_gene_count(self) -> int:
        """
        Returns number of the genes that analyzed.
        """
        return len(self.listed_genes)

    def save(self, *args, **kwargs):
        self.gene_count = self.get_gene_count
        super(EnrichmentRecordModel, self).save(*args, **kwargs)

@receiver(models.signals.post_delete, sender=EnrichmentRecordModel)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes results from filesystem
    when corresponding `EnrichmentRecordModel` object is deleted.
    """
    if instance.result:
        if os.path.isfile(instance.result.path):
            os.remove(instance.result.path)

class EnrichmentSearchRecordModel(models.Model):
    """
    Search records saved from `url:get_record/`
    """
    searched_task_id = models.CharField('searched_task_id', max_length=50, blank=False, null=False)
    searched_at = models.DateTimeField(auto_now_add=True)
    is_task_id_valid = models.BooleanField('is_task_id_valid', null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    is_permitable_search = models.BooleanField('is_permitable_search', null=True)

    def __str__(self):
        return f'Task Id: {self.searched_task_id} searched (Is valid: {self.is_task_id_valid}) at {self.searched_at}.'

class ContactUsModel(models.Model):

    SUBJECT = (
        ('general_info', 'General Information'),
        ('suggestion', 'Suggestion'),
        ('request_for_support', 'Request for Support'),
        ('contrib_to_dev', 'Contribute to Development'),
        ('bug_declaration', 'Bug Declaration'),
        ('other', 'Other')
    )

    name = models.CharField('name', max_length=128, blank=False, null=False)
    contact_at = models.DateTimeField('contact_at', auto_now_add=True)
    email = models.EmailField('email', max_length=255)
    subject = models.CharField('subject', choices=SUBJECT, default=SUBJECT[0][1], max_length=255)
    message = models.TextField('message', max_length=1024)

    def __str__(self):
        return f'Subject: {self.subject} from {self.email}'