from django.contrib import admin

import plugins.books.models as models


@admin.register(models.BookSetting)
class BookSettingAdmin(admin.ModelAdmin):
    list_display = ('book_page_title',)


@admin.register(models.Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'number', 'book', 'pages', 'doi')
    list_filter = ('book',)
    search_fields = ('title', 'book__title', 'doi')
    raw_id_fields = ('book',)
    filter_horizontal = ('contributors',)


@admin.register(models.BookAccess)
class BookAccessAdmin(admin.ModelAdmin):
    list_display = ('book', 'chapter', 'type', 'format', 'country', 'accessed')
    list_filter = ('book', 'type', 'format', 'country')
    search_fields = ('book__title', 'chapter__title')


@admin.register(models.Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher_name', 'date_published', 'is_open_access')
    list_filter = ('is_open_access', 'peer_reviewed', 'date_published', 'category')
    search_fields = ('title', 'subtitle', 'publisher_name', 'isbn', 'doi')
    raw_id_fields = ('category',)
    filter_horizontal = ('keywords', 'publisher_notes', 'linked_repository_objects')


@admin.register(models.Contributor)
class ContributorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'book', 'affiliation', 'sequence')
    list_filter = ('book',)
    search_fields = ('first_name', 'last_name', 'affiliation', 'email')
    raw_id_fields = ('book',)


@admin.register(models.Format)
class FormatAdmin(admin.ModelAdmin):
    list_display = ('title', 'book', 'sequence')
    list_filter = ('book',)
    search_fields = ('title', 'filename')
    raw_id_fields = ('book',)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_title')
    search_fields = ('name', 'slug')


@admin.register(models.BookPreprint)
class BookPreprintAdmin(admin.ModelAdmin):
    list_display = ('book', 'preprint', 'order')
    list_filter = ('book',)
    raw_id_fields = ('book', 'preprint')


@admin.register(models.KeywordBook)
class KeywordBookAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'book', 'order')
    list_filter = ('book',)
    search_fields = ('keyword__word',)
    raw_id_fields = ('keyword', 'book')


@admin.register(models.KeywordChapter)
class KeywordChapterAdmin(admin.ModelAdmin):
    list_display = ('keyword', 'chapter', 'order')
    list_filter = ('chapter',)
    search_fields = ('keyword__word',)
    raw_id_fields = ('keyword', 'chapter')


@admin.register(models.PublisherNote)
class PublisherNoteAdmin(admin.ModelAdmin):
    list_display = ('note',)
    search_fields = ('note',)
