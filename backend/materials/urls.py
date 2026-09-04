from django.urls import path
from .views import (
    CourseMaterialListCreateView, CourseMaterialDetailView,
    MaterialFolderListCreateView, MaterialFolderDetailView,
    download_material, course_materials
)

urlpatterns = [
    # Materials
    path('materials/', CourseMaterialListCreateView.as_view(), name='material-list'),
    path('materials/<int:pk>/', CourseMaterialDetailView.as_view(), name='material-detail'),
    path('materials/<int:material_id>/download/', download_material, name='material-download'),
    path('courses/<int:course_id>/materials/', course_materials, name='course-materials'),
    
    # Folders
    path('folders/', MaterialFolderListCreateView.as_view(), name='folder-list'),
    path('folders/<int:pk>/', MaterialFolderDetailView.as_view(), name='folder-detail'),
]