from enum import Enum
from .player import *

class StructureInfo:
    def __init__(self, id, name, cost, can_build):
        self.id = id
        self.name = name
        self.cost = cost
        self.can_build = can_build

'''
Enum class for different structure types

Fields
-----
id - id number of structure type
name - string description of structure type
cost - cost to build structure type
can_build - flag for if the structure can be built by players

Methods
-----
get_cost() - returns cost of structure type
get_can_build() - returns if structure type can be built
'''


class StructureType(Enum):

    GENERATOR = StructureInfo(
        id=0,
        name="Generator",
        cost=1000,
        can_build=False
    )
    ROAD = StructureInfo(
        id=1,
        name="Road",
        cost=10,
        can_build=True
    )
    TOWER = StructureInfo(
        id=2,
        name="Tower",
        cost=250,
        can_build=True
    )
    # TRANSFORMER = StructureInfo(
    #     id=3,
    #     name="Transformer",
    #     cost=50,
    #     can_build=True
    # )

    def get_base_cost(self):
        return self.value.cost

    def get_can_build(self):
        return self.value.can_build

    def get_id(self):
        return self.value.id


    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return f"{self.name}"


'''
Class containing information about a single structure

Fields
-----
struct_type - the type of structure (StructureInfo class)

'''
class Structure:
    @classmethod
    def make_copy(self, s):
        if s is None:
            return None
        return Structure(s.type, s.x, s.y, s.team)


    def __init__(self, struct_type, x, y, team):
        self.x = x
        self.y = y
        self.team = team
        self.type = struct_type


    def get_cost(self, passability):
        return self.type.get_base_cost() * passability


    def __str__(self):
        return f"[{self.type.name} {str(self.team)} {(self.x, self.y)}]"

    def __repr__(self):
        return f"[{self.type.name} {str(self.team)} {(self.x, self.y)}]"


#
#
# class Generator(Structure):
#     def __init__(self, x, y, team):
#         super().__init__(StructureType.GENERATOR, x, y, team)
#
#
# class Road(Structure):
#     def __init__(self, x, y, team):
#         super().__init__(StructureType.ROAD, x, y, team)
#
#
# class Transformer(Structure):
#     def __init__(self, x, y, team):
#         super().__init__(StructureType.TRANSFORMER, x, y, team)
#
#
# class Tower(Structure):
#     def __init__(self, x, y, team):
#         super().__init__(StructureType.TOWER, x, y, team)
#
#
# class Preserve(Structure):
#     def __init__(self, x, y, team):
#         super().__init__(StructureType.PRESERVE, x, y, team)
