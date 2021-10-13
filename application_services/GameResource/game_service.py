from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService as RDBService

# data schema: GameInfo
# table_name: Game
class GameResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def find_by_template(cls, template):
        res = RDBService.find_by_template("GameInfo", "Game", template)
        return res

    @classmethod
    def create(cls, create_data):
        res = RDBService.create("GameInfo", "Game", create_data)
        return res

    @classmethod
    def update(cls, select_data, update_data):
        res = RDBService.update("GameInfo", "Game", select_data, update_data)
        return res

    @classmethod
    def delete(cls, template):
        res = RDBService.delete("GameInfo", "Game", template)
        return res

    @classmethod
    def find_by_type(cls, template):
        res = RDBService.find_by_type("GameInfo", "Game", template)
        return res

    @classmethod
    def find_by_dev(cls, template):
        res = RDBService.find_by_dev("GameInfo", "Game", template)
        return res

