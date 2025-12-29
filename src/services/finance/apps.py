from django.apps import AppConfig


class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'src.services.finance'
    verbose_name = 'Finance & Membership'

    def ready(self):
        import src.services.finance.signals  # noqa