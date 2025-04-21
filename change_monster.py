def ask_specific(prompt: str, possibilities: list[str]) -> str:
    value = input(prompt)

    while value not in possibilities:
        value = input(f'Entrée invalide ! Il faut une des possibilités parmis : {possibilities} ("{value}")\n{prompt}')

    return value


monsters = ['P1', 'P2', 'P3', 'L1', 'L2', 'L3', 'MV1', 'MV2', 'MV3', 'D1']
new_monster = ask_specific('Entrez l\'identifiant du nouveau monstre : ', possibilities=monsters)

content = str({"enemy_id": new_monster}).replace("'", '"')

with open('data/level.json', 'w+') as file:
    file.write(content)

print('Valeur modifiée')
