from django import forms
from resources.models import Schedule, Resource, Reservation, TIME_CHOICES
import datetime

class ResourceForm(forms.ModelForm):
    
    class Meta:
        model = Resource


class ReservationForm(forms.ModelForm):
    """
    A custom form for reservations.

    Also does custom validation.
    """
    
    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        if not self.is_bound:
            if self.instance.id:
                self.fields['start_date'].initial = self.instance.start_when.date()
                self.fields['end_date'].initial = self.instance.end_when.date()
                self.fields['start_time'].initial = self.instance.start_when.time()
                self.fields['end_time'].initial = self.instance.end_when.time()

    start_date = forms.DateField(label='Start Date')
    end_date = forms.DateField(label='End Date')
    start_time = forms.ChoiceField( label='Start Time', choices=TIME_CHOICES,)
    end_time = forms.ChoiceField( label='End Time',  choices=TIME_CHOICES,)
    #schedule = forms.ModelChoiceField(
    #                queryset=Schedule.objects.all(),
    #                widget=forms.HiddenInput)
    resource = forms.ModelChoiceField(
                    queryset=Resource.objects.all(),
                    widget=forms.HiddenInput)
    start_when = forms.DateTimeField(widget=forms.HiddenInput, required=False)
    end_when = forms.DateTimeField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Reservation
        fields = ('start_date','start_time', 'end_date', 'end_time', 
                  'summary', 'resource','start_when','end_when')

    def clean(self):
        # Get all the data from the form
        cleaned_data = self.cleaned_data
        resource = cleaned_data.get("resource")
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")
        summary = cleaned_data.get("summary")

        # this is defined if we are editing an instance
        reservation = None
        if self.instance.id:
            reservation = self.instance

        if not (end_date and start_date):
            raise forms.ValidationError('Please include a start and end date.')

        if not summary:
            raise forms.ValidationError('Please include a summary.')

        # convert string to datetime
        start_time = datetime.time(*[int(n) for n in start_time.split(':')])
        end_time = datetime.time(*[int(n) for n in end_time.split(':')])
        start_when = datetime.datetime.combine(start_date,start_time)
        end_when = datetime.datetime.combine(end_date,end_time)
        
        if end_when <= start_when:
            raise forms.ValidationError('Oops, end date/time must be after start date/time.')

        cleaned_data['start_when'] = start_when
        cleaned_data['end_when'] = end_when

        conflicts = Reservation.objects.get_conflicts(
                        resource, 
                        start_when, 
                        end_when, 
                        reservation=reservation)

        if conflicts:
            msg = ', '.join([str(c) for c in conflicts])
            raise forms.ValidationError(
                'Sorry, there are conflicts with other reservations: %s' % msg)

        return cleaned_data

