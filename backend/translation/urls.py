from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import TranslationAPIView, xml_translate

urlpatterns = [
    path("translate", TranslationAPIView.as_view()),
    path("translate-xml", xml_translate),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['xml'])