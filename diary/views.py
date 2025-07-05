from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, ListView, DeleteView
from taggit.models import Tag

from .forms import DiarySettingsForm, DiaryEntryForm
from .models import DiaryEntry, DiarySettings, CustomField


class HomePageView(TemplateView):
    """ Контроллер домашней страницы"""
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        # предполагалось, что я покажу пользователю, сколько у него записей в дневнике
        context = super().get_context_data(**kwargs)
        context["total_entries"] = DiaryEntry.objects.count()
        return context


class SettingsView(LoginRequiredMixin, UpdateView):
    """ Контроллер для настроек вида дневника"""
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
    """ Контроллер для создания новой записи дневника"""
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
    """ Контроллер для просмотра конкретной записи дневника"""
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
    """ Контроллер для обновления пользовательских полей дневника"""
    def post(self, request, *args, **kwargs):
        settings = get_object_or_404(DiarySettings, user=request.user)
        custom_fields = request.POST.getlist('custom_fields[]')
        settings.custom_fields_names = [f.strip() for f in custom_fields if f.strip()]
        settings.save()
        return JsonResponse({'status': 'ok'})


class DiaryEntryListView(LoginRequiredMixin, ListView):
    """ Контроллер для просмотра списка записей дневника"""
    model = DiaryEntry
    template_name = 'diary/entry_list.html'
    context_object_name = 'entries'
    paginate_by = 10

    def get_queryset(self):
        queryset = DiaryEntry.objects.filter(user=self.request.user)

        # Поиск по тексту
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(text__icontains=search_query)

        # Поиск по тегам
        tag_query = self.request.GET.get('tag')
        if tag_query:
            queryset = queryset.filter(tags__name__in=[tag_query])

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['tag_query'] = self.request.GET.get('tag', '')

        # Получаем все теги пользователя
        context['tags'] = Tag.objects.filter(
            diaryentry__user=self.request.user
        ).distinct()

        return context


class DiaryEntryUpdateView(LoginRequiredMixin, UpdateView):
    """ Контроллер для обновления записи дневника"""
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
    """ Контроллер для удаления записи дневника """
    model = DiaryEntry
    template_name = 'diary/entry_confirm_delete.html'
    success_url = reverse_lazy('diary:entry_list')
    context_object_name = 'entry'

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)
