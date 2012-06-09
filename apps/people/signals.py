from django.conf import settings



def create_profile(sender, instance, signal, created, **kwargs):
    """When user is created also create a profile."""
    from people.models import Profile
    if created:
        Profile(user = instance).save()



def story_added(sender, instance, signal, created, **kwargs):
    """When story is submitted, generate mail to webmaster."""
    
    if settings.DEBUG:
        return None

    from people.models import Story
    from django.contrib.sites.models import Site
    from django.template.loader import render_to_string
    from django.core.mail import EmailMessage
    
    story = Story.objects.get(pk=instance.id)
    site = Site.objects.get(id=1) # Need this for link in email template. Jschool's site ID in settings is 1.
    
    recipients = ['webmaster@journalism.berkeley.edu', 'sredd@berkeley.edu',]
    email_subject = render_to_string("tools/stories/storynew-subject.txt", { 's': story })                    
    email_body_txt = render_to_string("tools/stories/storynew-body.txt", { 's': story, 'site': site, })        

    msg = EmailMessage(email_subject, email_body_txt, story.profile.user.email, recipients)
    msg.send(fail_silently=False)
