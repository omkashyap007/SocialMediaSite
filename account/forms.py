from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate , login
from account.models import Account

class RegistrationForm(forms.Form) : 
    email = forms.EmailField(max_length = 255 ,  help_text = "Required Field")
    username = forms.CharField(
        max_length = 255 , help_text = "Required Field" , 
        widget = forms.TextInput(
            attrs = {
                "id" : "id_username" , 
                "class" : "form-control" , 
                "autocomplete" : False ,
            }
        )
    )
    password1 = forms.CharField(
        max_length = 30 ,
        help_text = "Required Field",
        widget = forms.PasswordInput(
            attrs = {
                "id" : "id_password" ,
                "class" : "form-control" , 
                "autocomplete" : False , 
            }  
        ),
        required = True , 
        )
    password2 = forms.CharField(
        max_length = 30 , 
        help_text = "Required Field" ,
        widget = forms.PasswordInput(
            attrs = {
                "id":  "id_password_confirm" , 
                "class" : "form-control" , 
                "autocomplete" : False , 
            }
        )
    )
    
    class Meta : 
        fields = ["email" , "username" , "password1" , "password2"]
        
    def clean_email(self) : 
        email = self.cleaned_data.get("email").lower()
        
        try : 
            account = Account.objects.get(email = email)
        except Exception as e : 
            return email
        raise forms.ValidationError("The email '{}' already exist !".format(email))
    
    def clean_username(self) :
        username = self.cleaned_data.get("username")
        
        try : 
            account = Account.objects.get(username = username)
        except Exception as e : 
            return username
        raise forms.ValidationError("The username '{}' already exists !".format(username))
    
    def clean_password1(self) : 
        password1 = self.cleaned_data.get("password1") 
        
        if not password1 : 
            raise forms.ValidationError("Kindly enter the Password !") 
        
        if len(password1) > 30 : 
            raise forms.ValidationError("The length of password cannot be greater than 30 !")
        return password1 
    def clean_password2(self) :
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if not password1 : 
            raise forms.ValidationError("Kindly enter the password !")

        if password1  and password2 and not password1 == password2 : 
            raise forms.ValidationError("The two password Fields do not match !")
        
        return password2    
    
    def save(self) : 
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password1")
        
        user = Account.objects.create_user(
            username = username , 
            email = email , 
            password = password ,
        )
        user.save()
        return user

class LoginForm(forms.Form): 
    email = forms.EmailField(
        max_length = 100 ,
        widget = forms.EmailInput(
            attrs = {
                "placeholder" : "Your Email here !" , 
                "id" : "inputEmail" , 
                "class" : "form-control" ,
                "name" : "email" , 
                "autofocus" : True , 
            }
        ) ,
        required = True , 
    )
    
    password = forms.CharField(
        max_length = 30 , 
        widget = forms.PasswordInput(
            attrs = {
                "placeholder" : "Your password here !" , 
                "id" : "inputPassword" , 
                "class" : "form-control" , 
                "name" : "password" , 
                
            }
        ),
        required = True , 
    )
    
    class Meta : 
        fields = "__all__"
        
        
    def clean_email(self) :
        email = self.cleaned_data.get("email")
        
        try : 
            user = Account.objects.get(email = email)
        except : 
            user = None
            
        if not user : 
            raise forms.ValidationError("No user with this email !")
        
        return email
    
    
    def clean_password(self) : 
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        
        if not password : 
            raise forms.ValidationError("Kindly enter the password !") 
        
        try : 
            account = Account.objects.get(email = email)
            print(account)
        except : 
            account = None

        return password
    

    def save(self , request): 
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        user = authenticate(email = email , password = password )
        
        if not user : 
            return None
        if user : 
            login(request , user)
            return user
        
class AccountUpdateForm(forms.ModelForm) : 
    class Meta : 
        model = Account
        fields = ["username" , "email" , "profile_image", "hide_email"] 
        
    def clean_email(self) : 
        email = self.cleaned_data.get("email").lower()
        
        try : 
            account = Account.objects.exclude(pk=self.instance.pk).get(email = email)
        except Account.DoesNotExist :
            return email
        raise forms.ValidationError("Email '{}' is already taken !".format(email))
    
    def clean_username(self): 
        username = self.cleaned_data.get("username")
        
        try : 
            account = Account.objects.exclude(pk=self.instance.pk).get(username = username)
        except Account.DoesNotExist:
            return username
        
        raise forms.ValidationError("Username '{}' is already taken !".format(username) ) 
    
    def save(self , commit = True) : 
        account = super(AccountUpdateForm , self).save(commit = False)
        account.username = self.cleaned_data.get("username")
        account.email = self.cleaned_data.get("email")
        account.profile_image = self.cleaned_data.get("profile_image")
        account.hide_email = self.cleaned_data.get("hide_email")
        
        if commit : 
            account.save()
        return account
    
    