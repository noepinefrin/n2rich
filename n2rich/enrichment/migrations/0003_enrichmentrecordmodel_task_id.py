# Generated by Django 4.2.6 on 2023-11-02 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrichment', '0002_alter_enrichmentrecordmodel_enrichment_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='enrichmentrecordmodel',
            name='task_id',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]