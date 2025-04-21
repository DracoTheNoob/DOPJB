def ask_integer(prompt: str, bounds: tuple[int, int] = (0, 1000)) -> int:
    value = input(prompt)

    while not value.isdigit() or not (bounds[0] <= int(value) <= bounds[1]):
        value = input(f'Entrée invalide ("{value}")\n{prompt}')

    return int(value)


def ask_str(prompt: str, min_length: int = 1) -> str:
    value = input(prompt)

    while len(value) < min_length or value == ' ':
        value = input(f'Entrée invalide, taille minimale du texte : {min_length} ("{value}")\n{prompt}')

    return value


def ask_specific(prompt: str, possibilities: list[str]) -> str:
    value = input(prompt)

    while value not in possibilities:
        value = input(f'Entrée invalide ! Il faut une des possibilités parmis : {possibilities} ("{value}")\n{prompt}')

    return value


players_amount = ask_integer('Entrez le nombre de joueurs (3-5) : ', bounds=(3, 5))
print()

json = {}

for i in range(players_amount):
    player = {}

    name = ask_str(f'Nom du joueur n°{i} : ')

    while name in list(json.keys()):
        print('Ce nom a déjà été entré, veuillez en choisir un autre\n')
        name = ask_str(f'Nom du joueur n°{i} : ')

    player['role'] = ask_specific(f'Role du joueur n°{i} (G=guerrier, V=voleur, M=mage, D=druide) : ', possibilities=['G', 'V', 'M', 'D'])
    player['level'] = ask_integer(f'Niveau du joueur n°{i} (0-5) : ', bounds=(0, 5))
    player['weapon'] = input(f'Identifiant de l\'arme du joueur n°{i} : ')
    player['item'] = input(f'Identifiant de l\'objet du joueur n°{i} : ')

    json[name] = player

    print()

with open('data/players.json', 'w+') as file:
    file.write(str(json).replace("'", '"'))

print('Fichier généré')
