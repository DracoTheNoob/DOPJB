import random
import excel


role_excel_rows = {
    'G': 2,
    'V': 9,
    'M': 16,
    'D': 23
}


class Weapon:
    def __init__(self, id: str, name: str, miss: int, attack: int, crit: int):
        self.id = id
        self.name = name
        self.miss = miss
        self.attack = attack
        self.crit = crit

    def __str__(self):
        name: str = f"'{self.name}'"
        miss: str = f'miss={self.miss}'
        damage: str = f'dmg={self.attack}'
        crit: str = f'crit={self.crit}'

        return f'{name}[{miss}, {damage}, {crit}]'


def load_weapon(weapon_id: str) -> Weapon | None:
    if weapon_id is None or weapon_id == '':
        return None

    return Weapon(
        id=weapon_id,
        name=excel.read_by_id('armes', weapon_id, 'D'),
        miss=excel.read_by_id('armes', weapon_id, 'E'),
        attack=excel.read_by_id('armes', weapon_id, 'F'),
        crit=excel.read_by_id('armes', weapon_id, 'G')
    )


class Item:
    def __init__(self, id: str, name: str, hp: int, dodge: int, defense: int, regen_in: int, regen_out: int):
        self.id = id
        self.name = name
        self.hp = hp
        self.dodge = dodge
        self.defense = defense
        self.regen_in = regen_in
        self.regen_out = regen_out

    def __str__(self):
        name: str = f"name='{self.name}'"
        hp: str = f'hp={self.hp}'
        dodge: str = f'dodge={self.dodge}'
        defense: str = f'def={self.defense}'
        regen_in: str = f'regen_in={self.regen_in}'
        regen_out: str = f'regen_out={self.regen_in}'

        return f'[{name}, {hp}, {dodge}, {defense}, {regen_in}, {regen_out}]'


def load_item(item_id: str) -> Item | None:
    if item_id is None or len(item_id) != 4:
        return None

    return Item(
        id=item_id,
        name=excel.read_by_id('objet', item_id, 'D'),
        hp=excel.read_by_id('objet', item_id, 'E'),
        dodge=excel.read_by_id('objet', item_id, 'F'),
        defense=excel.read_by_id('objet', item_id, 'G'),
        regen_in=excel.read_by_id('objet', item_id, 'H'),
        regen_out=excel.read_by_id('objet', item_id, 'I')
    )


class Attack:
    def __init__(self, hit: bool, damage: int, critical: bool):
        self.hit = hit
        self.damage = damage
        self.critical = critical

    def __str__(self):
        hit = f'hit={self.hit}'
        damage = f'damage={self.damage}'
        critical = f'critical={self.critical}'

        return f'[{hit}, {damage}, {critical}]'


class Entity:
    def __init__(self, name: str, hp: int, miss: int, attack: int, crit: int, dodge: int, defense: int, regen_in: int,
                 regen_out: int, weapon_id: str | None, item_id: str | None):
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.miss = miss
        self.attack = attack
        self.crit = crit
        self.dodge = dodge
        self.defense = defense
        self.regen_in = regen_in
        self.regen_out = regen_out
        self.targets = []

        if weapon_id is not None:
            self.weapon = load_weapon(weapon_id)

            if self.weapon is not None:
                self.miss += self.weapon.miss
                self.crit += self.weapon.crit
                self.attack += self.weapon.attack
        else:
            self.weapon = None

        if item_id is not None:
            self.item = load_item(item_id)

            try:
                if self.item is not None:
                    self.hp += int(self.item.hp)
                    self.max_hp += int(self.item.hp)
                    self.defense += int(self.item.defense)
                    self.regen_in += int(self.item.regen_in)
                    self.regen_out += int(self.item.regen_out)
            except TypeError:
                pass
        else:
            self.item = None

        self.hit = 100 - miss

    def __str__(self):
        name: str = f"name='{self.name}'"
        hp: str = f'hp=[{self.hp}/{self.max_hp} ({int(self.hp / self.max_hp * 100)}%)]'
        miss: str = f'miss={self.miss}'
        dmg: str = f'dmg={self.attack}'
        crit: str = f'crit={self.crit}'
        dodge: str = f'dodge={self.dodge}'
        defense: str = f'def={self.defense}'
        regen_in: str = f'regen_in={self.regen_in}'
        regen_out: str = f'regen_out={self.regen_out}'
        weapon: str = f'weapon={str(self.weapon)}'
        item: str = f'weapon={str(self.item)}'

        return f'[{name}, {hp}, {miss}, {dmg}, {crit}, {dodge}, {defense}, {regen_in}, {regen_out}, {weapon}, {item}]'

    def roll_attack(self) -> Attack:
        damage = random.gauss(self.attack, self.attack / 6)

        hit = random.randint(1, 100) <= int(self.hit)
        critical = random.randint(1, 100) <= int(self.crit) and hit
        damage = int(round((damage * 2) if critical else damage)) if hit else 0

        return Attack(hit, damage, critical)

    def roll_defense(self, attack: Attack) -> Attack:
        hit = random.randint(1, 100) > self.dodge
        damage = int(round(attack.damage * (1 - self.defense/100))) if hit else 0

        if self.name in ['P1', 'P2', 'P3', 'L1', 'L2', 'L3', 'MV1', 'MV2', 'MV3', 'D1']:
            self.hp -= damage

        return Attack(hit, damage, attack.critical)


def load_enemy(enemy_id: str, hp_modifier: int = 1) -> Entity:
    return Entity(
        name=enemy_id,
        hp=excel.read_by_id('monstres', enemy_id, 'B') * hp_modifier,
        miss=excel.read_by_id('monstres', enemy_id, 'C'),
        attack=excel.read_by_id('monstres', enemy_id, 'D'),
        crit=excel.read_by_id('monstres', enemy_id, 'E'),
        dodge=excel.read_by_id('monstres', enemy_id, 'F'),
        defense=excel.read_by_id('monstres', enemy_id, 'G'),
        regen_in=excel.read_by_id('monstres', enemy_id, 'H'),
        regen_out=excel.read_by_id('monstres', enemy_id, 'I'),
        weapon_id=None, item_id=None
    )


class Player(Entity):
    def __init__(self, name: str, role: str, level: int, hp: int, miss: int, attack: int, crit: int, dodge: int,
                 defense: int, regen_in: int, regen_out: int, weapon_id: str | None, item_id: str | None):
        super().__init__(name, hp, miss, attack, crit, dodge, defense, regen_in, regen_out, weapon_id, item_id)

        self.role = role
        self.level = level

    def __str__(self):
        prefix: str = f"role='{self.role}', lvl={self.level}"

        return f'[{prefix}, {Entity.__str__(self)[1:]}'


def load_player(role: str, level: int, name: str, weapon_id: str | None, item_id: str | None) -> Player:
    row = role_excel_rows[role] + level

    return Player(
        role=role, level=level, name=name,
        hp=excel.read_cell('classes', f'B{row}'),
        miss=excel.read_cell('classes', f'C{row}'),
        attack=excel.read_cell('classes', f'D{row}'),
        crit=excel.read_cell('classes', f'E{row}'),
        dodge=excel.read_cell('classes', f'F{row}'),
        defense=excel.read_cell('classes', f'G{row}'),
        regen_in=excel.read_cell('classes', f'H{row}'),
        regen_out=excel.read_cell('classes', f'I{row}'),
        weapon_id=weapon_id, item_id=item_id
    )
