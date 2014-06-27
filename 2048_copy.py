#!/usr/bin/env python3

import curses
import os
import random
from enum import Enum


class GameController:
    class MovementDirections(Enum):
        up = 1
        down = 2
        left = 3
        right = 4

    def __init__(self):
        self.output_listeners = []
        self.is_active = True

        self.board_width = 4
        self.board_height = 4

        self.free_tiles = 0

        self.help_displayed = False

        self.init_game()

    def init_game(self):
        self.current_score = 0

        self.pieces = [[0 for col in range(self.board_width)]
                for row in range(self.board_height)]
        self.pieces[0][0] = 2
        self.pieces[0][1] = 4

        self.free_tiles = self.board_width * self.board_height
        self.free_tiles -= 2

    def generate_piece(self):
        new_free_tile_index = random.randint(0, self.free_tiles - 1)
        new_piece_value = 2 ** random.randint(1, 2)

        new_piece_inserted = False
        current_free_tile_index = 0

        for row in range(0, self.board_width):
            if new_piece_inserted:
                break
            for col in range(0, self.board_height):
                if self.pieces[row][col] == 0:
                    if current_free_tile_index == new_free_tile_index:
                        self.pieces[row][col] = new_piece_value
                        new_piece_inserted = True
                        break
                    else:
                        current_free_tile_index += 1

        self.free_tiles -= 1

    def moves_available(self):
        if self.free_tiles > 0:
            return True
        else:
            return False

    # controller info
    #

    def get_state(self):
        return self.is_active

    def get_board_size(self):
        return (self.board_width, self.board_height)

    def get_current_game_state(self):
        return (self.pieces, self.current_score)

    # notifier interface
    #

    def register_output_listener(self, output_listener):
        self.output_listeners.append(output_listener)
        output_listener.register_notification(self)

    def unregister_output_listener(self, output_listener):
        output_listener.unregister_notification(self)
        self.output_listeners.remove(output_listener)

    def notify_output_listeners(self):
        for listener in self.output_listeners:
            listener.game_state_change_notification(self)

    # listener interface
    #

    def movement_event(self, movement_direction):
        md = movement_direction
        mds = GameController.MovementDirections
        max_x = self.board_width - 1
        max_y = self.board_height - 1
        empty_tile = 0

        pass_dir_dict = {
                mds.up: 1,
                mds.down: -1,
                mds.left: 1,
                mds.right: -1}
        range_dict = {
                mds.up: range(0, self.board_height, 1),
                mds.down: range(max_y, -1, -1),
                mds.left: range(0, self.board_width, 1),
                mds.right: range(max_x, -1, -1)}
        free_tile_init_index_dict = {
                mds.up: self.board_height - 1,
                mds.down: 0,
                mds.left: self.board_width - 1,
                mds.right: 0}

        pass_dir = pass_dir_dict[md]
        movement_line_range = range_dict[md]

        if (md == mds.up) or (md == mds.down):
            # direction lines are columns
            for col in range(self.board_width):
                free_tile_index = free_tile_init_index_dict[md]
                free_tile_set = False
                for row in movement_line_range:
                    is_tile_empty = self.pieces[row][col] == empty_tile

                    if is_tile_empty:
                        if not free_tile_set:
                            free_tile_index = row
                            free_tile_set = True
                    else:
                        if free_tile_set:
                            self.pieces[free_tile_index][col] = \
                                    self.pieces[row][col]
                            self.pieces[row][col] = empty_tile

                            free_tile_index += pass_dir

        elif (md == mds.left) or (md == mds.right):
            # direction lines are columns
            for row in range(self.board_height):
                free_tile_index = free_tile_init_index_dict[md]
                free_tile_set = False
                for col in movement_line_range:
                    is_tile_empty = self.pieces[row][col] == empty_tile

                    if is_tile_empty:
                        if not free_tile_set:
                            free_tile_index = col
                            free_tile_set = True
                    else:
                        if free_tile_set:
                            self.pieces[row][free_tile_index] = \
                                    self.pieces[row][col]
                            self.pieces[row][col] = empty_tile

                            free_tile_index += pass_dir

        self.generate_piece()
        self.current_score += 2

        self.notify_output_listeners()

        # check endgame
        if not self.moves_available():
            for listener in self.output_listeners:
                listener.endgame_event()

    def restart_event(self):
        self.init_game()

        self.notify_output_listeners()

    def exit_event(self):
        self.is_active = False

    def help_event(self):
        if not self.help_displayed:
            for listener in self.output_listeners:
                listener.open_help()
            self.help_displayed = True
        else:
            for listener in self.output_listeners:
                listener.close_help()
            self.help_displayed = False


class CursesOutput:
    def __init__(self, window):
        self.window = window

        self.help_window = None

        # width, and height of a single tile in characters
        self.tile_width = 6
        self.tile_height = 3
        # width, and height of a playing board
        self.board_width_tiles = 0
        self.board_height_tiles = 0

        # drawing location for the board
        self.board_x = 0
        self.board_y = 3

        self.pieces = None
        self.score = 0

        self.game_area_border_char = "="
        self.tile_border_char = "."
        self.tile_inner_char = " "
        self.piece_border_char = "x"
        self.piece_hl_char = "-"
        self.piece_vl_char = "|"
        self.piece_inner_char = " "

        self.help_window_margin = 1

        # parametrized fields
        self.inside_tile_width = 0
        self.board_width = 0
        self.board_height = 0
        self.window_width = 0
        self.window_height = 0

        self.generate_parametrized()


    def generate_parametrized(self):
        self.inside_tile_width = self.tile_width - 2
        self.board_width = self.board_width_tiles * self.tile_width
        self.board_height = self.board_height_tiles * self.tile_height
        self.window_width = self.board_width
        self.window_height = self.board_height + 2 + 2

    def redraw(self):
        self.window.erase()
        self.draw_game_window()
        self.draw_pieces()
        self.window.refresh()

        if self.help_window != None:
            self.draw_help_window()

    def draw_game_window(self):
        game_area_border = \
                self.game_area_border_char * self.board_width

        self.window.addstr(0, 0, "2048 copy")
        self.window.addstr(1, 0, "Score: {}".format(self.score))
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

    def draw_pieces(self):
        for row in range(self.board_height_tiles):
            for col in range(self.board_width_tiles):
                piece_value = self.pieces[row][col]
                if piece_value != 0:
                    piece_x = col * self.tile_width + self.board_x
                    piece_y = row * self.tile_height + self.board_y
                    self.draw_piece(piece_x, piece_y, piece_value)

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

    def draw_help_window(self):
        self.help_window.border()
        self.help_window.addstr(1, 1, "Help window")
        self.help_window.refresh()

    # listener interface
    #

    def register_notification(self, notifier):
        (self.board_width_tiles, self.board_height_tiles) = \
                notifier.get_board_size()
        self.generate_parametrized()
        (self.pieces, self.score) = notifier.get_current_game_state()
        self.redraw()

    def unregister_notification(self):
        pass

    def game_state_change_notification(self, notifier):
        (self.pieces, self.score) = notifier.get_current_game_state()
        self.redraw()

    def open_help(self):
        width = self.window_width - self.help_window_margin * 2
        height = self.window_height - self.help_window_margin * 2

        self.help_window = curses.newwin(
                height, width,
                self.help_window_margin, self.help_window_margin)
        self.redraw()

    def close_help(self):
        self.help_window = None
        self.redraw()

    def endgame_event(self):
        width = self.window_width - self.help_window_margin * 2
        height = self.window_height - self.help_window_margin * 2

        self.help_window = curses.newwin(
                height, width,
                self.help_window_margin, self.help_window_margin)
        self.redraw()


class CursesInput:
    MOVEMENT_KEYS_TRANSLATION = {
            curses.KEY_UP: GameController.MovementDirections.up,
            curses.KEY_DOWN: GameController.MovementDirections.down,
            curses.KEY_LEFT: GameController.MovementDirections.left,
            curses.KEY_RIGHT: GameController.MovementDirections.right
            }

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
        elif (pressed_key in CursesInput.MOVEMENT_KEYS_TRANSLATION):
            for listener in self.input_listeners:
                listener.movement_event(
                        CursesInput.
                        MOVEMENT_KEYS_TRANSLATION[pressed_key])
        elif (pressed_key == ord('?')):
            for listener in self.input_listeners:
                listener.help_event()

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

    gc.register_output_listener(co)
    ci.register_listener(gc)

    while(gc.get_state()):
        ci.get_input()

if __name__ == "__main__":
    # needed for the faster reaction of <ESC> key
    os.environ["ESCDELAY"] = "10"

    curses.wrapper(main)
