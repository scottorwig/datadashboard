from django.contrib import admin
from apps.disciplineform.models import Accounts, Student, Staff, Incident, DisciplineAction

admin.site.register(Accounts)
admin.site.register(Student)
admin.site.register(Staff)
admin.site.register(Incident)
admin.site.register(DisciplineAction)