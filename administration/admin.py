from django.contrib import admin
from administration.models import Admin, Problem, ProblemCategory, Toilet

admin.site.register(Admin)
admin.site.register(Problem)
admin.site.register(ProblemCategory)
admin.site.register(Toilet)
