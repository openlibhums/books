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


class ContributorForm(forms.ModelForm):

    class Meta:
        model = models.Contributor
        exclude = ('book',)


class FormatForm(forms.ModelForm):

    class Meta:
        model = models.Format
        exclude = ('book', 'filename')
