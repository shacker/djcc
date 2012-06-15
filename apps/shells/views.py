from shells.models import *
from shells.constants import *
from shells.functions import unzipper
from shells.forms import ShellForm, PageForm, MediaForm, WidgetForm
from django.template import RequestContext
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Count
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django.template.defaultfilters import slugify
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import sys, zipfile, os, os.path


# Needed for django_inlines, which replaces content strings
# like {{ media slug }} with appropriate embed code
# from django_inlines import inlines
# from tutorials.mediaobjects import *
# inlines.registry.register('media', ShellInline)



def shell_page(request,shell_slug=None,page_slug=None):
    # Shell slug will always be present. Page slug won't be if this is the homepage.
    # If Page slug is missing, the page to show is the one marked is_home for the current shell.
    shell = get_object_or_404(Shell,slug=shell_slug)
    shell2 = shell

    if page_slug:
        page = get_object_or_404(Page,slug=page_slug,shell__slug=shell_slug)
    else:
        try:
            page = shell.get_shell_home()
        except:
            page = None

    # Did they remember to select a palette? If not, give them the default palette.
    if shell.palette:
        palette = shell.palette
    else:
        palette = Palette.objects.get(default_pal=True)



    # Get related pages and widgets, in order
    related_pages = Page.objects.filter(shell=shell).order_by('navorder')
    widgets = Widget.objects.filter(page=page).order_by('widgetorder')

    return render_to_response('shells/shell_page.html',
        {
        'shell':shell,
        'palette':palette,
        'page':page,
        'related_pages':related_pages,
        'widgets':widgets,
        },
        context_instance = RequestContext(request),)



def shell_about(request,shell_slug=None):
    # Team members, etc. for this project

    shell = get_object_or_404(Shell,slug=shell_slug)
    members = shell.project.members.all().order_by('last_name')

    # Did they remember to select a palette? If not, give them the default palette.
    if shell.palette:
        palette = shell.palette
    else:
        palette = Palette.objects.get(default_pal=True)

    # Get related pages, in order
    related_pages = Page.objects.filter(shell=shell).order_by('navorder')

    return render_to_response('shells/shell_about.html',
        {
        'shell':shell,
        'members':members,
        'palette':palette,
        'related_pages':related_pages,
        },
        context_instance = RequestContext(request),)



def view_palettes(request):
    # Visualize all palettes in the system

    palettes = Palette.objects.all()

    return render_to_response('shells/palette_view.html',
        {
        'palettes':palettes,
        },
        context_instance = RequestContext(request),)



@permission_required('shells.change_shell')
def admin_index(request):
    '''
    Let fellows edit their own shells.
    List all shells the current fellow has permission to access.
    '''

    # Get all shells that belong to a project that has the current user listed as a member.
    # shells = Shell.objects.filter(project__members__in=[request.user,])
    shells = Shell.objects.all()

    return render_to_response('shells/admin_index.html',
        {
        'shells':shells,
        },
        context_instance = RequestContext(request),)



@permission_required('shells.change_shell')
def admin_shell(request,shell_slug):
    '''
    Edit attributes and pages for a particular shell.
    '''

    shell = get_object_or_404(Shell,slug=shell_slug)
    pages = Page.objects.filter(shell=shell).order_by('navorder')

    if request.POST:

        # Handle submission of the Shell Attributes form
        shellform = ShellForm(request.POST, request.FILES, instance=shell)

        if shellform.is_valid():
            # Don't commit the save until we've added in the fields we need to set
            shell.save()

            messages.success(request, "Cool. Shell attributes changed.")
            return HttpResponseRedirect(reverse('shells_admin_shell',args=[shell.slug]))

    else:
        shellform = ShellForm(instance=shell)

    return render_to_response('shells/admin_shell.html',
        locals(),
        context_instance = RequestContext(request),)





@permission_required('shells.change_shell')
def admin_new_page(request,shell_id):
    '''
    Add a new page to a shell
    '''
    shell = Shell.objects.get(id=shell_id)

    if request.POST:
        form = PageForm(request.POST, request.FILES)

        if form.is_valid():

            page = form.save(commit=False)
            page.slug = slugify(form.cleaned_data['title'])
            page.navorder = 99 # Put new page at the bottom of the list by default
            page.shell = shell
            page.save()

            messages.success(request, "New page added successfully.")
            return HttpResponseRedirect(reverse('shells_admin_page',args=[page.id]))
        else:
            messages.error(request, "The title and body fields cannot be empty!")

    else:
        form = PageForm()

    return render_to_response('shells/admin_page.html',
        locals(),
        context_instance = RequestContext(request),)



@permission_required('shells.change_shell')
def admin_edit_page(request,page_id):
    '''
    Edit particulars for a single page
    '''

    page = get_object_or_404(Page,id=page_id)

    if request.POST:

        # Handle submission of the Shell Attributes form
        form = PageForm(request.POST, request.FILES, instance=page)

        if form.is_valid():

            # Don't commit the save until we've added in the fields we need to set
            page.slug = slugify(form.cleaned_data['title'])
            page.save()

            messages.success(request, "Cool - page changed.")
            return HttpResponseRedirect(reverse('shells_admin_page',args=[page.id]))

    else:
        form = PageForm(instance=page)

    return render_to_response('shells/admin_page.html',
        locals(),
        context_instance = RequestContext(request),)




@permission_required('shells.change_shell')
def admin_delete_page(request, page_id=None):
  """
  If user has permission, let them delete this page
  """

  page = get_object_or_404(Page,id=page_id)

  # Check permission! Make sure user is in the group that owns this shell.
  if request.user in page.shell.project.members.all():
      page.delete()
      messages.success(request, "Page deleted.")
      return HttpResponseRedirect(reverse('shells_admin_shell',args=[page.shell.slug]))
  else:
      messages.error(request, "That page is not yours to delete!")
      return HttpResponseRedirect(reverse('accounts_profile'))


@permission_required('shells.change_shell')
def admin_delete_media(request, media_id=None):
  """
  If user has permission, let them delete this media object
  """
  media = get_object_or_404(Media,id=media_id)

  # Check permission! Make sure user is in the group that owns this shell.
  if request.user in media.page.shell.project.members.all():

      # If this media object has an attached file, try and delete that first,
      # then the media obj in the db
      fullpath = os.path.join(settings.MEDIA_ROOT,str(media.file))
      try:
          os.remove(fullpath)
      except:
          pass
      media.delete()
      messages.success(request, "Media object deleted.")
      return HttpResponseRedirect(reverse('shells_admin_shell',args=[media.page.shell.slug]))
  else:
      messages.error(request, "That media is not yours to delete!")
      return HttpResponseRedirect(reverse('accounts_profile'))


@permission_required('shells.change_shell')
@csrf_exempt
def reorder_pages(request):
    """
    Handle page re-ordering from JQuery drag/drop in shells/admin_shell.html
    """

    newpagelist = request.POST.getlist('pagetable[]')

    # Items arrive in order, so all we need to do is increment up from one, saving
    # "i" as the new priority for the current object.
    i = 1
    for t in newpagelist:
        newitem = Page.objects.get(pk=t)
        newitem.navorder = i
        newitem.save()
        i = i + 1

    # All views must return an httpresponse of some kind ... without this we get
    # error 500s in the log even though things look peachy in the browser.
    return HttpResponse(status=201)


@permission_required('shells.change_shell')
def reorder_widgets(request):
    """
    Handle widget re-ordering from JQuery drag/drop in shells/admin_page.html
    """

    newwidgetlist = request.POST.getlist('widgettable[]')

    # Items arrive in order, so all we need to do is increment up from one, saving
    # "i" as the new priority for the current object.
    i = 1
    for t in newwidgetlist:
        newitem = Widget.objects.get(pk=t)
        newitem.widgetorder = i
        newitem.save()
        i = i + 1

    # All views must return an httpresponse of some kind ... without this we get
    # error 500s in the log even though things look peachy in the browser.
    return HttpResponse(status=201)



@permission_required('shells.change_shell')
def admin_new_media(request,page_id):
    '''
    Add a new media object to a page
    '''
    page = Page.objects.get(id=page_id)

    if request.POST:
        form = MediaForm(request.POST, request.FILES)

        if form.is_valid():

            media = form.save(commit=False)
            media.page = page
            media.save()

            # Check whether a .zip file was uploaded. If so, unzip it in place
            unzipper(media)

            messages.success(request, "New media object added.")
            return HttpResponseRedirect(reverse('shells_admin_page',args=[page_id]))
        else:
            messages.error(request, "Some required fields are empty")

    else:
        form = MediaForm()

    return render_to_response('shells/admin_media.html',
        locals(),
        context_instance = RequestContext(request),)



@permission_required('shells.change_shell')
def admin_edit_media(request,media_id):
    '''
    Edit particulars for a single media object
    '''

    media_obj = get_object_or_404(Media,id=media_id)

    if request.POST:

        form = MediaForm(request.POST, request.FILES, instance=media_obj)

        if form.is_valid():
            media_obj.save()

            # Check whether a .zip file was uploaded. If so, unzip it in place
            unzipper(media_obj)

            messages.success(request, "Media object modified.")
            # return HttpResponseRedirect(reverse('shells_admin_page',args=[media_obj.page.id]))


    else:
        form = MediaForm(instance=media_obj)

    return render_to_response('shells/admin_media.html',
        locals(),
        context_instance = RequestContext(request),)




@permission_required('shells.change_shell')
def admin_new_widget(request,page_id):
    '''
    Add a new widget to a page
    '''
    page = Page.objects.get(id=page_id)

    if request.POST:
        form = WidgetForm(request.POST)

        if form.is_valid():
            widget = form.save(commit=False)
            widget.page = page
            widget.save()

            messages.success(request, "New widget added.")
            return HttpResponseRedirect(reverse('shells_admin_page',args=[page_id]))
        else:
            messages.error(request, "Some required fields are empty")

    else:
        form = WidgetForm()

    return render_to_response('shells/admin_widget.html',
        locals(),
        context_instance = RequestContext(request),)



@permission_required('shells.change_shell')
def admin_edit_widget(request,widget_id):
    '''
    Edit particulars for a single widget
    '''

    widget_obj = get_object_or_404(Widget,id=widget_id)

    if request.POST:

        form = WidgetForm(request.POST, request.FILES, instance=widget_obj)

        if form.is_valid():
            widget_obj.save()

            messages.success(request, "Widget modified.")
            # return HttpResponseRedirect(reverse('shells_admin_page',args=[media_obj.page.id]))

    else:
        form = WidgetForm(instance=widget_obj)

    return render_to_response('shells/admin_widget.html',
        locals(),
        context_instance = RequestContext(request),)



@permission_required('shells.change_shell')
def admin_delete_widget(request, widget_id=None):
  """
  If user has permission, let them delete this widget object
  """
  widget = get_object_or_404(Widget,id=widget_id)

  # Check permission! Make sure user is in the group that owns this shell.
  if request.user in widget.page.shell.project.members.all():

      widget.delete()
      messages.success(request, "Widget object deleted.")
      return HttpResponseRedirect(reverse('shells_admin_shell',args=[widget.page.shell.slug]))
  else:
      messages.error(request, "That widget is not yours to delete!")
      return HttpResponseRedirect(reverse('accounts_profile'))

