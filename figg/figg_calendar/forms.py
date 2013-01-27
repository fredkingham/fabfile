from django import forms
from django.contrib.auth.models import User
from mainPage.models import EventSeries, Tag, Venue


class SelectCalendarForm(forms.Form):
    #tag = forms.CharField(max_length=50, required=False)
    tag = forms.ModelChoiceField(queryset=Tag.objects.all(), required=False)
    venue = forms.ModelChoiceField(queryset=Venue.objects.all(), to_field_name="name", required=False)
    cal = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    series = forms.ModelChoiceField(queryset=EventSeries.objects.all(), required=False)
    add = forms.BooleanField(initial=False, required=False)

class Tracking(forms.Form):
    cal = forms.ModelChoiceField(queryset=User.objects.all(), to_field_name="username", required=False)

class RelatedTags(forms.Form):
    venue = forms.ModelChoiceField(queryset=Venue.objects.all(), to_field_name="name", required=False)
    cal = forms.ModelChoiceField(queryset=User.objects.all(), to_field_name="username", required=False)
    series = forms.ModelChoiceField(queryset=EventSeries.objects.all(), required=False)

    def clean(self):
        cleaned_data = super(RelatedTags, self).clean()

        if not cleaned_data.get("venue") and not cleaned_data.get("cal") and not cleaned_data.get("series"):
            raise forms.ValidationError("no look up field passed in")

        return cleaned_data

class TrackingQueryForm(forms.Form):
    tag = forms.ModelChoiceField(queryset=Tag.objects.all(), to_field_name="name", required=False)
    venue = forms.ModelChoiceField(queryset=Venue.objects.all(), to_field_name="name", required=False)
    cal = forms.ModelChoiceField(queryset=User.objects.all(), to_field_name="username", required=False)
    series = forms.ModelChoiceField(queryset=EventSeries.objects.all(), required=False)

    def clean(self):
        cleaned_data = super(TrackingQueryForm, self).clean()
        tag = cleaned_data.get("tag")
        venue = cleaned_data.get("venue")
        cal = cleaned_data.get("cal")
        series = cleaned_data.get("series")

        if not tag and not venue and not cal and not series:
            raise forms.ValidationError("no look up field passed in")

        return cleaned_data
