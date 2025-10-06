# forms.py
from django import forms

class DatasetForm(forms.Form):
    name = forms.CharField(label="Name", max_length=255)
    source_type = forms.ChoiceField(
        choices=[("", "Select"), ("api", "API"), ("file", "File"), ("manual", "Manual")],
        required=False
    )
    file_format = forms.ChoiceField(
        choices=[("", "Select"), ("csv", "CSV"), ("json", "JSON"), ("xlsx", "XLSX")],
        required=False
    )
    upload_file = forms.FileField(required=False)
    data_source_url = forms.URLField(required=False)
    date_start = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_end = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    is_realtime = forms.BooleanField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
