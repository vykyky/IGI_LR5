from django import forms
from main.models import Doctor, DoctorSchedule
from django.utils import timezone

class CartAddServiceForm(forms.Form):
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.none(),  # пустой по умолчанию, потом заполним
        label="Врач",
        required=True
    )

    available_time = forms.ModelChoiceField(
        queryset=DoctorSchedule.objects.none(),
        label="Время приёма",
        required=True
    )


    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput
    )

    def __init__(self, *args, **kwargs):
        service = kwargs.pop('service', None)
        super().__init__(*args, **kwargs)

        if service:
            self.fields['doctor'].queryset = Doctor.objects.filter(services=service).distinct()

        if 'doctor' in self.data:
            try:
                doctor_id = int(self.data.get('doctor'))
                self.fields['available_time'].queryset = DoctorSchedule.objects.filter(
                    doctor_id=doctor_id,
                    start_time__gte=timezone.now()
                )
            except (ValueError, TypeError):
                pass
        elif self.initial.get('doctor'):
            doctor = self.initial['doctor']
            self.fields['available_time'].queryset = DoctorSchedule.objects.filter(
                doctor=doctor,
                start_time__gte=timezone.now()
            )
