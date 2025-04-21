import json
import time

import pygame.transform

from no_print_core import Fight, Player, Entity
from drawing import draw_entity, draw_text, draw_attack, draw_heal, boring_calculations

pygame.init()

info = pygame.display.Info()
background = None

total_between_space, window_width, window_height, o1, o2, w, x_enemy, y_enemy = 0, 0, 0, 0, 0, 0, 0, 0


def get_no_digit(text: str) -> str:
    return text[:min([text.find(str(k)) if str(k) in text else len(text) for k in list(range(0, 10))])]


def handle_display(screen, fight: Fight, remaining: int, tick: int) -> None:
    players: list[Player] = fight.players
    dead_players: list[Player] = fight.dead_players
    enemy: Entity = fight.enemy

    screen.blit(background, (0, 0))

    # show alive players
    for i in range(len(players)):
        r = players[i].role
        hp = players[i].hp

        x_player = o1 + i * (o2 + w)
        y_player = window_height - w - o2

        draw_entity(
            screen=screen,
            loc=(x_player, y_player),
            hp=hp,
            ratio=hp / players[i].max_hp,
            name=f'{players[i].name}',
            tick=tick,
            remaining=remaining,
            image=f'class-{r}'
        )

    # show dead players
    for i in range(len(dead_players)):
        r = dead_players[i].role

        draw_entity(
            screen=screen,
            loc=(o1 + (i + len(players)) * (o2 + w), window_height - w - o2),
            hp=0,
            ratio=0,
            name=f'{dead_players[i].name}',
            tick=tick,
            remaining=remaining,
            image=f'class-{r}'
        )

    # show enemy
    draw_entity(
        screen=screen,
        loc=(x_enemy - w/2, y_enemy - w/2),
        hp=enemy.hp,
        ratio=enemy.hp / enemy.max_hp,
        name=f'{enemy.name}',
        tick=tick,
        remaining=remaining,
        image=f'enemy-{get_no_digit(enemy.name)}',
        player=False
    )

    if fight.current_state == 'idle':
        for i in range(len(fight.attacks)):
            # coordinates of the targeted player
            attack = fight.attacks[i]
            target_id = fight.players.index(fight.get_player_by_name(fight.enemy.targets[i]))
            x = int(o1 + target_id * (o2 + w) + w / 2)
            y = int(window_height - o2)

            # render the attack
            offset = 0 if fight.attacks[i].hit and not fight.attacks[i].damage == 0 else w*.75
            draw_attack(screen, x_enemy, y_enemy + w, x, y - offset, remaining, attack)

    for i in range(len(fight.players)):
        if i == 0 and fight.current_state == 'enemy' or fight.current_state == f'p{i}':
            x_player = int(o1 + w / 2 + i * (o2 + w))
            y_player = window_height - o2
            offset = 0 if fight.attacks[0].hit else w*1.2
            y = y_enemy + int(w*1.5) - offset

            draw_attack(screen, x_player, y_player, x_enemy, y, remaining, fight.attacks[0])
            break

    if fight.get_next_state() == 'heal' and fight.heals[0] != 0:
        for i in range(len(fight.players)):
            if fight.heals[i] == 0:
                continue

            x = int(o1 + i * (o2 + w) + w / 2)
            y = int(window_height - w / 2 - o2)

            draw_heal(screen, int(window_width / 2), int(window_height / 2), x, y, remaining, fight.heals[i])

        if fight.heals[-1] != 0:
            x = x_enemy
            y = y_enemy + w
            draw_heal(screen, x, y, x + .000001, y, remaining, fight.heals[-1])

    pygame.display.flip()


def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return False

    return True


def load_fight():
    # load players from json configuration file
    players_configuration_file = open('data/players.json', 'r')
    players_configuration = json.load(players_configuration_file)
    players_configuration_file.close()
    del players_configuration_file

    # load enemy from json configuration file
    enemy_configuration_file = open('data/level.json', 'r')
    enemy_configuration = json.load(enemy_configuration_file)
    enemy_id = enemy_configuration['enemy_id']
    enemy_configuration_file.close()
    del enemy_configuration_file
    del enemy_configuration

    return Fight(players_configuration, enemy_id)


def load_pygame():
    pygame.font.init()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()

    global total_between_space, window_width, window_height, o1, o2, w
    total_between_space, window_width, window_height, o1, o2, w = boring_calculations(screen, .65)

    global x_enemy, y_enemy
    x_enemy = int(window_width / 2)
    y_enemy = int(o1 + w)

    return screen, clock


def main():
    fight: Fight = load_fight()
    screen, clock = load_pygame()

    global background

    background = pygame.image.load(f'src/sprite/background-{get_no_digit(fight.enemy.name)}.png')
    background = background.convert()
    background = pygame.transform.scale(background, (info.current_w, info.current_h))

    tick: int = 0
    attack_remaining: int = 0
    animation_tick: int = 0
    running: bool = True
    escape_pressed = False

    while running:
        escape_pressed = not handle_events()
        animation_tick += 1

        if tick == 70:
            fight.next_action()

            attack_remaining = 60

            running = not escape_pressed and fight.running
            tick = 0
        else:
            tick += 1
            running = not escape_pressed

        attack_remaining = max(attack_remaining - 1, 0)

        if escape_pressed:
            break

        handle_display(screen, fight, attack_remaining, animation_tick)
        clock.tick(60)

    if escape_pressed:
        pygame.quit()
        return

    # show last screen
    win = fight.enemy.hp <= 0
    color = (0, 240, 0) if win else (240, 0, 0)
    text = 'Victoire !' if win else 'Défaite...'
    x, y = screen.get_width() // 2, screen.get_height() // 2

    screen.blit(background, (0, 0))
    draw_text(screen, x, y, text, color, font_size=screen.get_height() // 6, center=True)

    pygame.display.flip()

    time.sleep(5.0)
    pygame.quit()


if __name__ == '__main__':
    main()
