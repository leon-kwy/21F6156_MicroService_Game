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
    def find_by_template(cls, template, limit, offset):
        res = RDBService.find_by_template(template, limit, offset)
        return res

    @classmethod
    def create(cls, create_data):
        res = RDBService.create("GameInfo", "Game", create_data)
        return res

    @classmethod
    def update(cls, ID, update_data):
        res = RDBService.update( ID, update_data)
        return res

    @classmethod
    def insert(cls, select_data, update_data):
        res = RDBService.insert(select_data, update_data)
        return res

    @classmethod
    def delete(cls, template):
        res = RDBService.delete("GameInfo", "Game", template)
        return res
