#!/usr/bin/env python3

import curses
import os
from enum import Enum

TILE_WIDTH = 6
TILE_HEIGHT = 3
TILES_HORIZONTAL = 4
TILES_VERTICAL = 4

def draw_game_window(window, score):
    GAME_AREA_BORDER_CHAR = "="
    game_area_border = \
            GAME_AREA_BORDER_CHAR  * TILE_WIDTH * TILES_HORIZONTAL

    window.addstr(0, 0, "2048 copy")
    window.addstr(1, 0, "Score: {}".format(score))
    window.addstr(2, 0, game_area_border)
    draw_tiles(window, 0, 3)
    window.addstr(3 + TILE_HEIGHT * TILES_VERTICAL, 0, game_area_border)

def draw_tiles(window, x, y):
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

        window.addstr(start_line, x, border_line)
        window.addstr(start_line + 1, x, inner_line)
        window.addstr(start_line + 2, x, border_line)

def draw_piece(window, x, y, value):
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

    window.addstr(y, x, border_line)
    window.addstr(y + 1, x, middle_line)
    window.addstr(y + 2, x, border_line)

def draw_tile(window, x, y):
    BORDER_CHAR = "."
    INNER_CHAR = " "
    INSIDE_AREA_WIDTH = TILE_WIDTH - 2

    border_line = BORDER_CHAR * TILE_WIDTH
    middle_line = "".join((
            BORDER_CHAR,
            INNER_CHAR * INSIDE_AREA_WIDTH,
            BORDER_CHAR))

    window.addstr(y, x, border_line)
    window.addstr(y + 1, x, middle_line)
    window.addstr(y + 2, x, border_line)

def redraw_screen(window, pieces):
    window.erase()
    draw_game_window(window, 12)
    for piece in pieces:
        draw_piece(
                window,
                piece[0] * TILE_WIDTH,
                piece[1] * TILE_HEIGHT + 3,
                piece[2])
    window.refresh()

def move_piece(current_state, direction):
    if (direction == curses.KEY_UP):
        current_state[0][1] = 0
    elif (direction == curses.KEY_DOWN):
        current_state[0][1] = TILES_VERTICAL - 1
    elif (direction == curses.KEY_LEFT):
        current_state[0][0] = 0
    elif (direction == curses.KEY_RIGHT):
        current_state[0][0] = TILES_HORIZONTAL - 1 

    current_state[0][2] *= 2

def reset_game(game_state):
    game_state[0] = [0, 0, 2]

def main(stdscr):
    game_state = [[0, 0, 2]]
    curses.curs_set(0)

    active = True

    MOVEMENT_KEYS = (
            curses.KEY_UP,
            curses.KEY_DOWN,
            curses.KEY_LEFT,
            curses.KEY_RIGHT)

    redraw_screen(stdscr, game_state)

    while(active):
        pressed_key = stdscr.getch()

        if (pressed_key == ord('r')):
            reset_game(game_state)
            redraw_screen(stdscr, game_state)
        elif (pressed_key == 0x1b):
            active = False
        elif (pressed_key in MOVEMENT_KEYS):
            move_piece(game_state, pressed_key)
            redraw_screen(stdscr, game_state)

if __name__ == "__main__":
    # needed for the faster reaction of <ESC> key
    os.environ["ESCDELAY"] = "10"

    curses.wrapper(main)
