from django.contrib import admin
from .models import ObjectSf, Tests, Testing, TestJournal, Settings, ActionLog


admin.site.register(ObjectSf)
admin.site.register(Tests)
admin.site.register(Testing)
admin.site.register(TestJournal)
admin.site.register(Settings)
admin.site.register(ActionLog)