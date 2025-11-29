from django import template
from django.urls import reverse, resolve

register = template.Library()

@register.simple_tag(takes_context=True)
def get_back_url(context):
    """Get the appropriate back URL based on current page"""
    request = context['request']
    path = request.path
    
    # Define back navigation rules
    back_urls = {
        # Course related
        '/courses/': '/',
        '/dashboard/': '/',
        
        # Default to home
    }
    
    # Check if path matches any pattern
    for pattern, back_url in back_urls.items():
        if path.startswith(pattern):
            return back_url
    
    # Default: use browser back
    return None

@register.simple_tag(takes_context=True)
def show_back_button(context):
    """Determine if back button should be shown"""
    request = context['request']
    path = request.path
    
    # Don't show on these pages
    hide_on = ['/', '/login/', '/register/', '/logout/']
    
    return path not in hide_on
