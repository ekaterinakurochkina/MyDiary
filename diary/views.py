from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from django.views.generic import ListView, DetailView, DeleteView, TemplateView

from .forms import DiaryEntryForm, CustomFieldForm, DiarySettingsForm
from .models import DiaryEntry, CustomField, DiarySettings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView

class DiarySettingsView(LoginRequiredMixin, UpdateView):
    model = DiarySettings
    form_class = DiarySettingsForm
    template_name = 'diary/settings.html'
    success_url = reverse_lazy('diary:entry_list')

    def get_object(self):
        obj, created = DiarySettings.objects.get_or_create(user=self.request.user)
        return obj

CustomFieldFormSet: type[BaseInlineFormSet] = inlineformset_factory(
    DiaryEntry,
    CustomField,
    form=CustomFieldForm,
    extra=1,
    can_delete=True
)
class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_entries"] = DiaryEntry.objects.count()
        return context

class DiaryEntryCreateView(CreateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = 'diary/diaryentry_form.html'
    success_url = reverse_lazy('diary:entry_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['custom_fields_formset'] = CustomFieldFormSet(self.request.POST)
        else:
            context['custom_fields_formset'] = CustomFieldFormSet()
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        context = self.get_context_data()
        custom_fields_formset = context['custom_fields_formset']

        self.object = form.save()  # Сохраняем основную запись

        if custom_fields_formset.is_valid():
            custom_fields_formset.instance = self.object
            custom_fields_formset.save()

        return super().form_valid(form)


class DiaryEntryUpdateView(UpdateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = 'diary/diaryentry_form.html'
    success_url = reverse_lazy('diary:entry_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['custom_fields_formset'] = CustomFieldFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['custom_fields_formset'] = CustomFieldFormSet(
                instance=self.object
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        custom_fields_formset = context['custom_fields_formset']

        self.object = form.save()

        if custom_fields_formset.is_valid():
            custom_fields_formset.instance = self.object
            custom_fields_formset.save()

        return super().form_valid(form)


class DiaryEntryListView(LoginRequiredMixin, ListView):
    model = DiaryEntry
    template_name = 'entry_list.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user).order_by('-created_at')


class DiaryEntryDetailView(LoginRequiredMixin, DetailView):
    model = DiaryEntry
    template_name = 'diary/entry_detail.html'
    context_object_name = 'entry'

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)


class DiaryEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = DiaryEntry
    template_name = 'diary/entry_confirm_delete.html'
    success_url = reverse_lazy('diary:entry_list')
    context_object_name = 'entry'

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)
