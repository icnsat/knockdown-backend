from django.contrib import admin
from .models import TrainingSession, BigramStatistics
from django import forms

admin.site.register(TrainingSession)
# admin.site.register(BigramStatistics)


class BigramStatisticsForm(forms.ModelForm):
    bigram = forms.CharField(max_length=3, strip=False)

    class Meta:
        model = BigramStatistics
        fields = '__all__'


@admin.register(BigramStatistics)
class BigramStatisticsAdmin(admin.ModelAdmin):
    form = BigramStatisticsForm
