from django import forms
from django.conf import settings
from shells.models import Page, Shell, Media, Widget
# from tinymce.widgets import TinyMCE


class PageAdminForm(forms.ModelForm):
    # Pull in the tinymce config options for admin views from global settings
    # attrs are the params for when tinymce is off, mce_attrs are for when it's on
    # body = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 40},mce_attrs=settings.TINYMCE_ADMIN_CONFIG))

    class Meta:
        model = Page

    def _media(self):
        js = ['/media/js/tinymce_filebrowser_callback.js','/media/js/tiny_mce/tiny_mce.js',]
        return forms.Media(js=js)

    media = property(_media)


class ShellForm(forms.ModelForm):

    class Meta:
        model = Shell
        exclude = ('project','slug')


class MediaForm(forms.ModelForm):

    title = forms.CharField(help_text='Not displayed on site; for your reference only.',error_messages={'required': 'Please enter a title for this media object.'})

    class Meta:
        model = Media
        exclude = ('page')


class WidgetForm(forms.ModelForm):

    class Meta:
        model = Widget
        exclude = ('page')


class PageForm(forms.ModelForm):
    '''
    Only fellows, not the public, can access the view containing this tinymce field. We don't provide a raw HTML editor
    (which makes it a bit safer), but we do consider them trusted editors, so we're not sanitizing the HTML submitted from
    this form. Besides, they can still use the media embedder to add arbitrary embed code, so sanitizing this would be moot
    anyway.
    '''
    # body = forms.CharField(widget=TinyMCE(attrs={'cols': 40, 'rows': 40},mce_attrs=settings.TINYMCE_DEFAULT_CONFIG))
    title = forms.CharField(error_messages={'required': 'Please enter a title for this page.'})

    class Meta:
        model = Page
        exclude = ('slug','shell','navorder')


