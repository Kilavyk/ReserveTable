from django import forms
from .models import Booking
from datetime import date


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['table', 'booking_date', 'time_slot', 'guests_count', 'special_requests']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date', 'min': date.today()}),
            'special_requests': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Укажите дополнительные пожелания (необязательно)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table'].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get('table')
        guests_count = cleaned_data.get('guests_count')

        if table and guests_count and guests_count > table.max_guests:
            raise forms.ValidationError(
                f'Количество гостей ({guests_count}) превышает максимальную вместимость столика ({table.max_guests}).'
            )

        return cleaned_data
