from pygame import Surface, Rect
from pygame.freetype import Font

from rpg import STAT_HEALTH, Entity


def get_font(size: float) -> Font:
    return Font('src/roboto.ttf', size)


class Draw:
    def __init__(self, screen: Surface):
        self.window: Surface = screen

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

    def health_bar(self, x: float, y: float, width: float, height: float, entity: Entity | float, border: int = 5, centering: bool = False, white: bool = False):
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
        self.rect('black', x, y, width, height, centering=centering)
        self.rect('grey',  x + border, y + border, width - 2*border, height - 2*border, centering=centering)
        self.rect(color, x + border, y - border + height - height_, width - 2*border, height_, centering=centering)

    def text(self, color: tuple[int, int, int] | str, text: str, x: float, y: float, size: float, centering = False):
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

    def image(self, image, x: float, y: float, centering: bool = False):
        self.window.blit(
            image,
            dest=(
                int(x - (image.get_width() / 2 if centering else 0)),
                int(y - (image.get_height() / 2 if centering else 0))
            )
        )
