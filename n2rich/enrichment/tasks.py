from celery_progress.backend import ProgressRecorder
from celery import Task
from .helperfunctions import get_selected_field_dbs, string_parser, replacedb
from .enrichment import ConnectDB, Enrichment
from n2rich.celery import app
from enrichment.models import EnrichmentRecordModel
from enrichment.helperfunctions import get_object_or_none

from django.core.files.base import ContentFile

import json

class BaseTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        obj = get_object_or_none(EnrichmentRecordModel, task_id=task_id)

        if obj:
            obj.complete = False
            obj.success = False
            obj.save()

    def on_success(self, retval, task_id, args, kwargs):
        obj = get_object_or_none(EnrichmentRecordModel, task_id=task_id)

        if obj:
            json_retval = json.dumps(retval)

            obj.result.save('analysis.json', ContentFile(json_retval))
            obj.complete = True
            obj.success = True
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
