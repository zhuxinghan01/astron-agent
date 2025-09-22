from common.service.base import ServiceFactory
from common.service.settings.settings_service import SettingsService


class SettingsServiceFactory(ServiceFactory):

    def __init__(self):
        super().__init__(SettingsService)

    def create(self):
        setting_service = SettingsService()
        setting_service.sync_env_file_to_environ()
        return setting_service
