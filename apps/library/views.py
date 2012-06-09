# Create your views here.
from library.models import StandardFile, MimeType, FileShare
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from postman.models import Message, STATUS_PENDING, STATUS_ACCEPTED
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.models import Site


def listfiles(request,user_slug=None):
    """List files uploaded by or shared with a user."""
        
    # We either need a given user's library or the requesting user's
    # Example of Python conditional shorthand (alternative to if/else)
    u = User.objects.get(username=user_slug) if user_slug else request.user

    myfiles = StandardFile.objects.filter(added_by=u)
    shares = FileShare.objects.filter(shared_with=u)
    
    return render_to_response(
        'library/listfiles.html', 
        locals(), 
        context_instance=RequestContext(request)
        )


def showfile(request,file_id):
    """Display a single library file."""
    
    document = get_object_or_404(StandardFile,id=file_id)
    
    return render_to_response(
        'library/showfile.html', 
        locals(), 
        context_instance=RequestContext(request)
        )
        
def sharefile(request,file_id):
    """Share a file or collection with user's followers."""
    
    file = get_object_or_404(StandardFile,id=file_id)

    if request.method == "POST":

        sender = request.user.get_profile()
        followers = sender.followers.all()
        site = Site.objects.get(id=1) # Need this for link in email template. 
        
        
        for f in followers:
            # Create an individualized Postman message for each recipient
            body = render_to_string("library/share/email_body.txt", { 'recip': f, 'sender': sender, 'site': site, 'file': file })        
                    
            msg = Message.objects.create(
                subject = '%s has shared a file with you' % (sender),
                body = body,
                sender = request.user,
                recipient = f.user,
                moderation_status = STATUS_ACCEPTED, 
                )
            msg.notify_users(STATUS_PENDING,is_auto_moderated=True) # Send email to recips as well

            # Also create a FileShare record for each
            FileShare.objects.create(
                file=file,
                shared_with = f.user,
                )
            
        messages.success(request, "Message sent to %d followers!" % (followers.count())) # In-page messsages
        return HttpResponseRedirect(reverse('library_showfile',args=[file_id])) # Redirect to original image page

    
    return render_to_response(
        'library/sharefile.html', 
        locals(), 
        context_instance=RequestContext(request)
        )        

          
def add_files(request):
    """Add one or more files to your library."""

    # Needed for ajax handling of multiple files
    csrf_token = get_token(request)

    
    return render_to_response(
        'library/add_files.html', 
        locals(), 
        context_instance=RequestContext(request)
        )


def save_upload( uploaded, filename, raw_data ):
  ''' 
  raw_data: if True, uploaded is an HttpRequest object with the file being
            the raw post data 
            if False, uploaded has been submitted via the basic form
            submission and is a regular Django UploadedFile in request.FILES
  '''
  filename = settings.UPLOAD_STORAGE_DIR + "/" + filename 
  # print settings.MEDIA_ROOT
  # print settings.UPLOAD_STORAGE_DIR
  # print filename
  try:
    from io import FileIO, BufferedWriter
    with BufferedWriter( FileIO( filename, "wb" ) ) as dest:
      # if the "advanced" upload, read directly from the HTTP request 
      # with the Django 1.3 functionality
      if raw_data:
        foo = uploaded.read( 1024 )
        while foo:
          dest.write( foo )
          foo = uploaded.read( 1024 ) 
      # if not raw, it was a form upload so read in the normal Django chunks fashion
      else:
        for c in uploaded.chunks( ):
          dest.write( c )
      # got through saving the upload, report success
      return True
  except IOError:
    # could not open the file most likely
    pass
  return False
 
def ajax_upload( request ):
  if request.method == "POST":   
    if request.is_ajax( ):
      # the file is stored raw in the request
      upload = request
      is_raw = True
      # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
      try:
        filename = request.GET[ 'qqfile' ]
      except KeyError: 
        return HttpResponseBadRequest( "AJAX request not valid" )
    # not an ajax upload, so it was the "basic" iframe version with submission via form
    else:
      is_raw = False
      if len( request.FILES ) == 1:
        # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
        # ID based on a random number, so it cannot be guessed here in the code.
        # Rather than editing Ajax Upload to pass the ID in the querystring,
        # observer that each upload is a separate request,
        # so FILES should only have one entry.
        # Thus, we can just grab the first (and only) value in the dict.
        upload = request.FILES.values( )[ 0 ]
      else:
        raise Http404( "Bad Upload" )
      filename = upload.name
     
    # save the file
    success = save_upload( upload, filename, is_raw )
    
    # Create a corresponding StandardFile instance for this user
    mimetype = MimeType.objects.get(extension='jpg')
    newfile = StandardFile.objects.create(
        file = settings.LIBRARY_URL + "/" + filename,
        added_by = request.user,
        mimetype = mimetype,
        permissions = 'single',
    )
    
 
    # let Ajax Upload know whether we saved it or not
    import json
    ret_json = { 'success': success, }
    return HttpResponse( json.dumps( ret_json ) )    
