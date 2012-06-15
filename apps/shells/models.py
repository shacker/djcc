from django.db import models
from django.conf import settings
from shells import constants
from sorl.thumbnail.fields import ImageField
from django.db.models import FileField
from django.template.defaultfilters import slugify
import re



def get_shell_upload_path(instance, filename):
    """
    Clean the filename and determine the foldername to upload images and media to
    (which is the folder named for the current shell's slug)
    Calling instance will be a Page, Shell, or Media instance.
    """

    if isinstance(instance,Shell):
        folder = instance.slug

    if isinstance(instance,Page):
        folder = instance.shell.slug

    if isinstance(instance,Media):
        folder = instance.page.shell.slug

    # To keep filenames clean, take the first part of the filename and run it
    # through django's slugify function (if you run the whole filename through,
    # you lose the "." separator in the filename.)
    parts = str(filename).split(".")

    return 'upload/shells/' + folder + '/' + slugify(parts[0]) + '.' + parts[1]


class Palette(models.Model):
    """Define color palettes for use in shells. We don't enable palette editing for fellows."""
    title = models.CharField('Palette name', max_length=20)
    default_pal = models.NullBooleanField('Default Palette',unique=True,null=True,default=False,help_text='Only one palette can be set as the default - set others to Unknown.')
    bodycolor = models.CharField('Body background color',blank=True, max_length=6,help_text="Do not enter # symbols. Get hex codes from colorblender.com or similar.")
    contentareabgcolor = models.CharField('Content area background color',blank=True, max_length=6)
    textcolor = models.CharField('Text color',blank=True, max_length=6)
    divcolor = models.CharField('Upper/lower div color',blank=True, max_length=6)
    divtextcolor = models.CharField('Text in the upper/lower divs',blank=True, max_length=6)
    headlinecolor = models.CharField('Headline color',blank=True, max_length=6)
    linkcolor = models.CharField('Link color',blank=True, max_length=6)
    vlinkcolor = models.CharField('Visited link color',blank=True, max_length=6)

    def __unicode__(self):
      return self.title


class Shell(models.Model):
    title = models.CharField('Site Title',max_length=200)
    slug = models.SlugField(unique=True,help_text="To be used in the shell URL.",)
    description = models.TextField('Description',  help_text="Brief project summary (one or two sentences), used on KDMC listing pages.")
    icon = ImageField('Project Icon',upload_to=get_shell_upload_path, blank=True,null=True,  help_text='Represents the project as a whole, for use on KDMC listing pages. <br />Should be square, 300x300px, JPG or PNG.')
    bannerimg = ImageField('Banner image', max_length=200,blank=True, upload_to=get_shell_upload_path, help_text='Main banner image for project.  Should be exactly 960x140px, JPG or PNG.')
    palette = models.ForeignKey(Palette,null=True,blank=True,help_text='<a href="/shells/admin/palettes/" target="_blank"><strong>VIEW PALETTES</strong></a> :: If no palette is chosen from this list, a default palette will be used.')

    def __unicode__(self):
        return self.title

    def get_shell_home(self):
        # Determine which of this shell's pages should be the homepage
        # by grabbing the one with the lowest navorder. If multiple,
        # just use whatever the queryset returns first.
        pages = Page.objects.filter(shell=self).order_by('navorder')
        return pages[0]



class Page(models.Model):
    shell = models.ForeignKey(Shell)
    title = models.CharField(max_length=200, help_text="Headline for this page.")
    navorder = models.IntegerField("Nav order",blank=True, null=True,help_text="Order in which this page&apos;s icons will appear in project.")
    # is_home = models.BooleanField(default=False,help_text="Is this the homepage for this shell/project? <br />Only one page within a project can be set to be the homepage.")
    slug = models.SlugField(help_text="To be used in this page's URL.",)
    shownavlabel = models.BooleanField('Show Navigation Label',default=False,help_text="If your icon images do not have text, show link to this page as plain text.")
    disable_icon = models.BooleanField('Disable Nav Icon',default=False,help_text="With this box checked, the nav link to this page will be text-only.")
    icon = ImageField("Page Icon", max_length=200,  upload_to=get_shell_upload_path,  blank=True, null=True,help_text="215x125px image becomes navigation button pointing to this page. ")
    icon_alt = ImageField("Rollover Icon", max_length=200,  upload_to=get_shell_upload_path,  blank=True, null=True,help_text="Optional 215x125px image creates a rollover effect on the page icon. ")
    body = models.TextField(help_text='Main article. Insert media with this tag: {{media 23}} where 23 is the media object ID from below.')

    class Meta:
         unique_together = (("slug", "shell"),)

    def __unicode__(self):
        return self.title



class Media(models.Model):
    page = models.ForeignKey(Page)
    title = models.CharField(max_length=200,help_text="Required for shell system but not displayed on site." )
    type = models.CharField('Media type',max_length=6,choices=constants.MEDIA_TYPE_CHOICES,)
    file = FileField("File", max_length=200, upload_to=get_shell_upload_path, blank=True, null=True,help_text="Upload a video/image/swf, zipped slideshow, etc.")
    width = models.IntegerField('Width (in pixels)', blank=True, null=True,help_text='Optional override for width of this media. Works for everything but embeds.')
    height = models.IntegerField('Height (in pixels)', blank=True, null=True,help_text='Optional override for height of this media. Works for everything but embeds.')
    style = models.CharField('Media style',blank=True,max_length=16,choices=constants.MEDIA_STYLE_CHOICES,help_text="When used with images, will cause text to wrap around image (sets a CSS class).")
    poster_frame = ImageField("Poster frame for uploaded video", max_length=200, upload_to=get_shell_upload_path, blank=True, null=True,help_text="If available, displayed before uploaded video plays.<br />Does not apply to YouTube/Vimeo videos.")
    embed = models.CharField('Embed Code',max_length=4000,blank=True,help_text='Embeddable HTML for maps or externally hosted video.',)
    caption = models.CharField(max_length=255,null=True,blank=True,help_text="Optional. If present, will be displayed below media.")

    class Meta:
         verbose_name_plural = "Media"


    def __unicode__(self):
        return "%s :: %s" % (self.title, self.id)


class Widget(models.Model):
    page = models.ForeignKey(Page)
    title = models.CharField(max_length=200,help_text="Required for shell system, optionally displayed on site." )
    show_title = models.BooleanField('Show Widget Title',default=False,help_text="Should the title field above display above the widget?")
    code = models.TextField('Embed Code',blank=False,help_text='Embeddable HTML/Javascript from 3rd party. Max width 200px',)
    widgetorder = models.IntegerField("Widget order",blank=True, null=True,help_text="Order in which this page&apos;s widgets will appear in sidebar.")


    class Meta:
         verbose_name_plural = "Widgets"


    def __unicode__(self):
        return "%s :: %s" % (self.title, self.id)



