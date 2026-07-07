from django.urls import path

from . import views

# Public patterns (mounted at api/v1/kb/)
public_urlpatterns = [
    path('entries/', views.PublicKnowledgeListView.as_view(), name='kb-public-list'),
    path('entries/<slug:slug>/', views.PublicKnowledgeDetailView.as_view(), name='kb-public-detail'),
]

# Admin patterns (mounted at api/v1/admin/kb/)
admin_urlpatterns = [
    path('entries/', views.AdminKnowledgeListCreateView.as_view(), name='kb-admin-list-create'),
    path('entries/<uuid:pk>/', views.AdminKnowledgeDetailView.as_view(), name='kb-admin-detail'),
    path('entries/<uuid:pk>/publish/', views.AdminKnowledgePublishView.as_view(), name='kb-admin-publish'),
    path('entries/<uuid:pk>/unpublish/', views.AdminKnowledgeUnpublishView.as_view(), name='kb-admin-unpublish'),
    path('entries/<uuid:pk>/archive/', views.AdminKnowledgeArchiveView.as_view(), name='kb-admin-archive'),
    path('entries/<uuid:pk>/restore/', views.AdminKnowledgeRestoreView.as_view(), name='kb-admin-restore'),
]

# Default export: combined (for backward compat if both mounts use the same file)
urlpatterns = public_urlpatterns + admin_urlpatterns
