from math import sin, pi

import pygame.image
from pygame import Surface, Rect
from pygame.freetype import Font

from rpg import STAT_HEALTH, Entity, ROLES, PLAYER_ROLES
from window import PLAYER_SIZE, ENEMY_SIZE, TPS


def get_font(size: float) -> Font:
    return Font('src/roboto.ttf', size)


class Draw:
    def __init__(self, screen: Surface):
        self.window: Surface = screen

        self.role_images: dict[str: Surface] = {}

        for role in ROLES:
            image: Surface = pygame.image.load(f'src/sprites/role-{role}.png')
            size: int = PLAYER_SIZE if role in PLAYER_ROLES else ENEMY_SIZE
            image = pygame.transform.scale(image, size=(size, size))

            self.role_images[role] = image

    def rect(self, color: tuple[int, int, int] | str, x: float, y: float, width: float, height: float, centering: bool = False):
        self.window.fill(
            color=color,
            rect=Rect(
                int(x - (width // 2 if centering else 0)),
                int(y - (height // 2 if centering else 0)),
                int(width), int(height)
            )
        )

    def square(self, color: tuple[int, int, int] | str, x: float, y: float, size: float, centering: bool = False):
        self.rect(color, x, y, size, size, centering=centering)

    def health_bar(self, x: float, y: float, entity: Entity | float, width: float = 30, height: float = 80, border: int = 5, vertical: bool = True, white: bool = False):
        # Calculating some data
        if type(entity) is Entity:
            ratio: float = entity.health / entity.stats[STAT_HEALTH]
        elif type(entity) in [float, int]:
            ratio: float = entity
        else:
            raise ValueError(f'{entity} not instance of any of the following : Entity, float or int')

        height_: int = round((height - 2*border) * ratio)

        color: tuple[int, int, int] = (200, 200, 200) if white else (
            min(255, max(0, int(255 * (1 - ratio)))),
            min(255, max(0, int(255 * ratio))),
            0
        )

        # Draw health bar
        if vertical:
            self.rect('black', x, y, width, height, centering=False)
            self.rect('grey',  x + border, y + border, width - 2*border, height - 2*border, centering=False)
            self.rect(color, x + border, y - border + height - height_, width - 2*border, height_, centering=False)
        else:
            self.rect('black', x, y, width, height, centering=True)
            self.rect('grey',  x, y, width - 2*border, height - 2*border, centering=True)
            self.rect(color, x, y, (width-2*border)*ratio, height - 2*border, centering=True)

    def text(self, color: tuple[int, int, int] | str, text: str, x: float, y: float, size: float, centering=False):
        # Calculating some data
        font: Font = get_font(size)
        surface, rect = font.render(text, fgcolor=color)

        # Draw the text
        self.window.blit(
            surface, (
                int(x - (rect.width / 2 if centering else 0)),
                int(y - (rect.height / 2 if centering else 0))
            )
        )

    def image(self, image, x: float, y: float, width: float | None = None, height: float | None = None, centering: bool = False):
        if width is not None:
            image = pygame.transform.scale(image, size=(width, image.get_height()))

        if height is not None:
            image = pygame.transform.scale(image, size=(image.get_width(), height))

        self.window.blit(
            image,
            dest=(
                int(x - (image.get_width() / 2 if centering else 0)),
                int(y - (image.get_height() / 2 if centering else 0))
            )
        )

    def entity(self, x: float, y: float, role: str, tick: int = 0):
        self.image(
            self.role_images[role], x, y,
            height=self.role_images[role].get_height() * (1 + sin(2*pi * (tick / (3*TPS))) / 10),
            centering=True
        )
