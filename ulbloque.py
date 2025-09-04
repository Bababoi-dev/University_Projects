#Nom:Gharbi
#Prénom:Marwa
#Matricule:000603700



#ChatGPT a été utilisé comme outil complémentaire pour corriger et déboguer certaines sections du code,
#ainsi que pour explorer de nouveaux concepts.
# De plus, il a contribué à la création de commentaires explicatifs.
# Il est à noter que ce projet ne favorise pas l'utilisation de ChatGPT comme ressource principale."


from sys import argv
from getkey import getkey


#1-Parsing du fichier

def parse_game(game_file_path: str) -> dict:

    """
    -Analyse un fichier de jeu et retourne un dictionnaire représentant l'état initial
     du jeu de puzzle de voitures.

    :param game_file_path: chemin vers le fichier texte contenant la description du jeu.

    :return:dict : dictionnaire représentant l'état initial du jeu.
    """

    with open(game_file_path,'r') as file:
        lines=file.readlines()

    max_moves=int(lines[-1].strip())
    grid_lines=lines[1:-2] #Enlever les lignes suplimentaire

    grid=[line.strip()[1:-1] for line in grid_lines]

    #Les dimentions
    height=len(grid)
    width=len(grid[0]) if height>0 else 0

    #Voitures
    cars={}
    for y,row in enumerate(grid):
        for x,char in enumerate(row):
            if char!='.':
                if char not  in cars:
                    cars[char]={'start':(x,y),'orientation':None,'length':1}
                else:
                    car=cars[char]
                    if car['orientation'] is None:
                        if x>car['start'][0]:
                            car['orientation']='h'
                        elif y>car['start'][1]:
                            car['orientation']='v'
                    car['length']+=1

    #Organisation par ordre alphabétique
    sorted_cars=sorted(cars.items())
    car_list=[[car['start'],car['orientation'],car['length']] for lettre,car in sorted_cars]

    #Dictionnaire du jeu
    game={
        'width':width,
        'height':height,
        'cars':car_list,
        'max_moves':max_moves,
    }

    return game



#--------------------------------------------------------------------------------------------------------------
#2-Affichage du jeu

def get_game_str(game: dict, current_move_number: int)-> str:
    """
    renvoie une chaîne de caractères représentant l'affichage du plateau de jeu.
    Elle utilise les informations contenues dans le dictionnaire game pour afficher
    les positions actuelles des voitures sur le plateau et le nombre de mouvements effectués.

    :param game: Un dictionnaire représentant l'état actuel du jeu de puzzle de voitures.

    :param current_move_number: Le nombre actuel de mouvements effectués.

    :return:Une chaîne de caractères (str) correspondant à l'affichage du plateau de jeu.
    """

    #Dimensions et voitures
    width=game['width']
    height=game['height']
    cars=game['cars']

    #Initialisation de la grille vide
    EMPTY_CELL=f"\u001b[40m.\u001b[0m"
    grid=[[EMPTY_CELL for  i in range(width)] for j in range(height)]

    #Couleurs des voitures
    COLORS= [
        '\u001b[41m',  # Rouge
        '\u001b[42m',  # Vert
        '\u001b[43m',  # Jaune
        '\u001b[44m',  # Bleu
        '\u001b[45m',  # Magenta
        '\u001b[46m',  # Cyan
    ]

    #Placement les voitures sur la grille
    row_with_A=-1 #ligne contenant la voiture 'A' par défaut
    for index,car in enumerate(cars):
        position,orientation,lenght=car
        x,y=position

        #Couleur et lettre de voiture
        if index==0:
            color='\u001b[47m'
        else:color = COLORS[(index - 1) % len(COLORS)]
        letter = chr(65 + index)


        #Placer les voitures
        for offset in range(lenght):
            if orientation=='h':
                if 0<=x+offset<width:
                    grid[y][x+offset]=f"{color}{letter}\u001b[0m"
            elif orientation=='v':
                if 0<=y+offset<height:
                    grid[y+offset][x]=f"{color}{letter}\u001b[0m"

        #Trouver la ligne contenant la voiture 'A'
        if index==0:
            row_with_A=y

    #Construction avec les bordures
    horizontal_border='-'*(width+2) #Bordure horizental
    game_str=horizontal_border+'\n' #Bordure supérieur

    for row_index,row in enumerate(grid):
        if row_index==row_with_A:
            game_str+='|'+''.join(row)+'\n'
        else:
            game_str+='|'+''.join(row)+'|\n'

    game_str+=horizontal_border #Bordure inférieure

    result=(
        game_str+
        f"\n\nMouvements effectués : {current_move_number}\n" +
        f"Mouvements maximum : {game['max_moves']}\n"
    )
    return result


#--------------------------------------------------------------------------------------------------------------
#3-Déplacer une voiture

def move_car(game: dict, car_index: int, direction: str) -> bool:
    """
    Permet de déplacer une voiture sur le plateau de jeu dans la direction spécifiée.
    Elle vérifie la validité du déplacement avant de mettre à jour la position de la voiture.

    :param game:Dictionnaire représentant l'état actuel du jeu de puzzle de voitures.

    :param car_index:Indice de la voiture à déplacer dans la liste des voitures du dictionnaire game.

    :param direction:Chaîne de caractères représentant la direction du déplacement. Les valeurs attendues sont 'UP', 'DOWN', 'LEFT', 'RIGHT'.

    :return:True : Le déplacement a été effectué avec succès.
           False : Le déplacement n'a pas pu être effectué, par exemple en raison d'un obstacle, d'un mouvement qui ferait sortir de la grille,
           ou d'une direction incohérente avec l'orientation de la voiture.
    """


    height=game['height']
    width=game['width']
    cars=game['cars']

    #Vérification de l'index de la voiture
    if car_index <0 or car_index>len(cars):
        return False

    car=cars[car_index]
    (x,y),orientation,lenght=car

    #Déplacement selon la direction
    dx, dy = 0, 0
    if direction == "UP" and orientation == "v":
        dy = -1
    elif direction == "DOWN" and orientation == "v":
        dy = 1
    elif direction == "LEFT" and orientation == "h":
        dx = -1
    elif direction == "RIGHT" and orientation == "h":
        dx = 1
    else:
        return False

    #Calcul des nouvelles position
    new_position=[
        (x+(i if orientation=='h' else 0)+dx,
         y+(i if orientation=='v' else 0)+dy)
        for i in range(lenght)
    ]

    #Vérification des limites
    for new_x,new_y in new_position:
        if new_x<0 or new_x>=width or new_y<0 or new_y>=height:
            return False

    #Vérification de la collision avec d'autre voiture
    for other_index,other_car in enumerate(cars):
        if other_index==car_index:
            continue
        (other_x,other_y),other_orientation,other_length=other_car
        other_position=[
            (other_x + (i if other_orientation == "h" else 0),
             other_y + (i if other_orientation == "v" else 0))
            for i in range(other_length)
        ]

        if any(pos in other_position for pos in new_position):
            return False

    cars[car_index][0]=(x+dx,y+dy)

    return True

#-------------------------------------------------------------------------------------------------------------------------
#4-Vérification de la victoire

def is_win(game: dict) -> bool:
    """
    Vérifie si le joueur a gagné le jeu de puzzle de voitures.
    Elle détermine si la voiture principale (la première voiture de la liste) a atteint la position de sortie.

    :param game: Dictionnaire représentant l'état actuel du jeu de puzzle de voitures.

    :return:True : Le joueur a gagné, c'est-à-dire que la voiture principale a atteint la position de sortie.
            False : Le joueur n'a pas encore gagné
    """
    width = game["width"]

    car_player_A = game['cars'][0]
    start_position, orientation, length = car_player_A

    # verifier la sortie
    x, y = start_position
    if orientation == "h" and x + length == width:
        return True

    return False




#-----------------------------------------------------------------------------------------------------------------------------------------
#5-Démarage/Boucle de la partie

def play_game(game: dict) -> int:
    """
    Permet de jouer au jeu de puzzle de voitures en utilisant les informations contenues dans le dictionnaire game.

    :param game: Dictionnaire représentant l'état initial du jeu de puzzle de voitures.

    :return: 0 : Le joueur a gagné.
             1 : Le joueur a perdu (le nombre de mouvements maximum a été dépassé).
             2 : Le joueur est toujours en jeu (le jeu continue).

    """
    max_moves = game['max_moves']
    current_moves = 0
    last_car_index = None  #  Mémoriser la dernière voiture choisie

    # Affichage de l'état initial du jeu
    print(get_game_str(game, current_moves))

    while current_moves < max_moves:

        # Choix de voiture ou de direction
        print('Select a car (A-Z) to move or a direction (←, ↑, →, ↓):')
        user_input = getkey()

        if user_input == 'ESCAPE':  # Touche ESC pour quitter
            print('You quit the game.')
            return 2

        # Vérification si l'entrée est une direction
        if user_input in ['UP', 'DOWN', 'LEFT', 'RIGHT']:

            if last_car_index is not None:  # Vérifie si une voiture est déjà sélectionnée
                direction = user_input

                if move_car(game, last_car_index, direction):
                    current_moves += 1
                    print('Car moved successfully.')
                else:
                    print('Invalid move. Try again.')

            else:
                # Aucune voiture sélectionnée précédemment
                print('No car selected. Please select a car first.')

        else:

            # Vérification si l'entrée est une voiture valide
            if len(user_input) == 1 and 'A' <= user_input.upper() <= 'Z':
                car_index = ord(user_input.upper()) - ord('A')

                if car_index < len(game['cars']):
                    last_car_index = car_index
                    print(f'Car {user_input.upper()} selected.')

                else:
                    print('This car does not exist. Try again.')

            else:
                print('Invalid input. Please select a valid car or direction.')

        # Affichage de l'état actuel du jeu
        print(get_game_str(game, current_moves))
        print('---------------------------------------------------------------')

        # Vérification de la victoire
        if is_win(game):
            return 0

    # Si le nombre de mouvements max est dépassé
    return 1



#-----------------------------------------------------------------------------------------------------------------------
#6-Jouer

def main():
    if len(argv)<2:
        print("Usage: python script.py <path_to_game_file>")
        return

    game_file_path=argv[1]

    try:
        game=parse_game(game_file_path)
    except FileNotFoundError:
        print("Error:File not found!")
        return
    except ValueError as e:
        print(f'Error: {e}')
        return

    #lancer le jeu
    result=play_game(game)

    if result==0:
        print("you won")
    elif result==1:
        print('You lost! Maximum moves exeded')
    elif result==2:
        print("Game abandoned!")
    else:
        print("unexpected error")




if __name__ == '__main__':
    main()






























































    