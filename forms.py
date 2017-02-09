from django import forms

from plugins.books import models


class BookForm(forms.ModelForm):

    class Meta:
        model = models.Book
        exclude = ('',)