# Generated by Django 4.2.6 on 2023-11-27 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrichment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrichmentrecordmodel',
            name='gene_count',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='gene_c'),
        ),
    ]
