from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30,
                               widget=forms.widgets.TextInput,
                               label='Username',
                               required=True)
    password1 = forms.CharField(max_length=30,
                                widget=forms.widgets.PasswordInput,
                                label="Password")
    password2 = forms.CharField(max_length=30,
                                widget=forms.widgets.PasswordInput,
                                label="Password (again)")
    fullname = forms.EmailField(max_length=50,
                                widget=forms.widgets.TextInput,
                                label='Full Name')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("You must confirm your password")
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match")
        return password2


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30,
                               widget=forms.widgets.TextInput,
                               label='Username',
                               required=True)
    password = forms.CharField(max_length=30,
                               widget=forms.widgets.PasswordInput,
                               label="Password")
