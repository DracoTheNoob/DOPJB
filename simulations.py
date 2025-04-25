import time

from os import path
from random import randint

from fight import Fight
from rpg import *


start: float = time.time()


def get_item(role: str, player_level: int):
    return str(PLAYER_ROLES.index(role) + 1) + str(randint(max(0, player_level - 2), player_level))


def create_team(team_size: int, player_level: int) -> list[Entity]:
    team: list[Entity] = []

    roles: list[str] = {
        3: [ROLE_WARRIOR, ROLE_THIEF, ROLE_DRUID],
        4: PLAYER_ROLES,
        5: PLAYER_ROLES + [ROLE_WARRIOR]
    }[team_size]

    for i in range(team_size):
        role: str = roles[i % (len(roles) - 1)]

        team.append(Entity(
            f'Player {i} lvl {player_level}',
            f'{role}{player_level}',
            get_item(role, player_level),
            get_item(role, player_level)
        ))

    return team


ENEMY_IDENTIFIERS: list[str] = [f'{role}{level}' for role in ENEMY_ROLES for level in range(3 if role != ROLE_DRAGON else 1)]

TEAMS: list[list[list[Entity]]] = [[create_team(team_size, player_level) for team_size in range(3, 6)] for player_level in range(6)]
ENEMIES: dict[str: Entity] = {identifier: Entity('', identifier, '', '') for identifier in ENEMY_IDENTIFIERS}


def simulate(tests: int = 100, decimal_precision: int = 4):
    results: dict[str: list[float]] = {f'{identifier}-{size}': [] for identifier in ENEMY_IDENTIFIERS for size in range(3)}

    for enemy_identifier in ENEMY_IDENTIFIERS:
        base_enemy: Entity = ENEMIES[enemy_identifier]

        for team_size in range(3):
            for player_level in range(6):
                base_team: list[Entity] = TEAMS[player_level][team_size]

                wins: int = 0

                for _ in range(tests):
                    enemy: Entity = base_enemy.clone()
                    team: list[Entity] = [p.clone() for p in base_team]

                    wins += Fight(team, enemy, None).compute()

                results[f'{enemy_identifier}-{team_size}'].append(round((wins / tests) * 10**decimal_precision, 0) / (10 ** (decimal_precision - 2)))

    return results


def output(results: dict[str: list[float]], file_path: str = 'tests/result.xlsx'):
    if not path.isfile(file_path):
        wb: Workbook = Workbook()
        wb.create_sheet('main', 0)
        wb.save(file_path)

        return output(results, file_path=file_path)

    wb: Workbook = load_workbook(file_path, data_only=False)
    sheet: Worksheet = wb['main']

    for i, identifier in enumerate(ENEMY_IDENTIFIERS):
        for team_size in range(3):
            for j in range(6):
                sheet[f'{chr(ord('B') + j + 8*team_size)}1'] = str(j)
                sheet[f'{chr(ord('B') + j + 8*team_size)}{i + 2}'] = results[f'{identifier}-{team_size}'][j] / 100

    wb.save(file_path)


print('\nFiles loaded')
output(simulate())
print(f'duration: {int(100*(time.time() - start)) / 100}s\n')
