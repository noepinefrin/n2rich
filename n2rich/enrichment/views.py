from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import EnrichmentRecordForm

from .tasks import sharedtask
from .helperfunctions import get_selected_field_dbs

# Create your views here.
def progress_view(request):
    return render(request, 'progress.html')

def index(request):
    return render(request, 'landing.html')

def analysis(request):
    context = {}

    form = EnrichmentRecordForm(request.POST or None)

    if form.is_valid():

        result = sharedtask.delay(1)

        form.instance.task_id = result.task_id

        form.save()

        request.session['field_dbs'] = get_selected_field_dbs(request)
        request.session['task_id'] = result.task_id

        return HttpResponseRedirect(reverse('analysis_progress'))

    context.update({
        'form': form
    })

    return render(request, 'analysis.html', context)