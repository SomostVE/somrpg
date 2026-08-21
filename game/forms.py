from django import forms
from .models import Character


class CharacterCreateForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"maxlength": 40, "autocomplete": "off", "placeholder": "Adventurer name"})}
