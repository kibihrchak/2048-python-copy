#!/usr/bin/env python3

import curses
import os
from enum import Enum

MOVEMENT_KEYS = (
        curses.KEY_UP,
        curses.KEY_DOWN,
        curses.KEY_LEFT,
        curses.KEY_RIGHT)

class GameController:
    def __init__(self):
        self.init_game()
        self.output_controllers = []
        self.is_active = True

        self.board_width = 4
        self.board_height = 4

    def init_game(self):
        self.current_score = 0
        self.pieces = [[0, 0, 2]]

    def refresh_output(self):
        for listener in self.output_controllers:
            listener.game_state_change(
                    self.pieces,
                    self.current_score)

    def get_state(self):
        return self.is_active

    # notifier interface
    #

    def register_listener(self, output_controller):
        self.output_controllers.append(output_controller)
        output_controller.game_state_change(
                self.pieces,
                self.current_score)

    def unregister_listener(self, output_controller):
        self.output_controllers.remove(output_controller)

    # listener interface
    #

    def movement_event(self, movement_direction):
        if (movement_direction == curses.KEY_UP):
            self.pieces[0][1] = 0
        elif (movement_direction == curses.KEY_DOWN):
            self.pieces[0][1] = self.board_height - 1
        elif (movement_direction == curses.KEY_LEFT):
            self.pieces[0][0] = 0
        elif (movement_direction == curses.KEY_RIGHT):
            self.pieces[0][0] = self.board_width - 1

        self.current_score += 2

        self.refresh_output()

    def restart_event(self):
        self.init_game()

        self.refresh_output()

    def exit_event(self):
        self.is_active = False

class CursesOutput:
    def __init__(self, window):
        self.window = window

        # width, and height of a single tile in characters
        self.tile_width = 6
        self.tile_height = 3
        self.inside_tile_width = self.tile_width - 2
        # width, and height of a playing board
        self.board_width_tiles = 4
        self.board_height_tiles = 4
        self.board_width = self.board_width_tiles * self.tile_width
        self.board_height = self.board_height_tiles * self.tile_height

        # drawing location for the board
        self.board_x = 0
        self.board_y = 3

        self.game_area_border_char = "="
        self.tile_border_char = "."
        self.tile_inner_char = " "
        self.piece_border_char = "x"
        self.piece_hl_char = "-"
        self.piece_vl_char = "|"
        self.piece_inner_char = " "

    def draw_game_window(self, score):
        game_area_border = \
                self.game_area_border_char * self.board_width

        self.window.addstr(0, 0, "2048 copy")
        self.window.addstr(1, 0, "Score: {}".format(score))
        self.window.addstr(2, 0, game_area_border)
        self.draw_tiles()
        self.window.addstr(
                self.board_y + self.board_height, 0, game_area_border)

    def draw_tiles(self):
        border_line = self.tile_border_char * self.board_width
        inner_line_tile = "".join((
                self.tile_border_char,
                self.tile_inner_char * self.inside_tile_width,
                self.tile_border_char))
        inner_line = inner_line_tile * self.board_width_tiles

        start_line = self.board_y

        for tile_row in range(self.board_height_tiles):
            self.window.addstr(
                    start_line, self.board_x, border_line)
            self.window.addstr(
                    start_line + 1, self.board_x, inner_line)
            self.window.addstr(
                    start_line + 2, self.board_x, border_line)

            start_line += self.tile_height

    def draw_pieces(self, pieces):
        for piece in pieces:
            self.draw_piece(
                    piece[0] * self.tile_width + self.board_x,
                    piece[1] * self.tile_height + self.board_y,
                    piece[2])

    def draw_piece(self, x, y, value):
        border_line = "".join((
                self.piece_border_char,
                self.piece_hl_char * self.inside_tile_width,
                self.piece_border_char))
        middle_line = "".join((
                self.piece_vl_char,
                "{:{fill}^{width}d}".format(
                    value,
                    fill = self.piece_inner_char,
                    width = self.inside_tile_width),
                self.piece_vl_char))

        self.window.addstr(y, x, border_line)
        self.window.addstr(y + 1, x, middle_line)
        self.window.addstr(y + 2, x, border_line)

    # listener interface
    #

    def game_state_change(self, pieces, score):
        self.window.erase()
        self.draw_game_window(score)
        self.draw_pieces(pieces)
        self.window.refresh()

class CursesInput:
    def __init__(self, window):
        self.window = window
        self.input_listeners = []

    def get_input(self):
        pressed_key = self.window.getch()

        if (pressed_key == ord('r')):
            for listener in self.input_listeners:
                listener.restart_event()
        elif (pressed_key == 0x1b):
            for listener in self.input_listeners:
                listener.exit_event()
        elif (pressed_key in MOVEMENT_KEYS):
            for listener in self.input_listeners:
                listener.movement_event(pressed_key)

    # notifier interface
    #

    def register_listener(self, input_listener):
        self.input_listeners.append(input_listener)

    def unregister_listener(self, input_listener):
        self.input_listeners.remove(input_listener)


def main(stdscr):
    curses.curs_set(0)

    gc = GameController()
    co = CursesOutput(stdscr)
    ci = CursesInput(stdscr)

    gc.register_listener(co)
    ci.register_listener(gc)

    while(gc.get_state()):
        ci.get_input()

if __name__ == "__main__":
    # needed for the faster reaction of <ESC> key
    os.environ["ESCDELAY"] = "10"

    curses.wrapper(main)
