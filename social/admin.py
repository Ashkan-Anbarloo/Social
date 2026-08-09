from django.contrib import admin
from .models import User , Post , Comment , Image , Contact ,Ticket
from django.contrib.auth.admin import UserAdmin
from django.core.mail import send_mail
# Register your models here.

class ImageInline(admin.TabularInline):
    model = Image
    extra = 0


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ['username' , 'phone' , 'first_name' , 'last_name']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information' , {'fields':('date_of_birth','bio','photo','job','phone')}),
    )


def make_deactivation(modeladmin , request , queryset):
    result = queryset.update(active=False)
    modeladmin.message_user(request , f"{result} post were rejected")

make_deactivation.short_description = 'DeActive'
#----------------------------------------------------------
def make_Activation(modeladmin , request , queryset):
    result = queryset.update(active=True)
    modeladmin.message_user(request , f"{result} post were Actived")

make_Activation.short_description = 'Active'

#----------------------------------------------------------
def status_report(modeladmin , request , queryset):
    report_data = {post.description: post.active for post in queryset}
    
    subject = "گزارش وضعیت پست‌ها"
    message = "در ادامه وضعیت پست‌های مورد نظر ارسال می‌گردد:\n\n"
    for key, value in report_data.items():
        message += f"{key} -> {value}\n"
    
    send_mail(
        subject,
        message,
        'ashkanbyo@gmail.com',
        [request.user.email],
        fail_silently=False,
    )
    modeladmin.message_user(request, "گزارش با موفقیت به ایمیل شما ارسال شد.")
status_report.short_description = 'ارسال گزارش وضعیت به ایمیل'

#----------------------------------------------------------
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author' , 'description' , 'created']
    ordering = ['created']
    list_filter = ['created' , 'author']
    search_fields = ['description']
    inlines = [ImageInline]
    actions = [make_deactivation , make_Activation , status_report]



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post' , 'name' , 'created']
    list_filter = ['created' , 'updated']
    search_fields = ['name' , 'body']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['post' , 'created']


admin.site.register(Contact)


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'created_at')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'created_at')
    fields = ('name', 'email', 'phone', 'subject', 'message', 'answer', 'created_at')
    