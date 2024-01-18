import tkinter as tk
from tkinter import ttk
import numpy as np
import random as rd
from threading import Thread
from queue import Queue

disk_color = ['white', 'red', 'yellow']
disks = list()

MAX_Value = 100000
MIN_Value = -100000

player_type = ['human']
for i in range(42):
    player_type.append('AI: alpha-beta level ' + str(i + 1))


def alpha_beta_decision(board, turn, ai_level, queue, max_player):
    player = max_player
    best_move = board.get_possible_moves()[0]
    best_value = MIN_Value
    A = MIN_Value
    B = MAX_Value
    for move in board.get_possible_moves():
        new_board = board.copy()
        new_board.add_disk(move, player, False)
        value = min_value_AB(new_board, turn + 1, ai_level, player % 2 + 1, A, B, max_player)
        if value > best_value:
            best_value = value
            best_move = move
    queue.put(best_move)


def min_value_AB(board, turn, ia_level, player, A, B, ia_player):
    if board.check_victory():
        return MAX_Value
    elif turn > 42:
        return 0
    elif ia_level == 0:
        return board.eval(ia_player)
    value = MAX_Value
    for move in board.get_possible_moves():
        new_board = board.copy()
        new_board.add_disk(move, player, False)
        value = min(value, max_value_AB(new_board, turn + 1, ia_level - 1, player % 2 + 1, A, B, ia_player))
        if value <= A:
            return value
        B = min(B, value)
    return value


def max_value_AB(board, turn, ia_level, player, A, B, ia_player):
    if board.check_victory():
        return MIN_Value
    elif turn > 42:
        return 0
    elif ia_level == 0:
        return board.eval(ia_player)
    value = MIN_Value
    for move in board.get_possible_moves():
        new_board = board.copy()
        new_board.add_disk(move, player, False)
        value = max(value, min_value_AB(new_board, turn + 1, ia_level - 1, player % 2 + 1, A, B, ia_player))
        if value >= B:
            return value
        A = max(A, value)
    return value


class Board:
    grid = np.array([[0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0]])

    def eval(self, ia_player):
        r = 0
        for i in range(7):
            for j in range(6):
                if i < 4:
                    if j < 3:
                        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
                    else:
                        directions = [(0, 1), (-1, 1)]
                elif j < 3:
                    directions = [(1, 0)]
                else:
                    directions = []
                if self.grid[i][j] == ia_player:
                    r += self.check_three_empty(ia_player, i, j, directions, 0)
                elif self.grid[i][j] == ia_player % 2 + 1:
                    r -= self.check_three_empty(ia_player % 2 + 1, i, j, directions, 0)
                else:
                    r += self.check_three_empty(ia_player, i, j, directions, (i, j))
                    r -= self.check_three_empty(ia_player % 2 + 1, i, j, directions, (i, j))
        return 1 if r == 0 else r

    def check_three_empty(self, player, row, col, directions, cell):  # Vérifie un allignement de trois avec une case vide

        reward = 0
        for direction in directions:
            count = 1 if cell != 0 else 0   # Nombre de pions alignés
            empty_cell = cell               # Vérifie cellule vide

            # Parcourt des trois positions suivantes dans la direction donnée
            for i in range(1, 4):
                dx, dy = direction
                new_row, new_col = row + i * dx, col + i * dy

                # Vérifie si la nouvelle position est à l'intérieur du plateau
                if 0 <= new_row < 7 and 0 <= new_col < 6:
                    if self.grid[new_row][new_col] == player:
                        count += 1
                    elif self.grid[new_row][new_col] == 0 and empty_cell == 0:
                        empty_cell = (new_row, new_col)
                    else:
                        return 0
                else:
                    return 0

            # Si trois pions de la même couleur sont alignés avec un emplacement vide
            if count == 3 and empty_cell != 0:
                reward += 7
                for k in range(empty_cell[0]):
                    if self.grid[empty_cell[0]-k][empty_cell[1]] == 0:
                        reward -= 0.5
            """
            # Si deux pions de la même couleur
            elif count == 2:
                reward = 2
            """

        return reward


    def copy(self):
        new_board = Board()
        new_board.grid = np.array(self.grid, copy=True)
        return new_board

    def reinit(self):
        self.grid.fill(0)
        for i in range(7):
            for j in range(6):
                canvas1.itemconfig(disks[i][j], fill=disk_color[0])

    def get_possible_moves(self):
        possible_moves = list()
        if self.grid[3][5] == 0:
            possible_moves.append(3)
        for shift_from_center in range(1, 4):
            if self.grid[3 + shift_from_center][5] == 0:
                possible_moves.append(3 + shift_from_center)
            if self.grid[3 - shift_from_center][5] == 0:
                possible_moves.append(3 - shift_from_center)
        return possible_moves

    def add_disk(self, column, player, update_display=True):
        for j in range(6):
            if self.grid[column][j] == 0:
                break
        self.grid[column][j] = player
        if update_display:
            canvas1.itemconfig(disks[column][j], fill=disk_color[player])

    def column_filled(self, column):
        return self.grid[column][5] != 0

    def check_victory(self):
        # Horizontal alignment check
        for line in range(6):
            for horizontal_shift in range(4):
                if self.grid[horizontal_shift][line] == self.grid[horizontal_shift + 1][line] == \
                        self.grid[horizontal_shift + 2][line] == self.grid[horizontal_shift + 3][line] != 0:
                    return True
        # Vertical alignment check
        for column in range(7):
            for vertical_shift in range(3):
                if self.grid[column][vertical_shift] == self.grid[column][vertical_shift + 1] == \
                        self.grid[column][vertical_shift + 2] == self.grid[column][vertical_shift + 3] != 0:
                    return True
        # Diagonal alignment check
        for horizontal_shift in range(4):
            for vertical_shift in range(3):
                if self.grid[horizontal_shift][vertical_shift] == self.grid[horizontal_shift + 1][vertical_shift + 1] == \
                        self.grid[horizontal_shift + 2][vertical_shift + 2] == self.grid[horizontal_shift + 3][
                    vertical_shift + 3] != 0:
                    return True
                elif self.grid[horizontal_shift][5 - vertical_shift] == self.grid[horizontal_shift + 1][
                    4 - vertical_shift] == \
                        self.grid[horizontal_shift + 2][3 - vertical_shift] == self.grid[horizontal_shift + 3][
                    2 - vertical_shift] != 0:
                    return True
        return False


class Connect4:

    def __init__(self):
        self.board = Board()
        self.human_turn = False
        self.turn = 1
        self.players = (0, 0)
        self.ai_move = Queue()

    def current_player(self):
        return 2 - (self.turn % 2)

    def launch(self):
        self.board.reinit()
        self.turn = 0
        information['fg'] = 'black'
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        self.human_turn = False
        self.players = (combobox_player1.current(), combobox_player2.current())
        self.handle_turn()

    def move(self, column):
        if not self.board.column_filled(column):
            self.board.add_disk(column, self.current_player())
            self.handle_turn()

    def click(self, event):
        if self.human_turn:
            column = event.x // row_width
            self.move(column)

    def ai_turn(self, ai_level):
        Thread(target=alpha_beta_decision,
               args=(self.board, self.turn, ai_level, self.ai_move, self.current_player(),)).start()
        self.ai_wait_for_move()

    def ai_wait_for_move(self):
        if not self.ai_move.empty():
            self.move(self.ai_move.get())
        else:
            window.after(100, self.ai_wait_for_move)

    def handle_turn(self):
        self.human_turn = False
        if self.board.check_victory():
            information['fg'] = 'red'
            information['text'] = "Player " + str(self.current_player()) + " wins !"
            return
        elif self.turn >= 42:
            information['fg'] = 'red'
            information['text'] = "This a draw !"
            return
        self.turn = self.turn + 1
        information['text'] = "Turn " + str(self.turn) + " - Player " + str(
            self.current_player()) + " is playing"
        if self.players[self.current_player() - 1] != 0:
            self.human_turn = False
            self.ai_turn(self.players[self.current_player() - 1])
        else:
            self.human_turn = True


game = Connect4()

# Graphical settings
width = 700
row_width = width // 7
row_height = row_width
height = row_width * 6
row_margin = row_height // 10

window = tk.Tk()
window.title("Connect 4")
canvas1 = tk.Canvas(window, bg="blue", width=width, height=height)

# Drawing the grid
for i in range(7):
    disks.append(list())
    for j in range(5, -1, -1):
        disks[i].append(canvas1.create_oval(row_margin + i * row_width, row_margin + j * row_height,
                                            (i + 1) * row_width - row_margin,
                                            (j + 1) * row_height - row_margin, fill='white'))

canvas1.grid(row=0, column=0, columnspan=2)

information = tk.Label(window, text="")
information.grid(row=1, column=0, columnspan=2)

label_player1 = tk.Label(window, text="Player 1: ")
label_player1.grid(row=2, column=0)
combobox_player1 = ttk.Combobox(window, state='readonly')
combobox_player1.grid(row=2, column=1)

label_player2 = tk.Label(window, text="Player 2: ")
label_player2.grid(row=3, column=0)
combobox_player2 = ttk.Combobox(window, state='readonly')
combobox_player2.grid(row=3, column=1)

combobox_player1['values'] = player_type
combobox_player1.current(0)
combobox_player2['values'] = player_type
combobox_player2.current(6)

button2 = tk.Button(window, text='New game', command=game.launch)
button2.grid(row=4, column=0)

button = tk.Button(window, text='Quit', command=window.destroy)
button.grid(row=4, column=1)

# Mouse handling
canvas1.bind('<Button-1>', game.click)

window.mainloop()
