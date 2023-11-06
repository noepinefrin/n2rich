from django.contrib import admin
from .models import EnrichmentRecordModel
# Register your models here.

class EnrichmentRecordModelAdmin(admin.ModelAdmin):
    readonly_fields = [field.name for field in EnrichmentRecordModel._meta.fields]

admin.site.register(EnrichmentRecordModel, EnrichmentRecordModelAdmin)