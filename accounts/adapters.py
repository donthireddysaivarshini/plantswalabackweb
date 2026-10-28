from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialApp

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom SocialAccountAdapter to gracefully resolve SocialApp.
    Prevents MultipleObjectsReturned if both database and settings.py APPS exist.
    """
    def get_app(self, request, provider, client_id=None):
        apps = self.list_apps(request, provider=provider, client_id=client_id)
        if len(apps) > 1:
            # 1. Match by client_id if provided
            if client_id:
                for app in apps:
                    if getattr(app, 'client_id', None) == client_id:
                        return app
            # 2. Prefer app with valid non-empty client_id and secret
            valid_apps = [a for a in apps if getattr(a, 'client_id', None) and getattr(a, 'secret', None)]
            if valid_apps:
                return valid_apps[0]
            # 3. Fallback to first non-hidden app
            visible_apps = [app for app in apps if not getattr(app, 'settings', {}).get("hidden")]
            if visible_apps:
                return visible_apps[0]
            return apps[0]
        elif len(apps) == 0:
            raise SocialApp.DoesNotExist(f"No SocialApp found for provider '{provider}'")
        return apps[0]
