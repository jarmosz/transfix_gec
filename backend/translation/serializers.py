from rest_framework import serializers

LANGUAGE_CHOICES = [('pl', 'Polish')]

class TranslationSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=20000, min_length = 1)
    language = serializers.ChoiceField(choices=LANGUAGE_CHOICES)