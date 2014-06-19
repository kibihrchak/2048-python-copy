#!/usr/bin/env python3

import curses
import os
from enum import Enum

TILE_WIDTH = 6
TILE_HEIGHT = 3
TILES_HORIZONTAL = 4
TILES_VERTICAL = 4

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
            self.pieces[0][1] = TILES_VERTICAL - 1
        elif (movement_direction == curses.KEY_LEFT):
            self.pieces[0][0] = 0
        elif (movement_direction == curses.KEY_RIGHT):
            self.pieces[0][0] = TILES_HORIZONTAL - 1

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

    def draw_game_window(self, score):
        GAME_AREA_BORDER_CHAR = "="
        game_area_border = \
                GAME_AREA_BORDER_CHAR  * TILE_WIDTH * TILES_HORIZONTAL

        self.window.addstr(0, 0, "2048 copy")
        self.window.addstr(1, 0, "Score: {}".format(score))
        self.window.addstr(2, 0, game_area_border)
        self.draw_tiles(0, 3)
        self.window.addstr(
                3 + TILE_HEIGHT * TILES_VERTICAL, 0,
                game_area_border)

    def draw_tiles(self, x, y):
        BORDER_CHAR = "."
        INNER_CHAR = " "
        INSIDE_AREA_WIDTH = TILE_WIDTH - 2

        border_line = BORDER_CHAR * TILE_WIDTH * TILES_HORIZONTAL
        inner_line_piece = "".join((
                BORDER_CHAR,
                INNER_CHAR * INSIDE_AREA_WIDTH,
                BORDER_CHAR))
        inner_line = inner_line_piece * TILES_HORIZONTAL

        for tile_row in range(TILES_VERTICAL):
            start_line = y + tile_row * TILE_HEIGHT

            self.window.addstr(start_line, x, border_line)
            self.window.addstr(start_line + 1, x, inner_line)
            self.window.addstr(start_line + 2, x, border_line)

    def draw_pieces(self, pieces):
        for piece in pieces:
            self.draw_piece(
                    piece[0] * TILE_WIDTH,
                    piece[1] * TILE_HEIGHT + 3,
                    piece[2])

    def draw_piece(self, x, y, value):
        BORDER_CHAR = "x"
        HL_CHAR = "-"
        VL_CHAR = "|"
        INNER_CHAR = " "
        INSIDE_AREA_WIDTH = TILE_WIDTH - 2

        border_line = "".join((
                BORDER_CHAR,
                HL_CHAR * INSIDE_AREA_WIDTH,
                BORDER_CHAR))
        middle_line = "".join((
                VL_CHAR,
                "{:{fill}^{width}d}".format(
                    value,
                    fill = INNER_CHAR,
                    width = INSIDE_AREA_WIDTH),
                VL_CHAR))

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
