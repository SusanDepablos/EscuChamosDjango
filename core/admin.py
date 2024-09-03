from django.contrib import admin
from .models import *
from django.utils.html import format_html

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','name','username', 'email', 'phone_number', 'country')
    search_fields = ('name','username', 'email', 'phone_number')
    list_filter = ('country','name',)

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id','name','abbreviation', 'dialing_code', 'iso')
    search_fields = ('name','abbreviation','iso')
    list_filter = ('iso',)
    

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id', 'path', 'extension', 'size', 'type', 'display_file')
    search_fields = ('id', 'content_type', 'object_id', 'path', 'extension', 'size', 'type')
    list_filter = ('type', 'extension')

    def display_file(self, obj):
        file_url = settings.MEDIA_URL + obj.path
        if obj.extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="margin-right:10px;"/>{}</a>',
                file_url, file_url, "Ver archivo"
            )
        else:
            return format_html('<a href="{}" target="_blank">{}</a>', file_url, "Ver archivo")

    display_file.short_description = 'Archivo'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id','following_user','followed_user')
    search_fields = ('following_user__username','followed_user__username')
    list_filter = ('following_user', 'followed_user')

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id','name','description')
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('id','content_type','object_id','content_object','user')
    search_fields = ('user__username',)
    list_filter = ('content_type',)

@admin.register(TypePost)
class TypePostAdmin(admin.ModelAdmin):
    list_display = ('id','name','description')
    search_fields = ('name',)
    list_filter = ('name',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id','content_type','object_id','content_object','user','observation')
    search_fields = ('user__username','observation')
    list_filter = ('content_type', 'user')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'body', 'user', 'type_post', 'status', 'count_files', 'count_reports', 'count_reactions')
    search_fields = ('body', 'user__username')
    list_filter = ('type_post', 'status', 'user')

    def count_files(self, obj):
        return obj.files.count()
    count_files.short_description = 'Archivos'

    def count_reports(self, obj):
        return obj.reports.count()
    count_reports.short_description = 'Reportes'

    def count_reactions(self, obj):
        return obj.reactions.count()
    count_reactions.short_description = 'Reacciones'


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('id','user','post')
    search_fields = ('user__username','post__body')
    list_filter = ('user', 'post')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'body', 'post', 'user', 'status', 'count_files', 'count_reports', 'count_reactions')
    search_fields = ('body', 'user__username', 'post__body')
    list_filter = ('status', 'user', 'post')

    def count_files(self, obj):
        return obj.file.count()
    count_files.short_description = 'Archivos'

    def count_reports(self, obj):
        return obj.reports.count()
    count_reports.short_description = 'Reportes'

    def count_reactions(self, obj):
        return obj.reactions.count()
    count_reactions.short_description = 'Reacciones'


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'user', 'archive', 'status', 'count_files', 'count_reports', 'count_reactions')
    search_fields = ('content', 'user__username')
    list_filter = ('status', 'user')

    def count_files(self, obj):
        return obj.file.count()
    count_files.short_description = 'Archivos'

    def count_reports(self, obj):
        return obj.reports.count()
    count_reports.short_description = 'Reportes'

    def count_reactions(self, obj):
        return obj.reactions.count()
    count_reactions.short_description = 'Reacciones'

