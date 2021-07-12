import logging
from typing import Set

logger = logging.getLogger("Hollow Knight")

from .Locations import lookup_name_to_id
from .Items import item_table
from .Regions import create_regions
from .Rules import set_rules
from .Options import hollow_knight_options

from BaseClasses import Region, Entrance, Location, MultiWorld, Item
from ..AutoWorld import World

class HKWorld(World):
    game: str = "Hollow Knight"
    options = hollow_knight_options
    item_names: Set[str] = frozenset(item_table)
    location_names: Set[str] = frozenset(lookup_name_to_id)

    def generate_basic(self):
        # Link regions
        self.world.get_entrance('Hollow Nest S&Q', self.player).connect(self.world.get_region('Hollow Nest', self.player))

        # Generate item pool
        pool = []
        for item_name, item_data in item_table.items():
            item = self.create_item(item_name)

            if item_data.type == "Event":
                event_location = self.world.get_location(item_name, self.player)
                self.world.push_item(event_location, item, collect=False)
                event_location.event = True
                event_location.locked = True
                if item.name == "King's_Pass":
                    self.world.push_precollected(item)
            elif item_data.type == "Cursed":
                if self.world.CURSED[self.player]:
                    pool.append(item)
                else:
                    # fill Focus Location with Focus and add it to start inventory as well.
                    event_location = self.world.get_location(item_name, self.player)
                    self.world.push_item(event_location, item)
                    event_location.event = True
                    event_location.locked = True

            elif item_data.type == "Fake":
                pass
            elif item_data.type in not_shufflable_types:
                location = self.world.get_location(item_name, self.player)
                self.world.push_item(location, item, collect=False)
                location.event = item.advancement
                location.locked = True
            else:
                target = option_to_type_lookup[item.type]
                shuffle_it = getattr(self.world, target)
                if shuffle_it[self.player]:
                    pool.append(item)
                else:
                    location = self.world.get_location(item_name, self.player)
                    self.world.push_item(location, item, collect=False)
                    location.event = item.advancement
                    location.locked = True
                    logger.debug(f"Placed {item_name} to vanilla for player {self.player}")

        self.world.itempool += pool


    def set_rules(self):
        set_rules(self.world, self.player)


    def create_regions(self):
        create_regions(self.world, self.player)


    def generate_output(self):
        pass  # Hollow Knight needs no output files


    def fill_slot_data(self): 
        slot_data = {}
        for option_name in self.options:
            option = getattr(self.world, option_name)[self.player]
            slot_data[option_name] = int(option.value)
        return slot_data

    def create_item(self, name: str) -> Item:
        item_data = item_table[name]
        return HKItem(name, item_data.advancement, item_data.id, item_data.type, self.player)

def create_region(world: MultiWorld, player: int, name: str, locations=None, exits=None):
    ret = Region(name, None, name, player)
    ret.world = world
    if locations:
        for location in locations:
            loc_id = lookup_name_to_id.get(location, 0)
            location = HKLocation(player, location, loc_id, ret)
            ret.locations.append(location)
    if exits:
        for exit in exits:
            ret.exits.append(Entrance(player, exit, ret))

    return ret


class HKLocation(Location):
    game: str = "Hollow Knight"

    def __init__(self, player: int, name: str, address=None, parent=None):
        super(HKLocation, self).__init__(player, name, address, parent)


class HKItem(Item):
    game = "Hollow Knight"

    def __init__(self, name, advancement, code, type, player: int = None):
        super(HKItem, self).__init__(name, advancement, code, player)
        self.type = type


not_shufflable_types = {"Essence_Boss"}

option_to_type_lookup = {
    "Root": "RandomizeWhisperingRoots",
    "Dreamer": "RandomizeDreamers",
    "Geo": "RandomizeGeoChests",
    "Skill": "RandomizeSkills",
    "Map": "RandomizeMaps",
    "Relic": "RandomizeRelics",
    "Charm": "RandomizeCharms",
    "Notch": "RandomizeCharmNotches",
    "Key": "RandomizeKeys",
    "Stag": "RandomizeStags",
    "Flame": "RandomizeFlames",
    "Grub": "RandomizeGrubs",
    "Cocoon": "RandomizeLifebloodCocoons",
    "Mask": "RandomizeMaskShards",
    "Ore": "RandomizePaleOre",
    "Egg": "RandomizeRancidEggs",
    "Vessel": "RandomizeVesselFragments",
}




