from django import forms 
from .models import User , Post , Comment
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth import get_user_model
# from django.contrib.auth.forms import UserCreationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=250 , required=True)
    password = forms.CharField(max_length=250 , required=True , widget=forms.PasswordInput)

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=20 , widget=forms.PasswordInput , label='password')
    password2 = forms.CharField(max_length=20 , widget=forms.PasswordInput , label='password')

    class Meta:
        model = User
        fields = ['username' , 'first_name' , 'last_name', 'email' , 'phone' , 'date_of_birth' , 'bio' , 'photo' , 'job']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('پسورد ها مطابقت ندارند !')
        return cd['password2']
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('phone already exists!')
        return phone
    
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username' , 'first_name' , 'last_name' , 'email' , 'phone' , 'date_of_birth' , 'bio' , 'photo' , 'job']

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if User.objects.exclude(id=self.instance.id).filter(phone=phone).exists():
            raise forms.ValidationError('phone already exists!')
        return phone

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(id=self.instance.id).filter(username=username).exists():
            raise forms.ValidationError('username already exists !')
        return username
    


class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ("پیشنهاد" , "پیشنهاد"),
        ("انتقاد" , "انتقاد"),
        ("گزارش" , "گزارش"),
    )
    message = forms.CharField(widget=forms.Textarea , required=True)
    name = forms.CharField(max_length=250 , required=True , widget=forms.TextInput(attrs={'class':'name' , 'placeholder':'name ...'}))
    email = forms.EmailField(label='E-mail')
    phone = forms.CharField(max_length=11 , required=True)
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone : 
            if not phone.isnumeric():
                raise forms.ValidationError('شماره تلفن عددی نیست !')
            else :
                return phone
            

class PostForm(forms.ModelForm):
    image = forms.ImageField()
    class Meta:
        model = Post
        fields = ['description' , 'tags']

    
    def clean_description(self):
        description = self.cleaned_data['description']
        if description:
            if len(description) < 2 :
                raise forms.ValidationError('توضیح بسیار کوتاهی است .')
            else:
                return description
 


class SearchForm(forms.Form):
    query = forms.CharField()


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name' , 'body']
        widgets = {
            'body' : forms.TextInput(attrs={
                'placeholder' : 'body ...',
                'class' : 'comment-body',
            }),
            'name' : forms.TextInput(attrs={
                'placeholder' : 'name ...',
                'class' : 'comment-name',
            }),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name)<3:
                raise forms.ValidationError('نام کوتاه است !')
            else:
                return name
            

class EmailPostForm(forms.Form):
    # name = forms.CharField(max_length=25)
    to = forms.EmailField()
    # comments = forms.CharField(required=False, widget=forms.Textarea)
            


