from django.db import models
from .validators import gene_list_validator
from .helperfunctions import string_parser

# Create your models here.
class EnrichmentRecordModel(models.Model):
    """
    Enrichment Records for analysed genes.
    """
    ENRICHMENT_CHOICES = (
        ('Transcription', 'Transcription'),
        ('Pathways', 'Pathways'),
        ('Ontologies', 'Ontologies'),
        ('Diseases/Drugs', 'Diseases/Drugs'),
        ('Cell Types', 'Cell Types')
    )

    analysed_at = models.DateTimeField(auto_now_add=True)
    enrichment_field = models.CharField(max_length=30, choices=ENRICHMENT_CHOICES, blank=False, null=False, default=ENRICHMENT_CHOICES[2][0])
    description = models.CharField(max_length=280, help_text='Write a recollective description for enrichment analysis up to 280 character.', null=True, blank=True)
    gene_list = models.CharField(max_length=500, help_text='Copy your biomarker candidates up to 100 genes.', validators=[gene_list_validator])
    email = models.EmailField(max_length=100, help_text='Share your e-mail adress to see enrichment results in your email as txt.', blank=True, null=True)
    task_id = models.CharField(max_length=50, unique=True, null=True, blank=True)


    def __str__(self):
        return f'{len(self.listed_genes)} genes analyzed at {self.enrichment_field} field.'

    @property
    def listed_genes(self) -> list | None:
        """
        Returns parsed genes as list.
        """
        return string_parser(self.gene_list)
