from threading import Timer

import pygame
import time
import json
import os

from pygame import Surface
from pygame.mixer import Sound
from random import randint

import log

from fight import Fight
from draw import Draw
from animation import Animation, HealthBarAnimation
from window import *


def load_players() -> list[Entity]:
    log.info('Loading players...')

    return [Entity(
        name=player['name'],
        identifier=f'{player['role']}{player['level']}',
        weapon_id=player['weapon_id'],
        object_id=player['object_id']
    ) for player in json.load(fp=open('data/players.json', 'r', encoding='utf-8'))['players']]


def load_enemy() -> Entity:
    log.info('Loading enemy...')

    enemy: dict = json.load(fp=open('data/enemy.json', 'r', encoding='utf-8'))

    return Entity(
        name=enemy['name'],
        identifier=enemy['identifier'],
        weapon_id='',
        object_id=''
    )


MUSICS_DIRECTORY: str = 'src/musics/'


class App:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.mixer.pre_init()

        self.running: bool = False
        self.window: Surface = pygame.display.set_mode((0, 0))
        self.players: list[Entity] = load_players()
        self.enemy: Entity = load_enemy()
        self.ticks: int = 0
        self.draw: Draw = Draw(self.window)
        self.fight: Fight = Fight(self.players, self.enemy, self.draw)
        self.animations: list[Animation] = []
        self.sounds: dict[int: list[Sound]] = {}
        self.end_tick: int = 0
        self.battle_music: Sound = self.pick_battle_music()
        self.end_music: Sound = Sound('src/musics/win.mp3')

        log.info('Calculating positioning data...')
        self.front_players: list[Entity] = [p for p in self.players if p.role in FRONT_ROLES]
        self.back_players: list[Entity] = [p for p in self.players if p.role in BACK_ROLES]

        self.tick_speed: int = 1

    def pick_battle_music(self) -> Sound:
        sound: Sound = Sound(MUSICS_DIRECTORY + 'battle-' + self.enemy.role + '.mp3')
        sound.set_volume(.2)
        return sound

    def init(self):
        log.info('Configuring the window...')
        pygame.display.set_caption(WINDOW_CAPTION)
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        log.info('Calculating player positions data...')
        dict_pos: dict[str: tuple[int, int]] = {}

        for i, players in enumerate([self.back_players, self.front_players]):
            n: int = len(players)
            odd: bool = n % 2 == 1

            for j, player in enumerate(players):
                pos: tuple[int, int] = (
                    int(MARGIN + i*(PLAYER_SIZE + MARGIN + 40)),
                    int(WINDOW_HEIGHT / 2 - PLAYER_SIZE / 2 - (n // 2 - j)*(PLAYER_SIZE + MARGIN) + (0 if odd else (PLAYER_SIZE + MARGIN)/2))
                )

                PLAYER_POS.append(pos)
                dict_pos[player.name] = pos

        for i, player in enumerate(self.players):
            PLAYER_POS[i] = dict_pos[player.name]

        log.info('Loading animations...')
        computed: tuple[list[Animation], dict[int: list[Sound]]] = self.fight.compute()

        self.animations += computed[0]
        self.sounds = computed[1]
        self.end_tick = max([a.start + (a.duration if a.duration is not None else 0) for a in self.animations])

        if self.fight.enemy.health > 0:
            self.end_music = Sound('src/musics/lose.mp3')
        self.end_music.set_volume(.2)

        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return

                if event.key == pygame.K_SPACE:
                    self.tick_speed = 3

                if event.key == pygame.K_LSHIFT:
                    self.tick_speed = -1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.tick_speed = 1

                if event.key == pygame.K_LSHIFT:
                    self.tick_speed = 1

    def render(self):
        self.window.fill(BACKGROUND_COLOR)

        # Draw players
        for i, player in enumerate(self.players):
            self.draw.square(ROLE_COLORS[player.role], PLAYER_POS[i][0], PLAYER_POS[i][1], PLAYER_SIZE)
            self.draw.health_bar(PLAYER_POS[i][0] + PLAYER_SIZE + 10, PLAYER_POS[i][1], 30, PLAYER_SIZE, player)

        # Draw the enemy
        self.draw.square((100, 50, 150), ENEMY_X, ENEMY_Y, ENEMY_SIZE)
        # Draw the enemy's health bar
        self.draw.health_bar(ENEMY_X - 40, ENEMY_Y, 30, ENEMY_SIZE, self.enemy)

        # Draw the animations
        for animation in self.animations:
            if animation.is_visible(self.ticks):
                animation.draw(self.ticks)

        if self.ticks >= self.end_tick + 5*FPS:
            self.draw.text('red', f't={self.ticks}', 10, 10, size=50)

            win: bool = self.fight.enemy.health <= 0
            self.draw.text(
                'green' if win else 'red',
                'Victoire !' if win else 'Défaite...',
                WINDOW_WIDTH / 2,
                WINDOW_HEIGHT / 2,
                size=200,
                centering=True
            )

        pygame.display.flip()

    def update(self):
        if self.ticks in self.sounds.keys():
            for sound in self.sounds[self.ticks]:
                sound.play()

        if self.ticks == self.end_tick:
            self.battle_music.fadeout(4000)
            Timer(5, lambda: self.end_music.play()).start()

    def run(self):
        last_update: float = time.time()

        log.info('Application started')

        self.battle_music.play(loops=-1)

        while self.running:
            now: float = time.time()

            while now - last_update >= TICK_DURATION:
                last_update += TICK_DURATION
                self.ticks += self.tick_speed
                self.update()

            self.render()
            self.handle_events()

        log.info('Closing the application...')
        pygame.quit()
