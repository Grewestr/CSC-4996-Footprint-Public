from django.shortcuts import redirect
import logging

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)

    def __call__(self, request):
        # Public, user, and admin URL definitions
        public_urls = ['/', '/login/', '/signup/', '/password_reset/']
        user_allowed_urls = [
            '/', '/dashboard/', '/logout/', '/profile/', '/change_password/', '/delete_email/',
            '/delete-upload/', '/check-status/', '/upload/', '/search_attributes1/',
            '/format_time_detected/', '/generate_detection_time_link/', '/edit_profile/'
        ]
        admin_allowed_urls = [
            '/', '/admin_dashboard/', '/logout/', '/profile/', '/update_account_status/',
            '/delete-upload/', '/check-status/', '/change_password/', '/delete_email/',
            '/upload/', '/dashboard/', '/format_time_detected/', '/generate_detection_time_link/', '/edit_profile/'
        ]


        # Get the role and uid from the session
        uid = request.session.get('uid')
        role = request.session.get('role')

        # Log the current request path, uid, and role
        self.logger.info(f"Processing request: path={request.path}, uid={uid}, role={role}")

        # Check for AJAX requests and allow them through
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.logger.info(f"Allowing AJAX request: {request.path}")
            return self.get_response(request)

        # Redirect unauthenticated users
        if not uid and request.path not in public_urls:
            self.logger.warning(f"Redirecting unauthenticated request: {request.path}")
            return redirect('login')

        # Handle role-based URL restrictions
        if role == 'user' and request.path not in user_allowed_urls:
            self.logger.warning(f"Redirecting user to dashboard: unauthorized path={request.path}")
            return redirect('dashboard')

        if role == 'admin' and not any(request.path.startswith(url) for url in admin_allowed_urls):
            self.logger.warning(f"Redirecting admin to admin_dashboard: unauthorized path={request.path}")
            return redirect('admin_dashboard')

        # Allow the request through if all conditions are met
        self.logger.info(f"Request allowed: path={request.path}")
        return self.get_response(request)
