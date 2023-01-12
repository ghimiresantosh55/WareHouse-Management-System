from django.apps import AppConfig


class LogAppConfig(AppConfig):
    name = 'log_app'
    # def ready(self):
    #     import log_app.signals
# class TestsConfig(AppConfig):
#     def ready(self):
#         from .signals import pre_create_historical_record_callback
#         from simple_history.signals import pre_create_historical_record
#         pre_create_historical_record.connect(pre_create_historical_record_callback)