from django import template
from TuTz718.models import Category 

register = template.Library()

@register.inclusion_tag('cats.html')
def get_category_list(cat=None):
    return {'cats': Category.objects.all(), 'act_cat': cat}




@register.filter(name='addcls')
def addcss(value, arg):
    return value.as_widget(attrs={'class': arg})