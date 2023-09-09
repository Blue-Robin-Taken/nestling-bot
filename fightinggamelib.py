"""
I do not give a rats ass about variable naming
make a PR if you care
"""
import random


class FightingGame:
    """
    --- Rules ---
    The move that is left to another move will be vulnerable to that move. It will deal more damage.
    The vulnerable move will deal 20% damage if the last move played was to the right of the current move.
    It is unknown what the last move of the opponent was.
    A defense multiplier is added if the last move of the opponent was vulnerable to the current move AND if the move is defensive.
    """
    move_list = {'dodge': [.5, True], 'kick': [10, False], 'block': [5, True], 'punch': [20, False]}

    def __init__(self, p1, p2, starting_hp):
        self.player_one = p1  # load players
        self.player_two = p2
        self.player_one_hp = starting_hp
        self.player_two_hp = starting_hp
        self.player_one_last_move = None
        self.player_two_last_move = None
        self.current_player = self.player_two
        self.moves = 0

        self.player_one_defense_multiplier = 1
        self.player_two_defense_multiplier = 1

    def exchange_players(self):
        if self.current_player == self.player_one:
            self.current_player = self.player_two
        else:
            self.current_player = self.player_one

    def console_game(self):
        running = True
        while running:
            move = input()
            if move not in self.move_list.keys():
                print('Invalid move')
                continue  # if the move isn't in the list, then restart the loop
            self.play_move(move)
            self.exchange_players()
            dead = self.check_dead()
            if dead:  # will return True if a string is returned
                # running = False
                if dead == 'Player_One_Dead':
                    print(
                        f'Player {self.player_one} was knocked out with a final health score of: {self.player_one_hp}')
                if dead == 'Player_Two_Dead':
                    print(
                        f'Player {self.player_two} was knocked out with a final health score of: {self.player_two_hp}')
                return
            self.moves += 1
            print(f'Player {self.current_player} played move {move}.')
            print(f'The health of {self.player_one}: {self.player_one_hp}.')
            print(f'The health of {self.player_two}: {self.player_two_hp}.')
            print(f'The current move is {self.moves}')

    def play_move(self, move):
        index = list(self.move_list.keys()).index(move)
        bonus_random = random.randint(10, 15) / 10  # random float between 1 and 1.5

        if index >= len(list(self.move_list.keys())) - 1:
            index = -1

        if self.current_player == self.player_one:
            if self.player_two_last_move == list(self.move_list.keys())[index - 1]:
                self.player_two_hp -= self.move_list[move][0] * 1.5 * bonus_random * self.player_one_defense_multiplier
                if not self.move_list[move][1]:
                    self.player_two_defense_multiplier += .2
                print('test')
            elif self.player_two_last_move == list(self.move_list.keys())[index + 1]:
                self.player_two_hp -= self.move_list[move][0] * .2
                print('worked')
            else:
                self.player_two_hp -= self.move_list[move][0] * bonus_random * self.player_one_defense_multiplier

            self.player_one_last_move = move

        if self.current_player == self.player_two:
            if self.player_one_last_move == list(self.move_list.keys())[index - 1]:
                self.player_one_hp -= self.move_list[move][0] * 1.5 * bonus_random * self.player_two_defense_multiplier
                if not self.move_list[move][1]:
                    self.player_one_defense_multiplier += .2
            elif self.player_one_last_move == list(self.move_list.keys())[index + 1]:
                self.player_one_hp -= self.move_list[move][0] * .2
            else:
                self.player_one_hp -= self.move_list[move][0] * bonus_random * self.player_two_defense_multiplier

            self.player_two_last_move = move

    def check_dead(self):
        if self.player_one_hp <= .4:
            return 'Player_One_Dead'
        elif self.player_two_hp <= .4:
            return 'Player_Two_Dead'
        else:
            return False

#
# game = FightingGame('joe', 'bob', 100)
#
# game.console_game()
