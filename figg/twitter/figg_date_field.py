from django import forms
from twitter import data_extract
from datetime import date, time

class FiggDateField(forms.DateField):
    def to_python(self, value):
        potential = data_extract.extract_text(value, today = None)

        if potential:
            return potential[0]

class FiggTimeField(forms.TimeField):
    def to_python(self, value):
        if value:
            return data_extract.get_time(value)


class FiggArrayFromStringField(forms.CharField):
    def to_python(self, value):
        value = super(forms.CharField, self).to_python(value)
        if value:
            return value.split(",")


