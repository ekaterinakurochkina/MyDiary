from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView, DeleteView

from .forms import DiarySettingsForm, DiaryEntryForm
from .models import DiaryEntry, DiarySettings, CustomField


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_entries"] = DiaryEntry.objects.count()
        return context


class SettingsView(LoginRequiredMixin, UpdateView):
    template_name = 'diary/settings.html'
    form_class = DiarySettingsForm
    success_url = reverse_lazy('diary:settings')

    def get_object(self, queryset=None):
        obj, created = DiarySettings.objects.get_or_create(user=self.request.user)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_fields'] = self.object.custom_fields_names or []
        return context

    def form_valid(self, form):
        # Обработка кастомных полей
        custom_fields = self.request.POST.getlist('custom_fields')
        form.instance.custom_fields_names = [f.strip() for f in custom_fields if f.strip()]
        return super().form_valid(form)


class DiaryEntryCreateView(LoginRequiredMixin, CreateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = 'diary/entry_form.html'
    success_url = reverse_lazy('diary:entry_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = DiaryEntry(user=self.request.user)
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        settings = get_object_or_404(DiarySettings, user=self.request.user)
        initial['targets'] = settings.default_targets
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = get_object_or_404(DiarySettings, user=self.request.user)

        # Создаем список словарей с именами полей и пустыми значениями
        custom_fields = [{'name': name, 'value': ''} for name in settings.custom_fields_names]

        context.update({
            'custom_fields': custom_fields,
            'show_targets': settings.show_targets,
            'show_tags': settings.show_tags,
            'is_update': False  # Явно указываем, что это создание
        })
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)

        settings = get_object_or_404(DiarySettings, user=self.request.user)
        for field_name in settings.custom_fields_names:
            value = self.request.POST.get(f'custom_{field_name}', '').strip()
            if value:
                CustomField.objects.create(
                    entry=self.object,
                    name=field_name,
                    value=value
                )

        return response


class DiaryEntryDetailView(LoginRequiredMixin, DetailView):
    model = DiaryEntry
    template_name = 'diary/entry_detail.html'
    context_object_name = 'entry'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['custom_fields'] = self.object.custom_fields.all()
        return context


@method_decorator(require_POST, name='dispatch')
class UpdateCustomFieldsView(LoginRequiredMixin, TemplateView):
    def post(self, request, *args, **kwargs):
        settings = get_object_or_404(DiarySettings, user=request.user)
        custom_fields = request.POST.getlist('custom_fields[]')
        settings.custom_fields_names = [f.strip() for f in custom_fields if f.strip()]
        settings.save()
        return JsonResponse({'status': 'ok'})


class DiaryEntryListView(LoginRequiredMixin, ListView):
    model = DiaryEntry
    template_name = 'entry_list.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user).order_by('-created_at')


class DiaryEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = DiaryEntry
    form_class = DiaryEntryForm
    template_name = 'diary/entry_form.html'
    context_object_name = 'entry'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = get_object_or_404(DiarySettings, user=self.request.user)

        # Получаем текущие значения кастомных полей
        existing_fields = {field.name: field.value for field in self.object.custom_fields.all()}

        # Создаем список всех кастомных полей с их значениями
        custom_fields = []
        for field_name in settings.custom_fields_names:
            custom_fields.append({
                'name': field_name,
                'value': existing_fields.get(field_name, '')
            })

        context.update({
            'custom_fields': custom_fields,
            'show_targets': settings.show_targets,
            'show_tags': settings.show_tags,
            'is_update': True  # Явно указываем, что это редактирование
        })
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        settings = get_object_or_404(DiarySettings, user=self.request.user)

        # Обновляем кастомные поля
        self.object.custom_fields.all().delete()  # Удаляем старые
        for field_name in settings.custom_fields_names:
            value = self.request.POST.get(f'custom_{field_name}', '').strip()
            if value:
                CustomField.objects.create(
                    entry=self.object,
                    name=field_name,
                    value=value
                )

        return response

    def get_success_url(self):
        return reverse_lazy('diary:entry_detail', kwargs={'pk': self.object.pk})


class DiaryEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = DiaryEntry
    template_name = 'diary/entry_confirm_delete.html'
    success_url = reverse_lazy('diary:entry_list')
    context_object_name = 'entry'

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)
