from django.core.files.base import ContentFile
from django.utils import timezone as tz

from n2rich.celery import app
from celery_progress.backend import ProgressRecorder
from celery import Task
from celery.schedules import crontab

from .helperfunctions import get_selected_field_dbs, string_parser, replacedb, get_object_or_none
from .enrichment import ConnectDB, Enrichment
from .models import EnrichmentRecordModel

import datetime
import json


@app.task
def clean_db_after_14_days():
    d = tz.now() - datetime.timedelta(days=14)
    later_than_14_days_results = EnrichmentRecordModel.objects.filter(analysed_at__lt=d)

    for record in later_than_14_days_results:
        record.result.delete() # Delete results after 14 days because of storage issues.
        record.is_active = False
        record.save()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=6, minute=0), # Execute every day at 6.00 A.M.
        clean_db_after_14_days.s(),
    )

class BaseTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        obj = get_object_or_none(EnrichmentRecordModel, task_id=task_id)

        if obj:
            obj.complete = True
            obj.success = False
            obj.save()

    def on_success(self, retval, task_id, args, kwargs):
        obj = get_object_or_none(EnrichmentRecordModel, task_id=task_id)

        if obj:
            json_retval = json.dumps(retval)

            obj.result.save(f'{task_id}.json', ContentFile(json_retval))
            obj.complete = True
            obj.success = True
            obj.is_active = True
            obj.save()

@app.task(bind=True, base=BaseTask)
def enrichment_analysis(self, gene_list_str, field):

    gene_list = string_parser(gene_list_str)
    enriched_results = {}

    progress_recorder = ProgressRecorder(self)
    field_dbs = get_selected_field_dbs(field)

    for i, db in enumerate(field_dbs, 1):

        replaced_db_name = replacedb(db, '_')

        progress_recorder.set_progress(i, len(field_dbs), f'{replaced_db_name} is analyzing...')

        connect_db = ConnectDB(db)
        dbs, dbs_stats, dbs_unique = connect_db._get_DBs_and_stats()
        enrichment = Enrichment(gene_list, dbs, dbs_stats, dbs_unique)
        enrichment_result = enrichment.response()

        enriched_results.update({
            db: enrichment_result
        })

    return enriched_results
