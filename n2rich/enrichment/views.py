from typing import Any

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib.auth import views as auth_views

from .forms import EnrichmentRecordForm, EnrichmentSearchForm, UserPasswordResetForm
from .models import EnrichmentRecordModel

from .tasks import enrichment_analysis
from .permissions import has_perm
from .helperfunctions import get_selected_field_dbs, get_object_or_none

import json

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name='account/password_reset.html'
    form_class=UserPasswordResetForm
    subject_template_name='account/password_reset_subject.txt'
    html_email_template_name='account/html_email_template.html'

    def dispatch(self, *args, **kwargs):
       if self.request.user.is_authenticated:
           return redirect('index')
       return super().dispatch(*args, **kwargs)

class UserRecords(LoginRequiredMixin, generic.ListView):
    model = EnrichmentRecordModel
    template_name = 'userrecords.html'
    context_object_name = 'object_list'

    login_url = '/login/'
    redirect_field_name = 'next'

    paginate_by = 4

    def get_queryset(self):

        user_records = EnrichmentRecordModel.objects.filter(
            user=self.request.user
        )

        return user_records

    def get_ordering(self):
        default_ordering = '-analysed_at'
        ordering_validation = ['-analysed_at', 'analysed_at']

        ordering = self.request.GET.get('ordering', default_ordering)

        if ordering != None and ordering not in ordering_validation:
            return default_ordering

        return ordering

class ResultFromArchive(generic.DetailView):

    slug_field = 'task_id'
    slug_url_kwarg = 'task_id'

    def get(self, request, *args, **kwargs):

            task_id = kwargs.get('task_id', None)

            obj = get_object_or_404(EnrichmentRecordModel, task_id=task_id)

            if not has_perm(request, obj):
                return HttpResponseForbidden()

            return JsonResponse(
                {
                    'complete': obj.complete,
                    'success': obj.success,
                    "progress": {
                        "pending": False,
                        "current": 100,
                        "total": 100,
                        "percent": 100
                    },
                    'result': json.load(obj.result)
                }
            )


class SearchRecordView(generic.FormView):
    template_name = 'getrecord.html'
    form_class = EnrichmentSearchForm

    def post(self, request, *args, **kwargs):

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.full_clean()

        if form.is_valid():

            task_id = form.instance.searched_task_id
            form.save()

            return HttpResponseRedirect(reverse('record', kwargs={'task_id': task_id}))

        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super(SearchRecordView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class RecordView(generic.DetailView):
    template_name = 'record.html'
    context_object_name = 'queryset'
    model = EnrichmentRecordModel
    slug_field = 'task_id'
    slug_url_kwarg = 'task_id'

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:

        task_id = kwargs.get('task_id', None)
        obj = get_object_or_404(EnrichmentRecordModel, task_id=task_id)

        if not has_perm(request, obj):
            return HttpResponseForbidden()

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['queryset'] = get_object_or_404(EnrichmentRecordModel, task_id=self.kwargs.get('task_id'))
        return context

class ResultView(generic.DetailView):
    template_name = 'progress.html'
    context_object_name = 'queryset'
    model = EnrichmentRecordModel
    slug_field = 'task_id'
    slug_url_kwarg = 'task_id'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        enrichment_record = get_object_or_404(EnrichmentRecordModel, task_id=self.kwargs.get('task_id', None))
        field = enrichment_record.enrichment_field
        field_dbs = get_selected_field_dbs(field)

        context.update({
            'task_id': self.kwargs.get('task_id', None),
            'field': field,
            'field_dbs': field_dbs
        })

        return context

class AnalysisFormView(generic.FormView):
    template_name = 'analysis.html'
    form_class = EnrichmentRecordForm

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.full_clean()

        if form.is_valid():

            form.instance.gene_list = form.cleaned_data.get('gene_list', None)
            form.instance.enrichment_field = form.cleaned_data.get('enrichment_field', None)
            form.instance.user = self.request.user if not self.request.user.is_anonymous else None
            form.instance.shareable = form.cleaned_data.get('shareable', None)
            form.instance.description = form.cleaned_data.get('description', None)

            gene_list_str = form.instance.gene_list
            enrichment_field = form.instance.enrichment_field

            result = enrichment_analysis.delay(gene_list_str, enrichment_field)

            form.instance.task_id = result.task_id

            form.save()

            return HttpResponseRedirect(reverse('analysis_progress', kwargs={'task_id': result.task_id}))

        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super(AnalysisFormView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class SignupForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password1', 'password2')

class SignupView(generic.CreateView):
    template_name = 'account/signup.html'
    form_class = SignupForm
    success_url = '/'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        valid = super(SignupView, self).form_valid(form)

        email = form.cleaned_data['email']
        password = form.cleaned_data['password1']

        user = authenticate(username=email, password=password)
        login(self.request, user)
        return valid

    def form_invalid(self, form):
        return super().form_invalid(form)

class UserLoginView(LoginView):
    template_name='account/login.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('/')
        return super().dispatch(request, *args, **kwargs)

def index(request):
    return render(request, 'landing.html')

def test(request):
    return render(request, 'errors/403.html')

def handler400(request, exception):
    context = {}
    response = render(request, "errors/400.html", context=context)
    response.status_code = 400
    return response


def handler403(request, exception):
    context = {}
    response = render(request, "errors/403.html", context=context)
    response.status_code = 403
    return response

def handler404(request, exception):
    context = {}
    response = render(request, "errors/404.html", context=context)
    response.status_code = 404
    return response


def handler500(request):
    context = {}
    response = render(request, "errors/500.html", context=context)
    response.status_code = 500
    return response