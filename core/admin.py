from django.contrib import admin
from .models import *
from django.utils.html import format_html, format_html_join

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id','name','username', 'email', 'phone_number', 'country')
    search_fields = ('name','username', 'email', 'phone_number')
    list_filter = ('country','name',)
    list_per_page = 10

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id','name','abbreviation', 'dialing_code', 'iso')
    search_fields = ('name','abbreviation','iso')
    list_per_page = 10
    list_filter = ('name',)
    

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'content_type', 'object_id', 'path', 'extension', 'size', 'type', 'display_file')
    search_fields = ('id', 'content_type', 'object_id', 'path', 'extension', 'size', 'type')
    list_per_page = 10
    list_filter = ('type', 'extension')

    def display_file(self, obj):
        file_url = settings.MEDIA_URL + obj.path
        file_extension = obj.extension.lower()
        
        if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="margin-right:10px;"/></a>',
                file_url, file_url
            )
        elif file_extension in ['mp4', 'webm', 'ogg']:
            return format_html(
                '<a href="{}" target="_blank"><video width="50" height="50" controls style="margin-right:10px;"><source src="{}" type="video/{}">Your browser does not support the video tag.</video></a>',
                file_url, file_url, file_extension
            )
        else:
            return format_html('<a href="{}" target="_blank">{}</a>', file_url, "Ver archivo")

    display_file.short_description = 'Archivo'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id','following_user','followed_user')
    search_fields = ('following_user__username','followed_user__username')
    list_per_page = 10
    list_filter = ('following_user', 'followed_user')

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id','name','description')
    search_fields = ('name',)
    list_per_page = 10
    list_filter = ('name',)

@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('id','content_type','object_id','content_object','user')
    search_fields = ('user__username',)
    list_per_page = 10
    list_filter = ('content_type',)

@admin.register(TypePost)
class TypePostAdmin(admin.ModelAdmin):
    list_display = ('id','name','description')
    search_fields = ('name',)
    list_per_page = 10
    list_filter = ('name',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id','content_type','object_id','content_object','user','observation')
    search_fields = ('user__username','observation')
    list_per_page = 10
    list_filter = ('content_type', 'user')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_body', 'user', 'type_post', 'status', 'display_media', 'count_files', 'count_reports', 'count_reactions')
    search_fields = ('body', 'user__username')
    list_per_page = 10
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

    def display_media(self, obj):
        media_html = []
        for file in obj.files.all():
            file_url = settings.MEDIA_URL + file.path

            if file.extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
                media_html.append(
                    format_html(
                        '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="margin-right:10px;"/></a>',
                        file_url, file_url
                    )
                )
            elif file.extension.lower() in ['mp4', 'webm', 'ogg']:
                media_html.append(
                    format_html(
                        '<a href="{}" target="_blank"><video width="50" height="50" controls style="margin-right:10px;"><source src="{}" type="video/{}">Your browser does not support the video tag.</video></a>',
                        file_url, file_url, file.extension
                    )
                )
        
        return format_html_join('', "{}", ((media,) for media in media_html)) or "No Media"
    
    display_media.short_description = 'Media'

    def truncated_body(self, obj):
        max_length = 40
        body_text = obj.body
        if len(body_text) > max_length:
            truncated = body_text[:max_length] + '...'
            return format_html(
                '<span class="truncated-text">{}</span><a href="#" onclick="toggleText(this, event)"></a><span class="full-text" style="display:none;">{}</span>',
                truncated, body_text
            )
        return body_text
    
    truncated_body.short_description = 'Body'


@admin.register(Share)
class ShareAdmin(admin.ModelAdmin):
    list_display = ('id','user','post')
    search_fields = ('user__username','post__body')
    list_per_page = 10
    list_filter = ('user', 'post')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'truncated_body', 'post', 'user', 'status', 'display_media', 'count_files', 'count_reports', 'count_reactions')
    search_fields = ('body', 'user__username', 'post__body')
    list_per_page = 10
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

    def display_media(self, obj):
        media_html = []
        for file in obj.file.all():
            file_url = settings.MEDIA_URL + file.path
            if file.extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
                media_html.append(
                    format_html(
                        '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="margin-right:10px;"/></a>',
                        file_url, file_url
                    )
                )
            elif file.extension.lower() in ['mp4', 'webm', 'ogg']:
                media_html.append(
                    format_html(
                        '<a href="{}" target="_blank"><video width="50" height="50" controls style="margin-right:10px;"><source src="{}" type="video/{}">Your browser does not support the video tag.</video></a>',
                        file_url, file_url, file.extension
                    )
                )
        
        return format_html_join('', "{}", ((media,) for media in media_html)) or "No Media"
    
    display_media.short_description = 'Media'

    def truncated_body(self, obj):
        max_length = 40 
        body_text = obj.body
        if len(body_text) > max_length:
            truncated = body_text[:max_length] + '...'
            return format_html(
                '<span class="truncated-text">{}</span><a href="#" onclick="toggleText(this, event)"></a><span class="full-text" style="display:none;">{}</span>',
                truncated, body_text
            )
        return body_text
    
    truncated_body.short_description = 'Body'


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'user', 'archive', 'status', 'display_media', 'count_files', 'count_reports', 'count_reactions')
    search_fields = ('content', 'user__username')
    list_per_page = 10
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

    def display_media(self, obj):
        media_html = []
        for file in obj.file.all():
            file_url = settings.MEDIA_URL + file.path
            if file.extension.lower() in ['jpg', 'jpeg', 'png', 'gif']:
                media_html.append(
                    format_html(
                        '<a href="{}" target="_blank"><img src="{}" width="50" height="50" style="margin-right:10px;"/></a>',
                        file_url, file_url
                    )
                )
            elif file.extension.lower() in ['mp4', 'webm', 'ogg']:
                media_html.append(
                    format_html(
                        '<a href="{}" target="_blank"><video width="50" height="50" controls style="margin-right:10px;"><source src="{}" type="video/{}">Your browser does not support the video tag.</video></a>',
                        file_url, file_url, file.extension
                    )
                )

        return format_html_join('', "{}", ((media,) for media in media_html)) or "No Media"
    
    display_media.short_description = 'Media'
