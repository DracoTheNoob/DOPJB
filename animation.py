import os

import pygame.image
from pygame import Surface

from draw import Draw
from window import *


class Animation:
    def __init__(self, starting_tick: int, duration: int | None, drawer):
        self.start: int = starting_tick
        self.duration: int = duration
        self.drawer: callable = drawer

    def is_visible(self, tick: int):
        if self.duration is None:
            return self.start <= tick

        return self.start <= tick < self.start + self.duration

    def draw(self, tick: int):
        self.drawer(tick - self.start)


class TextAnimation(Animation):
    def __init__(self, starting_tick: int, x: int, y: int, text: str, font_size: int, font_color: tuple[int, int, int] | str, draw: Draw):
        super().__init__(
            starting_tick, FPS,
            lambda tick: draw.text(font_color, text, x, y, font_size, centering=True)
        )


class MovingTextAnimation(Animation):
    def __init__(self, starting_tick: int, start: tuple[float, float], end: tuple[float, float], text: str, font_size: int, font_color: tuple[int, int, int] | str, draw: Draw):
        super().__init__(
            starting_tick, FPS,
            lambda tick: draw.text(
                font_color, text,
                start[0] + (end[0] - start[0]) * tick / self.duration,
                start[1] + (end[1] - start[1]) * tick / self.duration,
                font_size,
                centering=True
            )
        )


class HealthBarAnimation(Animation):
    def __init__(self, x: float, y: float, height: float, dataset: list[tuple[int, float]], app_draw: Draw):
        super().__init__(0, None, lambda tick: self.draw_bar(tick))

        self.x: float = x
        self.y: float = y
        self.height: float = height
        self.app_draw: Draw = app_draw
        self.dataset: list[tuple[int, float]] = [dataset[0]]

        for row in dataset[1:]:
            self.dataset.append((row[0] - FPS, self.dataset[-1][1]))
            self.dataset.append(row)

    def draw_bar(self, tick: int):
        for i in range(len(self.dataset) - 1):
            start: tuple[int, float] = self.dataset[i]
            end: tuple[int, float] = self.dataset[i + 1]

            if start[0] <= tick < end[0]:
                start_ratio = start[1]
                end_ratio = end[1]
                end_tick = end[0]
                break
        else:
            return

        ratio: float = end_ratio + abs(start_ratio - end_ratio) * (end_tick - tick) / FPS * (-1)**(start_ratio < end_ratio)

        self.app_draw.health_bar(
            self.x, self.y, 30, self.height, ratio,
            white=tick - start[0] < FPS / 4 and (tick - start[0]) % (FPS / 16) < FPS / 32 and start[1] > end[1]
        )


class FramedAnimation(Animation):
    def __init__(self, starting_tick: int, animation_path: str, x: float, y: float, width: float, height: float, app_draw: Draw, loops: int = -1):
        super().__init__(starting_tick, None, lambda tick: self.draw_frame(tick))
        self.app_draw: Draw = app_draw
        self.frames: list[Surface] = []

        for file in os.listdir(animation_path):
            if file.endswith('.png'):
                raw_frame: Surface = pygame.image.load(animation_path + '/' + file)
                scaled_frame: Surface = pygame.transform.scale(raw_frame, (width, height))

                self.frames.append(scaled_frame)

        self.x: float = x
        self.y: float = y
        self.duration = None if loops == -1 else 8 * len(self.frames)

    def draw_frame(self, tick: int):
        self.app_draw.image(
            self.frames[int(tick / 8) % len(self.frames)],
            self.x, self.y, centering=True
        )


class MovingFramedAnimation(Animation):
    def __init__(self, starting_tick: int, animation_path: str, start: tuple[float, float], end: tuple[float, float], width: float, height: float, app_draw: Draw):
        super().__init__(
            starting_tick,
            FPS,
            lambda tick: self.app_draw.image(
                self.frames[int(tick / 8) % len(self.frames)],
                start[0] + (end[0] - start[0]) * tick / self.duration,
                start[1] + (end[1] - start[1]) * tick / self.duration,
                centering=True
            )
        )

        self.app_draw: Draw = app_draw
        self.frames: list[Surface] = []

        for file in os.listdir(animation_path):
            if file.endswith('.png'):
                raw_frame: Surface = pygame.image.load(animation_path + '/' + file)
                scaled_frame: Surface = pygame.transform.scale(raw_frame, (width, height))

                self.frames.append(scaled_frame)
