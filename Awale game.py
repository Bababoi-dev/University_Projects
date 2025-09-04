# Constantes
PLAYER_1 = 0
PLAYER_2 = 1
BOARD_SIZE = 6  # Nombre de case par plateau
CAPTURE_VALUES = [2, 3]  # Valeurs qui permettent la capture

#-----------------------------------------------------------------------------------------------

def simulate_move(board, player, cell):
    """
    Simule un mouvement et retourne le nouvel état du plateau, les graines capturées et la validité du coup.

    Args:
        board (list): Le plateau de jeu
        player (int): Le joueur qui joue (0 ou 1).
        cell (int): La case choisie par le joueur.

    Returns:
        tuple: (new_board, captured_seeds, is_valid)
            - new_board: Plateau mis à jour après le coup
            - captured_seeds: Nombre de graines capturées
            - is_valid: Si le coup est valide (n'affame pas l'adversaire)
    """

    max_cell = len(board[0]) - 1
    opponent = 1 - player

    # Copier le plateau pour la simulation
    new_board = [row[:] for row in board]

    # Vérifier si la case contient des graines
    if new_board[player][cell] == 0:
        return new_board, 0, False

    # Prendre les graines de la case
    seeds_in_hand = new_board[player][cell]
    new_board[player][cell] = 0

    # Distribuer les graines
    current_row = player
    current_cell = cell

    while seeds_in_hand > 0:
        current_cell += 1
        # Si on atteint la fin d'une rangée, passer à la rangée adverse
        if current_cell > max_cell:
            current_row = 1 - current_row #Changée de rangée
            current_cell = 0

        # Déposer une graine
        new_board[current_row][current_cell] += 1
        seeds_in_hand -= 1

    # Vérifier les captures si la dernière graine tombe dans la rangée adverse
    captured_seeds = 0
    if current_row != player:  # Si on termine dans la rangée adverse
        cap_cell = current_cell

        # Capturer en arrière tant que les cases contiennent 2 ou 3 graines
        while cap_cell >= 0 and new_board[current_row][cap_cell] in CAPTURE_VALUES:
            captured_seeds += new_board[current_row][cap_cell]
            new_board[current_row][cap_cell] = 0
            cap_cell -= 1

    # Vérifier si l'adversaire serait affamé
    if sum(new_board[opponent]) == 0:
        return new_board, captured_seeds, False

    return new_board, captured_seeds, True

#---------------------------------------------------------------------------------------------------
# Fonction play:
def play(board, player: int, cell: int) -> int:
    """
    Joue un coup pour un joueur sur une case donnée du plateau.

    Args:
        board (list): Le plateau de jeu
        player (int): Le joueur qui joue (0 ou 1).
        cell (int): La case choisie par le joueur.

    Returns:
        int: Le nombre de graines récoltées par le joueur à ce tour.
    """
    max_cell = len(board[0]) - 1

    #Vérification des entrées
    if player not in [PLAYER_1, PLAYER_2]:
        raise ValueError("Le joueur doit être 0 ou 1")
    if cell < 0 or cell > max_cell:
        raise ValueError(f"La cellule doit être comprise entre 0 et {max_cell}")
    if board[player][cell] == 0:
        raise ValueError('La cellule choisie est vide')

    # Faire une simulation
    _, _, is_valid = simulate_move(board, player, cell)

    if not is_valid:
        raise ValueError("Ce mouvement affamerait l’adversaire, ce qui est interdit !")

    # Jouer le coup :

    # Prendre les graines
    seeds_in_hand = board[player][cell]
    board[player][cell] = 0

    # Distribue les graines
    current_row = player
    current_cell = cell

    while seeds_in_hand > 0:
        current_cell += 1
        if current_cell > max_cell:
            current_row = 1 - current_row #Changement de rangée
            current_cell = 0

        board[current_row][current_cell] += 1
        seeds_in_hand -= 1

    # Captures des graines
    captured_seeds = 0
    if current_row != player:
        opponent_row = current_row
        while current_cell >= 0 and board[opponent_row][current_cell] in CAPTURE_VALUES:
            captured_seeds += board[opponent_row][current_cell]
            board[opponent_row][current_cell] = 0
            current_cell -= 1

    return captured_seeds

#------------------------------------------------------------------------------------------------------
#FONCTION is_end :

def is_end(board, player: int) -> bool:
    """
    Vérifie si la partie est terminée pour un joueur donné.

    Args:
        board (list): Le plateau de jeu
        player (int): Le joueur dont c'est le tour (0 ou 1).

    Returns:
        bool: True si la partie est terminée, False sinon.
    """
    # Si le joueur n'a pas de graines,GAME OVER.
    if sum(board[player]) == 0:
        return True

    # Vérifier si le joueur peut jouer un coup valide
    for cell in range(BOARD_SIZE):
        if board[player][cell] > 0:
            # Utiliser la fonction simulate_move
            _, _, is_valid = simulate_move(board, player, cell)
            if is_valid:
                return False  # On trouve au moins un coup valide

    # Pas de coup valide
    return True

#-------------------------------------------------------------------------------------------------------------
#FONCTION enum:
def enum(board, player: int, depth: int) -> list[tuple[list[int], int]]:
    """
    Énumère toutes les suites de coups possibles avec leur score final pour une profondeur donnée.

    Args:
        board: Plateau de jeu
        player: Joueur dont c'est le tour (0, 1)
        depth: Profondeur restante de recherche

    Returns:
        list[tuple[list[int],int]]: Liste de tuples (suite de mouvements, score final)
    """
    #Fonction auxiliaire récurtsive
    def enum_helper(current_board, current_player, remaining_depth, moves=None, p1_score=0, p2_score=0):
        """
        Fonction auxiliaire récursive pour enum qui explore toutes les suites de coups possibles.
        Args:
            current_board: État actuel du plateau de jeu
            current_player: Joueur dont c'est le tour (0 ou 1)
            remaining_depth: Profondeur restante à explorer
            moves: Liste des coups déjà joués dans cette branche
            p1_score: Score accumulé du Joueur 1
            p2_score: Score accumulé du Joueur 2

        Returns:
            list[tuple[list[int],int]]: Liste de tuples contenant (séquence de coups, score final)
                                        pour toutes les branches d'exploration possibles

        """
        if moves is None:
            moves = []

        # Cas de base:Profondeur atteinte ou fin de partie
        if remaining_depth == 0 or is_end(current_board, current_player):
            final_score = p1_score - p2_score
            return [(moves.copy(), final_score)]

        results = []
        opponent = 1 - current_player

        #Essayer tous les coups possibles pour le joueur actuel
        for cell in range(BOARD_SIZE):
            if current_board[current_player][cell] > 0:
                # Utiliser la fonction simulate_move pour simuler le coup
                new_board, captured, is_valid = simulate_move(current_board, current_player, cell)

                if not is_valid:
                    continue  # Coup invalide, passer au suivant

                # Ajouter le coup à la séquence
                new_moves = moves.copy()
                new_moves.append(cell)

                # Mettre à jour les scores
                new_p1_score = p1_score + (captured if current_player == PLAYER_1 else 0)
                new_p2_score = p2_score + (captured if current_player == PLAYER_2 else 0)

                # Récursion avec le joueur suivant
                sub_results = enum_helper(new_board, opponent, remaining_depth - 1,new_moves, new_p1_score, new_p2_score)

                #Ajouter les résultats à la liste globale
                results.extend(sub_results)

        return results

    #Appel initial à la fonction auxiliaire
    return enum_helper(board, player, depth)

#--------------------------------------------------------------------------------------------------
#FONCTION suggest :

def suggest(board, player: int, depth: int) -> int:
    """
    Détermine le meilleur coup pour un joueur donné en utilisant l'algorithme MinMax.

    Args:
        board: Plateau de jeu actuel
        player: Joueur pour lequel on cherche le meilleur coup (0 ou 1)
        depth: Profondeur de recherche

    Returns:
        L'indice de la meilleure case à jouer (0-5)
    """

    def simulate_move_for_minmax(current_board, current_player, move):
        """
        Simule un déplacement pour l'algorithme MinMax.

        Args:
            current_board: Plateau de jeu
            current_player: Joueur actuel
            move: Coup à jouer

        Returns:
            tuple: (nouveau_plateau, graines_capturées) ou (None, 0) si coup invalide"""

        #Utilisation de la fonction de simulation
        new_board, captured, is_valid = simulate_move(current_board, current_player, move)

        if not is_valid:
            return None, 0

        return new_board, captured

    def minmax(current_board, current_player, remaining_depth, p1_score=0, p2_score=0):
        """
        Implémentation de l'algorithme MinMax.

        Args:
            current_board: Plateau de jeu actuel
            current_player: Joueur dont c'est le tour
            remaining_depth: Profondeur restante à explorer
            p1_score: Score cumulé du joueur 1
            p2_score: Score cumulé du joueur 2

        Returns:
            tuple: (meilleur_coup, meilleur_score)"""


        # Cas de base: profondeur atteinte ou fin de partie
        if remaining_depth == 0 or is_end(current_board, current_player):
            return None, p1_score - p2_score

        # Le joueur actuel cherche à optimiser son propre score
        opponent = 1 - current_player

        # Initialiser le meilleur score selon le joueur
        if current_player == player:  # Tour du joueur
            best_score = float('-inf')
        else:  # Tour de l'adversaire
            best_score = float('inf')

        best_move = None

        # Essayer tout les coups possibles
        for move in range(BOARD_SIZE):
            # Vérifier si la case contient des graines
            if current_board[current_player][move] > 0:
                # Simuler le coup
                result = simulate_move_for_minmax(current_board, current_player, move)


                # Si le coup est invalide (affame l'adversaire), passer au suivant
                if result[0] is None:
                    continue

                new_board, captured = result

                #Mettre à jour les scores
                new_p1_score = p1_score + (captured if current_player == PLAYER_1 else 0)
                new_p2_score = p2_score + (captured if current_player == PLAYER_2 else 0)

                # Appel récursif pour l'adversaire
                _, score = minmax(new_board, opponent, remaining_depth - 1,new_p1_score, new_p2_score)

                # Mettre à jour le meilleur coup si nécessaire

                if current_player == player:  # Maximiser pour le joueur initial
                    if score > best_score:
                        best_score = score
                        best_move = move
                else:  # Minimiser pour l'adversaire
                    if score < best_score:
                        best_score = score
                        best_move = move

        # Si aucun coup n'a été trouvé
        if best_move is None:
            return None, p1_score - p2_score

        return best_move, best_score

    # lancer l'algorithme MinMax
    best_move, _ = minmax(board, player, depth)
    return best_move