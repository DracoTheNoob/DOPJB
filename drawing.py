import math
import random

import pygame
import pygame.font
import pygame.image

last_ratios = {}
images_cache = {}
animations_cache = {}

total_between_space, window_width, window_height, o1, o2, w = 0, 0, 0, 0, 0, 0
names = {
    'D1': 'Le Dragon',
    'L1': 'Loup (niv. 1)',
    'L2': 'Loup (niv. 2)',
    'L3': 'Loup (niv. 3)',
    'MV1': 'Mort-Vivant (niv. 1)',
    'MV2': 'Mort-Vivant (niv. 2)',
    'MV3': 'Mort-Vivant (niv. 3)',
}


def boring_calculations(screen, total_players_space: float) -> tuple[float, int, int, int, int, int]:
    """
    Do boring calculations to place elements on the screen
    :param screen: The used screen
    :param total_players_space: The decimal percentage (from 0.0 to 1.0) of the total horizontal space taken by players
    :return: The result of the calculations
    """
    global total_between_space, window_width, window_height, o1, o2, w

    total_between_space = 1 - total_players_space
    window_width, window_height = screen.get_size()

    o1 = 15
    o2 = int((total_between_space * window_width - 2 * o1) / 4)
    w = int((total_players_space / 5) * window_width)

    return total_between_space, window_width, window_height, o1, o2, w


def draw_health_bar(screen, x: int, y: int, width: int, value: int, ratio: float, last_value: float, tick: int, boss: bool) -> None:
    """
    Draw a health bar on the specified location
    :param screen: The screen where the bar will be drawn
    :param x: The x location of the bar on the screen
    :param y: The y location of the bar on the screen
    :param width: The width of the bar
    :param value: The value in hp of the health
    :param ratio: The value between 0 and 1 representing the percentage of the bar that is filled
    :param last_value: The last value between 0 and 1
    :param tick: Current remaining ticks since next
    :param boss: If the bar should be displayed as a boss health bar or not
    :return: None
    """
    global w
    height = 30

    if boss:
        x = 50
        y = 20

        width = screen.get_width() - 100
        height = 50

    temp_value = ratio + ((last_value - ratio) * (max(tick, 30) - 30)) / 30
    inner_color = ((1 - temp_value) * 255, temp_value * 255, 0)

    pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(x, y, width, height))
    pygame.draw.rect(screen, (120, 120, 120), pygame.Rect(x + 5, y + 5, width - 10, height - 10))
    pygame.draw.rect(screen, inner_color, pygame.Rect(x + 5, y + 5, int((width - 10) * temp_value), height - 10))

    if not boss:
        draw_text(screen, x + 12, y+6, str(value), color=(255, 255, 255))


# copied and pasted function to make a text with outline -> return an image of a text only with borders, no inside
def text_hollow(font, message, font_color):
    not_color = [c ^ 0xFF for c in font_color]
    base = font.render(message, 0, font_color, not_color)
    size = base.get_width() + 2, base.get_height() + 2
    img = pygame.Surface(size, 16)
    img.fill(not_color)
    base.set_colorkey(0)
    img.blit(base, (0, 0))
    img.blit(base, (2, 0))
    img.blit(base, (0, 2))
    img.blit(base, (2, 2))
    base.set_colorkey(0)
    base.set_palette_at(1, not_color)
    img.blit(base, (1, 1))
    img.set_colorkey(not_color)
    return img


def draw_text(screen, x: int, y: int, content: str, color: tuple = (240, 240, 240), font=pygame.font.get_default_font(),
              font_size: int = 30, outline_color: tuple[int, int, int] = None, center: bool = False) -> None:
    """
    Draw a specified text on a specified location on the given screen
    :param screen: The screen where the text will be in
    :param x: The x location of the text on the screen
    :param y: The y location of the text on the screen
    :param content: The content of the text
    :param color: The color of the text
    :param font: The font used to write the text
    :param font_size: The size of the font
    :param outline_color: If the text is shown with outline or not
    :return: The width and length of the text on screen
    :param center: True if the given x and y are the center of the text, False if it is the top-left corner of the text
    """

    used_font = pygame.font.SysFont(font, font_size)
    text = used_font.render(content, False, color)

    if outline_color is not None:
        base = used_font.render(content, 0, color)
        outline = text_hollow(used_font, content, outline_color)
        img = pygame.Surface(outline.get_size(), 16)
        img.blit(base, (1, 1))
        img.blit(outline, (0, 0))
        img.set_colorkey(0)

        screen.blit(img, (x - (img.get_width()/2 if center else 0), y - (img.get_height()/2 if center else 0)))
    else:
        screen.blit(text, (x - (text.get_width()/2 if center else 0), y - (text.get_height()/2 if center else 0)))


def draw_rect(screen, x: int, y: int, width: int, height: int, color: tuple[int, int, int], fill: bool = False) -> None:
    """
    Draw a rectangle on the screen with specified dimensions and color
    :param screen: The screen to render the rectangle on
    :param x: The x location of the rectangle on the screen
    :param y: The y location of the rectangle on the screen
    :param width: The width of the rectangle
    :param height: The height of the rectangle
    :param color: The color of the rectangle : a tuple (r, g, b) with r, g, b between 0 and 255 both included
    :param fill: If the square must be drawn inside or not
    :return: None
    """
    pygame.draw.rect(screen, color, pygame.Rect(x, y, width, height))

    if not fill:
        pygame.draw.rect(screen, (30, 30, 30), pygame.Rect(x+1, y+1, width-2, height-2))


def draw_square(screen, x: int, y: int, side: int, color: tuple[int, int, int], fill=True) -> None:
    """
    Draw a square on the screen with specified location, side length, and color
    :param screen: The screen to render the square on
    :param x: The x location of the square on the screen
    :param y: The y location of the square on the screen
    :param side: The length of the side of the square
    :param color: The color of the square
    :param fill: If the square must be drawn inside or only sides
    :return: None
    """
    draw_rect(screen, x, y, side, side, color, fill=fill)


def draw_image(screen, image: str, x: int, y: int, side: int, tick: int, breathing: bool = False) -> None:
    """
    To draw an image on a given surface
    :param screen: The given surface
    :param image: The image to draw on the surface
    :param x: The x location of the drawn image
    :param y: The y location of the drawn image
    :param side: The length of the side of the image
    :param tick: The current tick of the game
    :param breathing: If the image should be animated (breathing) or not
    :return: None
    """

    if image not in images_cache:
        img = pygame.image.load('src/sprite/' + image + '.png')
        img = pygame.transform.scale(img, (side, side))
        images_cache[image] = img
        animations_cache[image] = random.randint(0, 60)

    if breathing:
        tick = math.sin((animations_cache[image] + .5*tick)*math.pi/35)*.05 + 1
    else:
        tick = 1
    img = images_cache[image].copy()
    img = pygame.transform.scale(img, (side, side*tick))
    screen.blit(img, (x, y - img.get_height()*(tick-1)/2))


def draw_entity(screen, loc: tuple[int | float, int | float], hp: int, ratio: float, name: str, tick: int, remaining: int, image: str, player=True) -> None:
    """
    Draw a player or enemy

    :param screen: The screen to render the square on
    :param loc: The x and y location of the entity on the screen
    :param hp: The current health of the entity
    :param ratio: The ratio (from 0.0 to 1.0) of the corresponding health bar completion (0=empty, 1=full)
    :param name: The name of the player or enemy : the text shown between the image and the health bar
    :param tick: The current tick
    :param remaining: The current remaining attack tick
    :param image: The image of the entity
    :param player: If the entity is a player
    :return: None
    """
    global total_between_space, window_width, window_height, o1, o2, w
    boss = name == 'D1'
    x, y = (screen.get_width()//2 - w, -w*.4) if boss else loc
    name = names[name] if name in names.keys() else name

    if name not in list(last_ratios.keys()):
        last_ratios[name] = 1

    draw_image(screen, image, x - w * .3, y + (w//1.6 if player else int(w*1.5)), w * 2 if boss else w*1.3, tick, breathing=ratio>0)

    if ratio > 0:
        draw_health_bar(screen, x + 5, y + w + 35, w - 10, hp, ratio, last_ratios[name], remaining, boss=boss)

    if boss:
        draw_text(screen, screen.get_width()//2, 100, name, (240, 50, 50), font_size=60, center=True, outline_color=(1, 1, 1))
    else:
        draw_text(screen, x + 10, y + w + 10, name, (240, 240, 240) if ratio > 0 else (140, 140, 140))

    if remaining == 0:
        last_ratios[name] = ratio


def handle_events() -> bool:
    """
    Handle all the vents called since the last refresh
    :return: If the game should still be running or not
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
            return False

    return True


def draw_path(screen, xf: int, yf: int, xt: int, yt: int, remaining: int, text: str, color: tuple[int, int, int] | str):
    """
    Draw a text that goes from a point to another one
    :param screen: The screen to draw on
    :param xf: The x of the location of the offender
    :param yf: The y of the location of the offender
    :param xt: The x of the location of the target
    :param yt: The y of the location of the target
    :param remaining: The remaining ticks to hit the target
    :param text: The text to show on the screen
    :param color: The color of the text to show on the screen
    """
    a = (yt - yf) / (xt - xf*1.00000001)
    b = yt - a * xt

    x = xt + (xf - xt) * (remaining / 60)
    y = a * x + b

    draw_text(screen, int(x), int(y), text, color, font='Impact', font_size=50, outline_color=(1, 1, 1), center=True)


def draw_attack(screen, xf: int, yf: int, xt: int, yt: int, remaining: int, attack) -> None:
    """
    Draw an attack going from a certain point to another one on a given screen
    :param screen: The screen to draw on
    :param xf: The x of the location of the offender
    :param yf: The y of the location of the offender
    :param xt: The x of the location of the target
    :param yt: The y of the location of the target
    :param remaining: The remaining ticks to hit the target
    :param attack: The value of the damages
    :return: None
    """
    color = (180, 180, 180) if not attack.hit else ((255, 240, 80) if attack.critical is True else (240, 40, 40))
    text = str(attack.damage)

    draw_path(screen, xf, yf, xt, yt, remaining, text, color)


def draw_heal(screen, xf: int, yf: int, xt: float, yt: int, remaining: int, heal: int) -> None:
    """
    Draw a heal going from a certain point to another one on a given screen
    :param screen: The screen to draw on
    :param xf: The x of the location of the healer
    :param yf: The y of the location of the healer
    :param xt: The x of the location of the target
    :param yt: The y of the location of the target
    :param remaining: The remaining ticks to hit the target
    :param heal: The amount of the heal
    :return: None
    """

    if heal == 0:
        return

    draw_path(screen, xf, yf, int(xt), yt, remaining, f'{"+" if heal > 0 else ""}{heal}', (240, 40, 240) if heal > 0 else (140, 80, 120))
