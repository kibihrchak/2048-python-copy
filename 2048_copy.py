#!/usr/bin/env python3

import curses
import os
import random
from enum import Enum


class GameController:
    EMPTY_TILE = 0

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

    def move_and_merge(self, dl_length, get_piece, set_piece):
        cursor_index = 0
        free_tile_index = -1
        merging_piece_index = -1

        merging_score = 0

        while cursor_index < dl_length:
            piece_val = get_piece(cursor_index)

            if piece_val == GameController.EMPTY_TILE:
                # the tile is free

                if free_tile_index == -1:
                    # free tile cursor is unset

                    free_tile_index = cursor_index

                cursor_index += 1
            else:
                # piece is found

                if merging_piece_index != -1:
                    # merging available

                    if get_piece(merging_piece_index) == piece_val:
                        # the pieces are the same

                        # merge pieces
                        set_piece(cursor_index, 
                                GameController.EMPTY_TILE)
                        set_piece(merging_piece_index, piece_val * 2)

                        merging_score += piece_val
                        merging_piece_index = -1
                        self.free_tiles += 1
                    elif free_tile_index != -1:
                        # no merging, but there is a free tile

                        # move the piece to the free tile
                        set_piece(free_tile_index, piece_val)
                        set_piece(cursor_index, 
                                GameController.EMPTY_TILE)

                        merging_piece_index = free_tile_index

                        free_tile_index += 1
                        cursor_index += 1
                    else:
                        # no merging, and no free tiles

                        merging_piece_index = cursor_index
                        cursor_index += 1
                else:
                    # merging unavailable

                    if free_tile_index != -1:
                        # there is a free tile

                        # move the piece to the free tile
                        set_piece(free_tile_index, piece_val)
                        set_piece(cursor_index, 
                                GameController.EMPTY_TILE)

                        merging_piece_index = free_tile_index

                        free_tile_index += 1
                        cursor_index += 1
                    else:
                        # no free tiles

                        merging_piece_index = cursor_index
                        cursor_index += 1

        return merging_score


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

        if md == mds.up:
            for col in range(self.board_width):
                def getter(index):
                    return self.pieces[index][col]
                def setter(index, value):
                    self.pieces[index][col] = value

                self.current_score += self.move_and_merge(
                        self.board_width, getter, setter)

        elif md == mds.down:
            for col in range(self.board_width):
                def getter(index):
                    row = self.board_height - index - 1
                    return self.pieces[row][col]
                def setter(index, value):
                    row = self.board_height - index - 1
                    self.pieces[row][col] = value

                self.current_score += self.move_and_merge(
                        self.board_width, getter, setter)

        elif md == mds.left:
            for row in range(self.board_height):
                def getter(index):
                    return self.pieces[row][index]
                def setter(index, value):
                    self.pieces[row][index] = value

                self.current_score += self.move_and_merge(
                        self.board_width, getter, setter)

        elif md == mds.right:
            for row in range(self.board_height):
                def getter(index):
                    col = self.board_width - index - 1
                    return self.pieces[row][col]
                def setter(index, value):
                    col = self.board_width - index - 1
                    self.pieces[row][col] = value

                self.current_score += self.move_and_merge(
                        self.board_width, getter, setter)

        self.generate_piece()

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
