from celery import shared_task
from celery_progress.backend import ProgressRecorder
import time

@shared_task(bind=True)
def sharedtask(self, duration):
    progress_recorder = ProgressRecorder(self)
    for i in range(10):
        time.sleep(duration - 0.30)
        progress_recorder.set_progress(i + 1, 10, f'On iteration {i}')
    return 'Done'