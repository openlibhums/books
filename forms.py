from django import forms

from django_summernote.widgets import SummernoteWidget

from plugins.books import models


class BookForm(forms.ModelForm):

    class Meta:
        model = models.Book
        exclude = ('',)
        widgets = {
            'description': SummernoteWidget()
        }
