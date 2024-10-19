# middleware.py

from django.shortcuts import redirect

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of public URLs that don't require authentication
        public_urls = ['/', '/login/', '/signup/','/example/','/password_reset/', '/test_search/','/results/','/generate_persons/','/demo_input/','/search_person/'] 

        # URLs accessible by regular users
        user_allowed_urls = ['/dashboard/','/logout/','/profile/','/change_password/','/delete_email/']

        # URLs accessible by admins
        admin_allowed_urls = ['/admin_dashboard/','/logout/','/approve_user/']

        # Get the role and uid from the session
        uid = request.session.get('uid')
        role = request.session.get('role')

        # If the user is not logged in (no uid in session)
        if not uid and request.path not in public_urls:
            # Redirect to login page if trying to access a protected page without being logged in
            return redirect('login')

        # If logged in as a user, check allowed URLs
        if role == 'user' and request.path not in user_allowed_urls:
            # Redirect regular users trying to access admin pages to the user dashboard
            return redirect('dashboard')

        # If logged in as an admin, check allowed URLs
        if role == 'admin':
            # Check if the path starts with any allowed admin URL
            if not any(request.path.startswith(url) for url in admin_allowed_urls):
                return redirect('admin_dashboard')

        # If all conditions are met, allow access to the requested page
        return self.get_response(request)