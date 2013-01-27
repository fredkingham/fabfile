from django import forms
from common import custom_fields
from django.forms import ModelForm
from mainPage.models import EventImage, Venue, Event
from preview_calculation import Regularity

regularity_choices = [(Regularity.HOURLY, 0), (Regularity.DAILY, 1), (Regularity.WEEKLY, 2), (Regularity.MONTHLY, 3)]


class DateLineForm(forms.Form):
    start_date = forms.DateField(input_formats=["%Y%m%d", "%d%b%Y"])
    end_date = forms.DateField(input_formats=["%Y%m%d", "%d%b%Y"])


class PreviewForm(forms.Form):
    what = forms.CharField(max_length=250, required=False)
    title = forms.CharField(max_length=100, required=False)
    when = forms.CharField()
    time = forms.CharField(required=False)
    venue = forms.CharField(required=False)
    repeat_event = forms.CharField(required=False)
    repeat_until = forms.CharField(required=False)
    invited = forms.CharField(required=False)


class EventCreatorForm(forms.Form):
    description = forms.CharField(max_length=250, required=False)
    title = forms.CharField(max_length=100)
    event_date = forms.DateField(required=False, input_formats=["%Y%m%d", "%d%b%Y"])
    event_time = custom_fields.FiggTimeField(required=False)
    event_venue = forms.CharField(required=False)
    invited = custom_fields.FiggArrayFromStringField(required=False)
    img = forms.ImageField(required=False)
    img_id = forms.IntegerField(required=False)
    public = forms.BooleanField(required=False)
    repeat_regularity = forms.ChoiceField(required=False, choices=regularity_choices)
    repeat_until = custom_fields.FiggDateField(required=False)


class EventEditorForm(forms.Form):
    description = forms.CharField(max_length=250, required=False)
    title = forms.CharField(max_length=100)
    event_date = forms.DateField(input_formats=["%Y%m%d", "%d%b%Y"])
    event_time = custom_fields.FiggTimeField(required=False)
    event_venue = forms.CharField(required=False)
    public = forms.BooleanField(required=False)
    event = forms.ModelChoiceField(queryset=Event.objects.all())
    invited = custom_fields.FiggArrayFromStringField(required=False)


class EventImgForm(ModelForm):
    class Meta:
        model = EventImage


class VenueForm(ModelForm):
    class Meta:
        model = Venue
        exclude = ('creator')

class EventQueryArgsValidation(forms.Form):
    start_date = forms.DateField(required=False, input_formats=["%Y%m%d", "%d%b%Y"])
    end_date = forms.DateField(required=False, input_formats=["%Y%m%d", "%d%b%Y"])
    start_key = forms.IntegerField(required=False)
    end_key = forms.IntegerField(required=False)
    cal = forms.CharField(max_length=100, required=False)
    tag = forms.CharField(max_length=100, required=False)
    series = forms.IntegerField(required=False)
    search_term = forms.CharField(max_length=250, required=False)

    def clean(self):
        cleaned_data = super(EventQueryArgsValidation, self).clean()
        start_date = cleaned_data.get("start_date")
        start_key = cleaned_data.get("start_key")
        end_date = cleaned_data.get("end_date")
        end_key = cleaned_data.get("end_key")
        if not start_date and not end_date and not start_key and not end_key:
            raise forms.ValidationError("no start or end field allowed")

        for key, value in cleaned_data.items():
            if value == None or value == "":
                del(cleaned_data[key])

        return cleaned_data
