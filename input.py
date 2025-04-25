import sys, json

from os import path

from rpg import PLAYER_ROLES, ENEMY_ROLES, ROLE_DRAGON, ENEMY_NAMES

COMMAND_PLAYERS: str = 'players'  # Type each player data individually
COMMAND_ENEMY: str = 'enemy'  # Type the enemy role
COMMAND_TEAMS: str = 'teams'  # Type one or multiple teams structure
COMMAND_TEAM: str = 'team'  # Type players data without those which are already given from the 'teams' option, such as the number of players, the roles, etc.

COMMANDS: list[str] = [COMMAND_PLAYERS, COMMAND_ENEMY, COMMAND_TEAMS, COMMAND_TEAM]
COMMAND_PREFIX: str = '-cmd='

PATH_PLAYERS: str = 'data/players.json'
PATH_ENEMY: str = 'data/enemy.json'
PATH_TEAMS: str = 'data/teams.json'

DELIMITER: str = '-' * 30


def write(destination: str, json_data: dict):
    with open(destination, 'w', encoding='utf-8') as file:
        file.write(json.dumps(json_data, ensure_ascii=False, indent=4))


def ask_in(sentence: str, choices: list[str], show_choices: bool | str = False) -> str:
    if type(show_choices) is bool:
        if show_choices is True:
            sentence = f'{sentence} ({choices}) : '
        else:
            sentence = f'{sentence} : '
    else:
        sentence = f'{sentence} ({show_choices}): '

    answer: str = input(sentence)

    if len(choices) == 0:
        return answer

    while answer not in choices:
        print(f'Valeur incorrecte (possibilitées : {choices})')
        answer = input(sentence)

    return answer


def get_teams() -> dict[str: list[dict]]:
    if not path.isfile(PATH_TEAMS):
        write(PATH_TEAMS, {'teams': {}})

    teams_json: dict = json.load(fp=open(PATH_TEAMS, 'r', encoding='utf-8'))
    return teams_json['teams']


def main(command: str):
    if command == COMMAND_PLAYERS:
        nb_players: int = int(ask_in('Nombre de joueur', [str(n) for n in range(3, 6)]))
        print(DELIMITER)

        json_data: dict = {
            'players': []
        }

        for i in range(1, nb_players + 1):
            json_data['players'].append(
                {
                    'name': ask_in(f'[{i}/{nb_players}] Nom \t', []),
                    'role': ask_in(f'[{i}/{nb_players}] Classe', PLAYER_ROLES),
                    'level': int(ask_in(f'[{i}/{nb_players}] Niveau', [str(n) for n in range(0, 7)])),
                    'weapon_id': ask_in(f'[{i}/{nb_players}] Arme\t', []),
                    'object_id': ask_in(f'[{i}/{nb_players}] Objet\t', [])
                }
            )

            print(DELIMITER)

        write(PATH_PLAYERS, json_data)
    elif command == COMMAND_ENEMY:
        role: str = ask_in('Ennemi', ENEMY_ROLES)
        level: int = int(ask_in('Niveau', ['1', '2', '3'] if role != ROLE_DRAGON else ['1'])) if role != ROLE_DRAGON else 1

        json_data: dict = {
            'name': ENEMY_NAMES[(role, level)],
            'identifier': f'{role}{level}'
        }

        write(PATH_ENEMY, json_data)
    elif command == COMMAND_TEAMS:
        teams: dict[str: list[dict]] = get_teams()
        first: bool = True

        while first or ask_in('Continuer la saisie ', ['yes', 'no', 'y', 'n'], show_choices=True).lower() in ['y', 'yes']:
            first = False
            print(DELIMITER)

            team_id: str = str(len(teams.keys()) + 1)
            print(f'Identifiant de l\'équipe : {team_id}')

            nb_players: int = int(ask_in('Nombre de joueur', [str(n) for n in range(3, 6)]))
            print()

            players: list[dict] = []

            for i in range(1, nb_players + 1):
                players.append({
                    'name': ask_in(f'[{i}/{nb_players}] Nom \t', []),
                    'role': ask_in(f'[{i}/{nb_players}] Classe', PLAYER_ROLES)
                })

                print()

            print(DELIMITER)

            teams[team_id] = players
        else:
            write(PATH_TEAMS, {'teams': teams})
    elif command == COMMAND_TEAM:
        team: list[dict] = get_teams()[ask_in('Identifiant de l\'équipe', [])]
        nb_players: int = len(team)

        for i in range(nb_players):
            team[i]['level'] = int(ask_in(f'[{i+1}/{nb_players} - {team[i]['name']} - {team[i]['role']}] Niveau', [str(n) for n in range(0, 7)]))
            team[i]['weapon_id'] = ask_in(f'[{i+1}/{nb_players} - {team[i]['name']} - {team[i]['role']}] Arme  ', [])
            team[i]['object_id'] = ask_in(f'[{i+1}/{nb_players} - {team[i]['name']} - {team[i]['role']}] Objet ', [])

            print()

        print(team)

        write(PATH_PLAYERS, {'players': team})


if __name__ == '__main__':
    args = sys.argv[1:]

    for arg in args:
        if arg.startswith(COMMAND_PREFIX):
            cmd = arg[len(COMMAND_PREFIX):]

            if cmd in COMMANDS:
                main(cmd)
                exit(0)
            else:
                print(f'Command name not recognized : \'{cmd}\' not in {COMMANDS}')
                exit(2)
    else:
        print(f'No command was specified, please run \'py {__file__[__file__.rfind('\\') + 1:]} -cmd={COMMANDS}\'')
        exit(1)
