from pygame.mixer import Sound

import log

from random import randint

from animation import *
from window import *


PHASE_IDLE: str = 'idle'
PHASE_PLAYER_1: str = 'player 0'
PHASE_PLAYER_2: str = 'player 1'
PHASE_PLAYER_3: str = 'player 2'
PHASE_PLAYER_4: str = 'player 3'
PHASE_PLAYER_5: str = 'player 4'
PHASE_ENEMY: str = 'enemy'
PHASE_HEAL: str = 'heal'

BATTLE_PHASES: list[str] = [
    PHASE_IDLE,
    PHASE_PLAYER_1, PHASE_PLAYER_2, PHASE_PLAYER_3, PHASE_PLAYER_4, PHASE_PLAYER_5,
    PHASE_ENEMY, PHASE_HEAL
]

PLAYER_PHASES: list[str] = [PHASE_PLAYER_1, PHASE_PLAYER_2, PHASE_PLAYER_3, PHASE_PLAYER_4, PHASE_PLAYER_5]

PHASE_DURATION: int = int(2 * TPS)

MAGE_SPELLS_DIRECTORY: str = 'src/animations/mage/'


def sound(filename: str, volume: float = 1):
    s: Sound = Sound(filename)
    s.set_volume(volume)
    return s


def pick_mage_spell() -> tuple[str, str]:
    spells: list[str] = os.listdir(MAGE_SPELLS_DIRECTORY)
    spell: str = spells[randint(0, len(spells) - 1)]

    spell_animation: str = MAGE_SPELLS_DIRECTORY + spell
    spell_sound: str = 'src/sounds/' + spell + '.mp3'

    return spell_animation, spell_sound


def roll_attack(attacker: Entity, defender: Entity) -> tuple[int, bool, bool, bool]:
    critical: bool = attacker.roll(STAT_CRITICAL)
    hitting: bool = attacker.roll(STAT_ACCURACY)
    dodging: bool = defender.roll(STAT_DODGE)

    damaging: bool = hitting and not dodging

    attack: float = attacker.roll(STAT_ATTACK)
    defense: float = defender.roll(STAT_DEFENSE)

    return -int(attack * (1 - defense) * (2 if critical else 1) * damaging), critical, hitting, dodging


def roll_heal(healer: Entity, stat: str = STAT_HEAL) -> tuple[int, bool, bool, bool]:
    critical: bool = healer.roll(STAT_CRITICAL)
    heal: int = healer.roll(stat)

    return int(heal * (critical + 1)), critical, True, False


def print_attack(damage: int, critical: bool, hit: bool, dodge: bool, attacker: Entity, defender: Entity):
    if hit and not dodge:
        log.info(f'{attacker.name} deals {damage} hp{' (CRITICAL!)' if critical else ''} to {defender.name} : {defender.health} hp remaining')
    elif dodge:
        log.info(f'{attacker.name} attacks the enemy, but he dodges !')
    else:
        log.info(f'{attacker.name} has aim issues')


def print_heal(heal: int, critical: bool, healer: Entity, healed: Entity):
    log.info(f'{healer.name} heals {heal} hp{' (CRITICAL!)' if critical else ''} to {healed.name} : {healed.health} hp remaining')


class Fight:
    def __init__(self, players: list[Entity], enemy: Entity, draw: Draw | None):
        # Initialize attributes
        self.current_phase: str = BATTLE_PHASES[-1]
        self.turn: int = 0
        self.ticks: int = 0

        self.players: list[Entity] = players
        self.enemy: Entity = enemy
        self.entities: list[Entity] = players + [enemy]

        self.nb_players: int = len(players)
        self.nb_alive: int = self.nb_players

        self.health_animation_ticks: list[list[tuple[int, float]]] = [[(0, 1.0)] for _ in range(len(self.entities))]
        self.draw: Draw | None = draw

        # Change enemy health based on the amount of players
        self.enemy.stats[STAT_HEALTH] = self.enemy.health = self.enemy.health * self.nb_players

        # Outputs
        self.animations: list[Animation] = []
        self.sounds: dict[int: list[Sound]] = {}

    def get_next_phase(self, current_phase: str):
        next_phase: str = BATTLE_PHASES[(BATTLE_PHASES.index(current_phase) + 1) % len(BATTLE_PHASES)]

        if next_phase in PLAYER_PHASES and int(next_phase[-1]) >= self.nb_players:
            return self.get_next_phase(next_phase)

        return next_phase

    def handle_life_change(self, healing: bool, i: int, j: int):
        if self.entities[i].health <= 0 or self.entities[j].health <= 0:
            return []

        source: Entity = self.entities[i]
        target: Entity = self.entities[j]

        life_change, critical, hitting, dodging = roll_heal(source) if healing else roll_attack(source, target)

        old_ratio: float = target.health / target.stats[STAT_HEALTH]
        target.health = max(0, min(target.stats[STAT_HEALTH], target.health + life_change))
        new_ratio: float = target.health / target.stats[STAT_HEALTH]

        if old_ratio != new_ratio:
            if self.health_animation_ticks[j][-1][0] == self.ticks + 2*TPS:
                self.health_animation_ticks[j][-1] = (self.health_animation_ticks[j][-1][0], new_ratio)
            else:
                self.health_animation_ticks[j].append((self.ticks + 2 * TPS, new_ratio))

        if healing:
            print_heal(life_change, critical, source, target)
        else:
            print_attack(life_change, critical, hitting, dodging, source, target)

        if self.draw is None:
            return []

        pos_i: tuple[int, int] = (ENEMY_X, ENEMY_Y) if i == -1 else PLAYER_POS[i]
        pos_j: tuple[int, int] = (ENEMY_X, ENEMY_Y) if j == -1 else PLAYER_POS[j]
        size_i: int = ENEMY_SIZE if i == -1 else PLAYER_SIZE
        size_j: int = ENEMY_SIZE if j == -1 else PLAYER_SIZE

        if self.entities[i].role == ROLE_UNDEAD:
            self.animations.append(FramedAnimation(
                self.ticks + TPS // 2,
                'src/animations/undead',
                pos_j[0] + size_j / 2,
                pos_j[1] + size_j / 2,
                PLAYER_SIZE, PLAYER_SIZE,
                self.draw,
                loops=1
            ))

            self.sounds[self.ticks].append(sound('src/sounds/undead.mp3'))
        elif self.entities[i].role == ROLE_WOLF:
            self.animations.append(FramedAnimation(
                self.ticks + TPS // 2,
                'src/animations/wolf',
                pos_j[0] + size_j / 2,
                pos_j[1] + size_j / 2,
                PLAYER_SIZE, PLAYER_SIZE,
                self.draw,
                loops=1
            ))

            self.sounds[self.ticks].append(sound('src/sounds/bite.mp3'))
        elif self.entities[i].role in [ROLE_WARRIOR, ROLE_THIEF, ROLE_LOOTER]:
            size: float = PLAYER_SIZE if self.entities[i].role in ROLE_LOOTER else ENEMY_SIZE

            for i in range(3 if critical else 1):
                self.animations.append(FramedAnimation(
                    self.ticks + TPS // 2 + i * TPS // 5,
                    'src/animations/slash',
                    pos_j[0] + size_j / 2 + i * randint(-30, 30),
                    pos_j[1] + size_j / 2 + i * randint(-30, 30),
                    size, size, self.draw, loops=1
                ))

                self.sounds[self.ticks + TPS // 2 + i * TPS // 5].append(sound('src/sounds/sword.mp3', .8))
        elif self.entities[i].role == ROLE_MAGE and not healing:
            spell_animation, spell_sound = pick_mage_spell()
            lightning: bool = spell_animation.endswith('lightning')

            for i in range((2 if lightning else 1) * (3 if critical else 1)):
                off: int = ENEMY_SIZE // 5

                self.animations.append(FramedAnimation(
                    self.ticks + i * TPS // 5, spell_animation,
                    pos_j[0] + size_j / 2 + (randint(-off, off) if lightning else 0),
                    pos_j[1] + size_j / 2 + (randint(-off, 0) if lightning else 0),
                    ENEMY_SIZE, ENEMY_SIZE, self.draw, loops=1
                ))

                self.sounds[self.ticks + i * TPS // 5].append(sound(spell_sound, 1 if lightning else .4))
        elif self.entities[i].role == ROLE_DRAGON:
            for i in range(5 * (2 if critical else 1)):
                self.animations.append(FramedAnimation(
                    self.ticks + i * TPS // 10, 'src/animations/dragon',
                    pos_j[0] + size_j / 2 + (5 - i) * 50,
                    pos_j[1] + size_j / 2 + randint(-10, 10),
                    ENEMY_SIZE, ENEMY_SIZE, self.draw, loops=1
                ))

            self.sounds[self.ticks].append(sound('src/sounds/fire.wav'))
        elif healing:
            if old_ratio != new_ratio:
                size = ENEMY_SIZE if j == -1 else PLAYER_SIZE

                for i in range(4):
                    self.animations.append(FramedAnimation(
                        self.ticks + i * TPS // 5, 'src/animations/heal',
                        pos_j[0] + size_j / 2, pos_j[1] + size_j / 2,
                        size * 1.1 ** i, size * 1.1 ** i, self.draw, loops=1
                    ))

                self.sounds[self.ticks].append(sound('src/sounds/healing.wav', .3))
        elif self.entities[i].role == ROLE_DRUID:
            self.animations.append(MovingTextAnimation(
                self.ticks,
                (pos_i[0] + size_i / 2, pos_i[1] + size_i / 2),
                (pos_j[0] + size_j / 2, pos_j[1] + size_j / 2),
                f'{'+' if life_change > 0 else '-'} {life_change}',
                48, 'green' if life_change > 0 else ('yellow' if critical else 'red'), self.draw
            ))

            self.sounds[self.ticks].append(sound('src/sounds/plants.wav', .5))
        else:
            self.animations.append(MovingTextAnimation(
                self.ticks,
                (pos_i[0] + size_i / 2, pos_i[1] + size_i / 2),
                (pos_j[0] + size_j / 2, pos_j[1] + size_j / 2),
                f'{'+' if life_change > 0 else '-'} {life_change}',
                48, 'green' if life_change > 0 else ('yellow' if critical else 'red'), self.draw
            ))

        if not hitting or dodging:
            size: int = ENEMY_SIZE if j == -1 else PLAYER_SIZE

            self.animations.append(FramedAnimation(
                self.ticks - TPS // 2, 'src/animations/dodge',
                pos_j[0] + size_j / 2, pos_j[1] + size_j / 2,
                size, size, self.draw, loops=1
            ))

            for i in range(3):
                self.sounds[self.ticks + TPS + i * TPS // 10].append(sound('src/sounds/dodge.wav'))

    def handle_heal(self, i: int, j: int) -> list[Animation]:
        return self.handle_life_change(True, i, j)

    def handle_attack(self, i: int, j: int):
        return self.handle_life_change(False, i, j)

    def roll_enemy_attacks(self):
        attacks: int = 1

        if self.nb_alive > 1 and random() <= -0.1 * self.nb_players ** 2 + 1.1 * self.nb_players - 2.1:
            attacks += 1

            if self.nb_alive > 2 and self.nb_players == 5 and random() <= 0.3:
                attacks += 1

        return attacks

    def compute(self) -> tuple[list[Animation], dict[int: list[Sound]]] | bool:
        self.animations = []
        self.sounds = {i: [] for i in range(TPS * 60 * 10)}

        while self.nb_alive > 0 and self.enemy.health > 0:
            self.current_phase = self.get_next_phase(self.current_phase)

            if self.current_phase == PHASE_IDLE:
                self.turn += 1
                log.info(f'\n--- Turn {self.turn} ---')

            self.ticks += PHASE_DURATION

            log.info(f'-- Phase : {self.current_phase} --')

            if self.current_phase == PHASE_IDLE:
                self.ticks -= PHASE_DURATION
                log.info('Players:')

                for player in self.players:
                    log.info(f'- {player.name} {player.role} : {player.health} / {player.stats[STAT_HEALTH]} hp')

                log.info('\nEnemy:', self.enemy.name, self.enemy.role, ':', self.enemy.health, '/', self.enemy.stats[STAT_HEALTH], 'hp')
            elif self.current_phase in PLAYER_PHASES:
                if self.players[int(self.current_phase[-1])].health <= 0:
                    self.ticks -= PHASE_DURATION
                    continue

                self.handle_attack(int(self.current_phase[-1]), -1)
            elif self.current_phase == PHASE_ENEMY:
                alive_players: list[Entity] = [player for player in self.players if player.health > 0]

                front_range: list[Entity] = [player for player in alive_players if player.role in FRONT_ROLES]
                back_range: list[Entity] = [player for player in alive_players if player.role in BACK_ROLES]

                attacks: int = self.roll_enemy_attacks()

                for _ in range(attacks):
                    for battle_range in [front_range, back_range]:
                        if len(battle_range) > 0:
                            j: int = self.entities.index(battle_range[randint(0, len(battle_range) - 1)])

                            self.handle_attack(-1, j)
                            self.nb_alive = len([p for p in self.players if p.health > 0])
                            break
            elif self.current_phase == PHASE_HEAL:
                for i, healer in enumerate(self.players):
                    if healer.stats[STAT_HEAL] > 0:
                        for j, healed in enumerate([player for player in self.players if player.name != healer.name]):
                            self.handle_heal(i, j)

                    if healer.stats[STAT_REGENERATION] > 0:
                        self.handle_heal(i, i)

                if self.enemy.stats[STAT_HEAL] > 0:
                    self.handle_heal(-1, -1)
        else:
            log.info(f'Done : winner = {'Players' if self.nb_alive > 0 else 'Enemy'}\n')

        if self.draw is not None:
            self.animations.append(HealthBarAnimation(ENEMY_X - 40, ENEMY_Y, ENEMY_SIZE, self.health_animation_ticks[-1], self.draw))

            for i in range(len(self.players)):
                pos: tuple[int, int] = PLAYER_POS[i]
                self.animations.append(HealthBarAnimation(pos[0] + PLAYER_SIZE + 10, pos[1], PLAYER_SIZE, self.health_animation_ticks[i], self.draw))

            return self.animations, {key: value for key, value in self.sounds.items() if len(value) > 0}
        else:
            return self.nb_alive > 0
