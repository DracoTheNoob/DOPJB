from openpyxl import Workbook, load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from random import random, gauss


# Stats related constants
STAT_HEALTH: str = 'health'
STAT_ATTACK: str = 'attack'
STAT_DEFENSE: str = 'defense'
STAT_CRITICAL: str = 'critical'
STAT_ACCURACY: str = 'accuracy'
STAT_DODGE: str = 'dodge'
STAT_REGENERATION: str = 'regeneration'
STAT_HEAL: str = 'heal'

STATS: list[str] = [
    STAT_HEALTH, STAT_ATTACK, STAT_DEFENSE,
    STAT_CRITICAL, STAT_ACCURACY, STAT_DODGE,
    STAT_REGENERATION, STAT_HEAL
]
POINT_BASED_STATS: list[str] = [STAT_HEALTH, STAT_ATTACK, STAT_REGENERATION, STAT_HEAL]
PERCENTAGE_BASED_STATS: list[str] = [STAT_DEFENSE, STAT_CRITICAL, STAT_ACCURACY, STAT_DODGE]

WEAPON_STATS: list[str] = [STAT_ATTACK, STAT_CRITICAL, STAT_ACCURACY, STAT_HEAL]
OBJECT_STATS: list[str] = [STAT_HEALTH, STAT_DEFENSE, STAT_DODGE, STAT_REGENERATION]

PROBABILITY_ROLLS: list[str] = [STAT_CRITICAL, STAT_ACCURACY, STAT_DODGE]
POINT_ROLLS: list[str] = [STAT_ATTACK, STAT_DEFENSE, STAT_REGENERATION, STAT_HEAL]

# Item related constants
TYPE_WEAPON: str = 'weapon'
TYPE_OBJECT: str = 'object'
ITEM_TYPES: list[str] = [TYPE_WEAPON, TYPE_OBJECT]


# Entity related constants
ROLE_WARRIOR: str = 'G'
ROLE_THIEF: str = 'V'
ROLE_MAGE: str = 'M'
ROLE_DRUID: str = 'D'

ROLE_UNDEAD: str = 'MV'
ROLE_WOLF: str = 'L'
ROLE_LOOTER: str = 'P'
ROLE_DRAGON: str = 'DG'

ROLES: list[str] = [
    ROLE_WARRIOR, ROLE_THIEF, ROLE_MAGE, ROLE_DRUID,
    ROLE_WOLF, ROLE_UNDEAD, ROLE_LOOTER, ROLE_DRAGON
]

PLAYER_ROLES: list[str] = [ROLE_WARRIOR, ROLE_THIEF, ROLE_MAGE, ROLE_DRUID]
ENEMY_ROLES: list[str] = [ROLE_UNDEAD, ROLE_WOLF, ROLE_LOOTER, ROLE_DRAGON]

FRONT_ROLES: list[str] = [ROLE_WARRIOR, ROLE_THIEF]
BACK_ROLES: list[str] = [ROLE_MAGE, ROLE_DRUID]

ROLE_TO_NAME: dict[str, str] = {
    ROLE_UNDEAD: 'Mort-Vivant',
    ROLE_WOLF: 'Loup',
    ROLE_LOOTER: 'Pilleur',
    ROLE_DRAGON: 'Dragon'
}


ENEMY_NAMES: dict[(str, int): str] = {
    (role, level + 1): f'{ROLE_TO_NAME[role]}{f' niv. {level + 1}' if role != ROLE_DRAGON else ''}' for role in ENEMY_ROLES for level in range(3 if role != ROLE_DRAGON else 1)
}

# Excel related variables
workbook: Workbook = load_workbook('src/bible.xlsx', read_only=True, data_only=True)

STAT_CELL_COLUMNS: dict[str: str] = {
    STAT_HEALTH: 'B',
    STAT_ATTACK: 'C',
    STAT_DEFENSE: 'D',
    STAT_CRITICAL: 'E',
    STAT_ACCURACY: 'F',
    STAT_DODGE: 'G',
    STAT_REGENERATION: 'H',
    STAT_HEAL: 'I'
}


class StatSet:
    def __init__(self, **args):
        self.stats: dict[str: float] = {}

        if 'args' in args:
            args = args['args']

        for stat in STATS:
            if stat in args:
                self.stats[stat] = float(args[stat])
            else:
                self.stats[stat] = 0.0

    def __getitem__(self, item):
        assert item in STATS
        return self.stats[item]

    def __setitem__(self, key, value):
        assert key in STATS
        self.stats[key] = float(value)

    def __add__(self, other):
        assert type(other) is StatSet

        result: StatSet = StatSet(
            health=self[STAT_HEALTH], attack=self[STAT_ATTACK], defense=self[STAT_DEFENSE],
            critical=self[STAT_CRITICAL], accuracy=self[STAT_ACCURACY], dodge=self[STAT_DODGE],
            regeneration=self[STAT_REGENERATION], heal=self[STAT_HEAL]
        )

        for stat, other_value in other.stats.items():
            result[stat] += other_value

        return result

    def clone(self):
        clone: StatSet = StatSet()

        for stat in self.stats:
            clone[stat] = self[stat]

        return clone


def load_entity_stats(identifier: str) -> StatSet:
    row: int = 3

    sheet: Worksheet = workbook['stat']
    current_id_cell = sheet[f'A{row}']

    while current_id_cell is not None and current_id_cell.value is not None:
        if str(current_id_cell.value) == identifier:
            break

        row += 1
        current_id_cell = sheet[f'A{row}']
    else:
        return StatSet()

    stat_dict: dict[str: float] = {}

    for stat in [s for s in STATS if s != STAT_HEAL or identifier[:-1] not in ENEMY_ROLES]:
        cell: str = f'{STAT_CELL_COLUMNS[stat]}{row}'
        stat_dict[stat] = float(sheet[cell].value)

    return StatSet(args=stat_dict)


class Item:
    def __init__(self, item_id: str, item_name: str, item_type: str, **args):
        self.id: str = item_id
        self.name: str = item_name
        self.type: str = item_type
        self.stats: StatSet = StatSet(args=args)


class Weapon(Item):
    def __init__(self, item_id: str, item_name: str, attack: float, critical: float, accuracy: float, heal: float):
        super().__init__(
            item_id, item_name, TYPE_WEAPON,
            attack=attack, critical=critical, accuracy=accuracy, heal=heal
        )


class Object(Item):
    def __init__(self, item_id: str, item_name: str, health: float, defense: float, dodge: float, regeneration: float):
        super().__init__(
            item_id, item_name, TYPE_OBJECT,
            health=health, defense=defense, dodge=dodge, regeneration=regeneration
        )


def load_item_infos(item_id: str, item_type: str) -> tuple[str, tuple[float, float, float, float]]:
    column: str = 'A' if item_type == TYPE_WEAPON else 'K'
    row: int = 4

    sheet: Worksheet = workbook['stuff']
    current_id_cell = sheet[f'{column}{row}']

    while current_id_cell is not None and current_id_cell.value is not None:
        if str(current_id_cell.value) == item_id:
            break

        row += 1
        current_id_cell = sheet[f'{column}{row}']
    else:
        return '', (0, 0, 0, 0)

    item_name: str = sheet[f'{chr(ord(column)+4)}{row}'].value
    item_stats: tuple[float, float, float, float] = (
        float(sheet[f'{chr(ord(column) + 5)}{row}'].value),
        float(sheet[f'{chr(ord(column) + 6)}{row}'].value),
        float(sheet[f'{chr(ord(column) + 7)}{row}'].value),
        float(sheet[f'{chr(ord(column) + 8)}{row}'].value)
    )

    return item_name, item_stats


def load_weapon(item_id: str) -> Weapon:
    item_data: tuple[str, tuple[float, float, float, float]] = load_item_infos(item_id, TYPE_WEAPON)

    name: str = item_data[0]
    attack, accuracy, critical, heal = item_data[1]

    return Weapon(item_id, name, attack, accuracy, critical, heal)


def load_object(item_id: str) -> Object:
    item_data: tuple[str, tuple[float, float, float, float]] = load_item_infos(item_id, TYPE_OBJECT)

    name: str = item_data[0]
    health, defense, dodge, regeneration = item_data[1]

    return Object(item_id, name, health, defense, dodge, regeneration)


class Entity:
    def __init__(self, name: str, identifier: str, weapon_id: str, object_id: str, stats: StatSet | None = None):
        self.name: str = name
        self.identifier: str = identifier
        self.role: str = identifier[:-1]
        self.stats: StatSet = (load_entity_stats(identifier) + load_weapon(weapon_id).stats + load_object(object_id).stats) if stats is None else stats
        self.health = self.stats[STAT_HEALTH]
        self.weapon_id: str = weapon_id
        self.object_id: str = object_id

    def apply_buff(self, buff: float):
        for stat in self.stats:
            self.stats[stat] *= 1 + buff

    def roll(self, stat: str) -> bool | float:
        assert stat in PROBABILITY_ROLLS + POINT_ROLLS

        if stat in PROBABILITY_ROLLS:
            return random() <= self.stats[stat]
        elif stat in POINT_ROLLS:
            return gauss(self.stats[stat], self.stats[stat] / 5)  # TODO : talk about that '/ 5'

    def heal(self, heal: int):
        self.health = min(self.health + heal, self.stats[STAT_HEALTH])

    def clone(self):
        return Entity(self.name, self.identifier, self.weapon_id, self.object_id, self.stats.clone())
