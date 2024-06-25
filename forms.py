from django import forms
from django.forms import SelectMultiple
from django.template.loader import render_to_string
from django.utils.text import slugify

from django_summernote.widgets import SummernoteWidget

from plugins.books import models, files


class DateInput(forms.DateInput):
    input_type = 'date'


class MonthInput(forms.DateInput):
    input_type = 'month'


class TableMultiSelect(SelectMultiple):
    def __init__(self, *args, **kwargs):
        items = kwargs.pop('items')
        super(TableMultiSelect, self).__init__(*args, **kwargs)
        self.items = items
        self.queryset = self.get_queryset()

    def get_queryset(self):
        pks = [row.get('object', None).pk for row in self.items if row.get('object', None)]
        return models.Contributor.objects.filter(pk__in=pks)

    def render(self, name, value, attrs=None, choices=(), renderer=None):
        value_for_template = [int(val) for val in value] if value else None
        context = {
            'items': self.items,
            'name': name,
            'value': value_for_template,
        }
        return render_to_string(
            'books/forms/table_mult_select.html',
            context,
        )


class BookForm(forms.ModelForm):

    class Meta:
        model = models.Book
        exclude = ('keywords', 'publisher_notes')
        widgets = {
            'description': SummernoteWidget(),
            'date_published': DateInput(),
            'date_embargo': DateInput(),
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

    file = forms.FileField()

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


class ChapterForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        items = kwargs.pop('items', None)
        super(ChapterForm, self).__init__(*args, **kwargs)
        self.fields['contributors'].widget = TableMultiSelect(items=items)
        self.fields['contributors'].required = False

    file = forms.FileField(required=False)

    class Meta:
        model = models.Chapter
        exclude = ('book', 'filename', 'keywords', 'publisher_notes')

    def save(self, commit=True, book=None, *args, **kwargs):
        save_chapter = super(ChapterForm, self).save(commit=False)

        if book:
            save_chapter.book = book

        file = self.cleaned_data["file"]
        if file:
            filename = files.save_file_to_disk(file, save_chapter)
            save_chapter.filename = filename

        if commit:
            save_chapter.save()

        return save_chapter


class DateForm(forms.Form):
    start_date = forms.DateField(widget=DateInput())
    end_date = forms.DateField(widget=DateInput())


class MonthForm(forms.Form):
    start_month = forms.DateField(widget=MonthInput())
    end_month = forms.DateField(widget=MonthInput())


class CategoryForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = (
            'name',
            'description',
            'display_title',
            'chapter_name',
            'chapter_name_plural',
            'buy_button_text',
        )
        widgets = {
            'description': SummernoteWidget,
        }

    def save(self, commit=True):
        save_category = super(CategoryForm, self).save(commit=False)
        save_category.slug = slugify(save_category.name)

        if commit:
            save_category.save()

        return save_category
