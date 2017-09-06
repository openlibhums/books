from django import forms

from django_summernote.widgets import SummernoteWidget

from plugins.books import models, files


class BookForm(forms.ModelForm):

    class Meta:
        model = models.Book
        exclude = ('',)
        widgets = {
            'description': SummernoteWidget()
        }


class ContributorForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        book = kwargs.pop('book', None)
        super(ContributorForm, self).__init__(*args, **kwargs)

        self.fields['sequence'].initial = book.get_next_contributor_sequence()

    class Meta:
        model = models.Contributor
        exclude = ('book',)


class FormatForm(forms.ModelForm):

    file = forms.FileField(required=True)

    class Meta:
        model = models.Format
        exclude = ('book', 'filename')

    def save(self, commit=True, *args, **kwargs):
        save_format = super(FormatForm, self).save(commit=False)
        file = self.cleaned_data["file"]
        filename = files.save_file_to_disk(file, save_format)
        save_format.filename = filename

        if commit:
            save_format.save()

        return save_format

    def clean(self):
        cleaned_data = self.cleaned_data

        return cleaned_data

