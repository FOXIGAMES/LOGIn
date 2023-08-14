from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from myzloo.models import CustomUser, MusicTrack, myzloo_favorites

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('email', 'username')

class MusicTrackAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'album', 'genre', 'release_year', 'duration_seconds')
    search_fields = ('title', 'artist', 'album', 'genre', 'release_year')

class MyzlooFavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'track')
    list_filter = ('user', 'track')
    search_fields = ('user__username', 'track__title', 'track__artist')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(MusicTrack, MusicTrackAdmin)
admin.site.register(myzloo_favorites, MyzlooFavoritesAdmin)
