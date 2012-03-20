from django.contrib.admin import *
from sorl.thumbnail.admin import AdminImageMixin

class ModelAdmin(AdminImageMixin, ModelAdmin):
	class Media:
		js = ['/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js', '/static/grappelli/tinymce_setup/tinymce_setup.js', ]

class TabularInline(AdminImageMixin, TabularInline):
	pass

class StackedInline(AdminImageMixin, StackedInline):
	pass

class SortableModelAdmin(ModelAdmin):
	list_display = ('__unicode__', 'order', )
	list_editable = ['order',]

	class Media:
		js = ['/static/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js', '/static/grappelli/tinymce_setup/tinymce_setup.js', '/static/grappelli/sortable.js', ]
