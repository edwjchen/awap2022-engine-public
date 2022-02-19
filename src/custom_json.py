import json

from .structure import *
from .player import *

'''
Used for custom JSON encodings of our classes
'''
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Team):
            return obj.value
        # if isinstance(obj, PlayerInfo):
        #     return [obj.team, obj.money, obj.utility]
        if isinstance(obj, StructureType):
            return obj.value.id
        if isinstance(obj, Structure):
            return [obj.x, obj.y, obj.team, obj.type]
            # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
