from django.urls import path

from .views import (
    # DiarySettingsView,
    DiaryEntryListView,
    # DiaryEntryDetailView,
    # DiaryEntryCreateView,
    DiaryEntryUpdateView,
    DiaryEntryDeleteView,
    HomePageView,
    SettingsView,
    DiaryEntryCreateView,
    DiaryEntryDetailView,
    UpdateCustomFieldsView
)

app_name = 'diary'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    # path('settings/', DiarySettingsView.as_view(), name='settings'),
    path('list/', DiaryEntryListView.as_view(), name='entry_list'),
    # path('create/', DiaryEntryCreateView.as_view(), name='entry_create'),
    # path('<int:pk>/', DiaryEntryDetailView.as_view(), name='entry_detail'),
    path('<int:pk>/update/', DiaryEntryUpdateView.as_view(), name='entry_update'),
    path('<int:pk>/delete/', DiaryEntryDeleteView.as_view(), name='entry_confirm_delete'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('entries/create/', DiaryEntryCreateView.as_view(), name='entry_create'),
    path('entries/<int:pk>/', DiaryEntryDetailView.as_view(), name='entry_detail'),
    path('update-custom-fields/', UpdateCustomFieldsView.as_view(), name='update_custom_fields'),
]
