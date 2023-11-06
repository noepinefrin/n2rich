from django import forms
from .models import EnrichmentRecordModel

class EnrichmentRecordForm(forms.ModelForm):

    class Meta:
        model = EnrichmentRecordModel
        fields = ('enrichment_field', 'email', 'gene_list', 'description')
        exclude = ['task_id']
        widgets = {
            'gene_list': forms.Textarea(attrs={'rows': 5}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.get('gene_list').widget.attrs.update({
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'BRCA1, BRCA2, APOE, APEX1...'
        })

        self.fields.get('enrichment_field').widget.attrs.update({
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5'
        })

        self.fields.get('description').widget.attrs.update({
            'class': 'block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500',
            'placeholder': 'Breast cancer related biomarker candidates.'
        })

        self.fields.get('email').widget.attrs.update({
            'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5',
            'placeholder': 'john@example.com'
        })




