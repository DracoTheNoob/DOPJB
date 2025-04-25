from rpg import *

FPS: int = 100
TICK_DURATION: float = 1 / FPS

WINDOW_WIDTH: int = 1920
WINDOW_HEIGHT: int = 1080

WINDOW_CAPTION: str = 'Darkness Over Paigibaie'
BACKGROUND_COLOR: tuple[int, int, int] = tuple[int, int, int](60 for _ in range(3))

MARGIN: int = 50
PLAYER_SIZE: int = 200

ENEMY_SIZE: int = 400
ENEMY_X: int = WINDOW_WIDTH - ENEMY_SIZE - MARGIN
ENEMY_Y: int = (WINDOW_HEIGHT - ENEMY_SIZE) // 2

PLAYER_POS: list[tuple[int, int]] = []

ROLE_COLORS: dict[str: tuple[int, int, int]] = {
    ROLE_WARRIOR: (255, 50, 60),
    ROLE_THIEF: (255, 128, 60),
    ROLE_MAGE: (120, 90, 255),
    ROLE_DRUID: (50, 180, 90)
}
