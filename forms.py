from django import forms
from django.forms import SelectMultiple
from django.template.loader import render_to_string
from django.utils.text import slugify

from django_summernote.widgets import SummernoteWidget

from plugins.books import models, files
from repository import models as repository_models


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
        exclude = ('keywords', 'publisher_notes', 'linked_repository_objects', 'contributors')
        widgets = {
            'description': SummernoteWidget(),
            'notes': SummernoteWidget(),
            'date_published': DateInput(),
            'date_embargo': DateInput(),
        }


class ContributorForm(forms.ModelForm):

    class Meta:
        model = models.Contributor
        fields = (
            'is_corporate',
            'corporate_name',
            'first_name',
            'middle_name',
            'last_name',
            'affiliation',
            'email',
            'bio',
            'headshot',
        )
        widgets = {
            'bio': SummernoteWidget(),
        }


class FormatForm(forms.ModelForm):

    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super(FormatForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.filename:
            self.fields['file'].required = False

    class Meta:
        model = models.Format
        exclude = ('book', 'filename')

    def save(self, commit=True, *args, **kwargs):
        save_format = super(FormatForm, self).save(commit=False)
        file = self.cleaned_data["file"]

        if file:
            filename = files.save_file_to_disk(file, save_format)
            save_format.filename = filename

        if commit:
            save_format.save()

        return save_format

    def clean(self):
        cleaned_data = self.cleaned_data

        return cleaned_data


class ChapterFormatForm(forms.ModelForm):

    file = forms.FileField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.filename:
            self.fields['file'].required = False

    class Meta:
        model = models.ChapterFormat
        exclude = ('chapter', 'filename')

    def save(self, commit=True, *args, **kwargs):
        chapter_format = super().save(commit=False)
        file = self.cleaned_data.get('file')

        if file:
            filename = files.save_file_to_disk(file, chapter_format)
            chapter_format.filename = filename

        if commit:
            chapter_format.save()

        return chapter_format


class ChapterForm(forms.ModelForm):

    contributors = forms.ModelMultipleChoiceField(
        queryset=models.Contributor.objects.none(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        items = kwargs.pop('items', None)
        super(ChapterForm, self).__init__(*args, **kwargs)
        self.fields['contributors'].widget = TableMultiSelect(items=items)
        # Set queryset from items
        pks = [row.get('object').pk for row in items if row.get('object')]
        self.fields['contributors'].queryset = models.Contributor.objects.filter(
            pk__in=pks,
        )
        # Set initial from existing ContributorLinks
        if self.instance and self.instance.pk:
            self.fields['contributors'].initial = list(
                models.ContributorLink.objects.filter(
                    chapter=self.instance,
                ).values_list('contributor_id', flat=True)
            )

    class Meta:
        model = models.Chapter
        fields = [
            'title',
            'description',
            'pages',
            'doi',
            'number',
            'date_embargo',
            'date_published',
            'sequence',
            'license_information',
            'custom_how_to_cite',
        ]

    def save(self, commit=True, book=None, *args, **kwargs):
        save_chapter = super(ChapterForm, self).save(commit=False)

        if book:
            save_chapter.book = book

        if commit:
            save_chapter.save()

        return save_chapter

    def save_chapter_contributors(self, chapter):
        selected_contributors = self.cleaned_data.get('contributors', [])
        existing_links = models.ContributorLink.objects.filter(chapter=chapter)

        # Remove links for contributors no longer selected
        existing_links.exclude(
            contributor__in=selected_contributors,
        ).delete()

        # Add links for newly selected contributors
        existing_contributor_ids = set(
            existing_links.values_list('contributor_id', flat=True)
        )
        next_order = (
            existing_links.order_by('-order').values_list(
                'order', flat=True,
            ).first() or 0
        ) + 1

        for contributor in selected_contributors:
            if contributor.pk not in existing_contributor_ids:
                models.ContributorLink.objects.create(
                    contributor=contributor,
                    chapter=chapter,
                    order=next_order,
                )
                next_order += 1


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


class PreprintSelectionForm(forms.Form):
    preprint_id = forms.ModelChoiceField(
        queryset=repository_models.Preprint.objects.none(),
        label="Select a Preprint",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        available_preprints = kwargs.pop('available_preprints', None)
        super().__init__(*args, **kwargs)
        if available_preprints is not None:
            self.fields['preprint_id'].queryset = available_preprints