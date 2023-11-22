from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from .models import EnrichmentRecordModel, EnrichmentSearchRecordModel
from .helperfunctions import get_object_or_none

from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model

class PasswordResetConfirmationForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetConfirmationForm, self).__init__(*args, **kwargs)

    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'}),
    )
    new_password2 = forms.CharField(
        label=_("New password (again)"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'}),
    )

class UserPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)

    email = forms.EmailField(label=_('E-Mail Address'), widget=forms.EmailInput(attrs={
        'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
        'placeholder': 'mary.william@example.com',
        'type': 'email',
        'name': 'email'
        }))

    def clean_email(self):
        email = self.cleaned_data['email']
        model = get_user_model()
        if not model.objects.filter(email__iexact=email, is_active=True).exists():
            self.add_error('email', 'There is no user registered with the specified email address!')

        return email

class EnrichmentRecordForm(forms.ModelForm):

    class Meta:
        model = EnrichmentRecordModel
        fields = ('enrichment_field', 'gene_list', 'shareable', 'description')
        exclude = ['task_id', 'user', 'complete', 'success']
        widgets = {
            'gene_list': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 2}),
        }


    def __init__(self, *args, **kwargs):

        self.user = kwargs.pop('user', None)

        super(EnrichmentRecordForm, self).__init__(*args, **kwargs)

        self.fields.get('gene_list').widget.attrs.update({
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'BRCA1, BRCA2, APOE, APEX1...'
        })

        self.fields.get('enrichment_field').widget.attrs.update({
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })

        self.fields.get('shareable').widget.attrs.update({
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })

        self.fields.get('description').widget.attrs.update({
            'class': 'p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Breast cancer related biomarker candidates.'
        })

    def clean(self):

        form_data = self.cleaned_data
        shareable = form_data.get('shareable', None)

        if shareable != 'public' and not self.user.is_authenticated:
            self.add_error('shareable', 'You are unable to designate your outcomes as private unless you are logged in.')



class EnrichmentSearchForm(forms.ModelForm):

    class Meta:
        model = EnrichmentSearchRecordModel
        fields = ('searched_task_id',)
        exclude = ['is_task_id_valid', 'is_permitable_search']

    def __init__(self, *args, **kwargs):
        super(EnrichmentSearchForm, self).__init__(*args, **kwargs)

        self.fields.get('searched_task_id').widget.attrs.update({
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5',
            'placeholder': 'Copy your task_id, the format must be UUID'
        })

    def clean(self):
        data = self.cleaned_data
        user = data.get('user', None)
        model_object = get_object_or_none(EnrichmentRecordModel, task_id=data.get('searched_task_id', None))

        if not model_object:

            data.update({
                'is_task_id_valid': False
            })

            raise ValidationError(_("Enter a valid task id."))

        if model_object.shareable != 'public' and (user == None or user != model_object.user):

            data.update({
                'is_permitable_search': False
            })

            raise ValidationError(_("Result is flagged as private."))

        return data

