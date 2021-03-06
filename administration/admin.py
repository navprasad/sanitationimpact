from django.contrib import admin
from administration.models import Admin, Problem, ProblemCategory, Toilet, UserProfile

admin.site.register(Admin)


class ProblemAdmin(admin.ModelAdmin):
    list_filter = ('category',)

admin.site.register(Problem, ProblemAdmin)

admin.site.register(ProblemCategory)
admin.site.register(Toilet)
admin.site.register(UserProfile)
