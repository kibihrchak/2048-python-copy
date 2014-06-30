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

    class GameStates(Enum):
        gs_active = 1
        gs_terminated = 2
        gs_endgame = 3
        gs_help = 4
    

    def __init__(self):
        self.output_listeners = []

        self.board_width = 4
        self.board_height = 4

        self.free_tiles = 0

        self.help_displayed = False

        self.state = GameController.GameStates.gs_endgame
        self.set_game_state(GameController.GameStates.gs_active)

    def __move_and_merge(self, dl_length, get_piece, set_piece):
        cursor_index = 0
        free_tile_index = -1
        merging_piece_index = -1

        merging_score = 0
        movement_done = False

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
                        movement_done = True

                        merging_piece_index = -1
                        self.free_tiles += 1
                    elif free_tile_index != -1:
                        # no merging, but there is a free tile

                        # move the piece to the free tile
                        set_piece(free_tile_index, piece_val)
                        set_piece(cursor_index, 
                                GameController.EMPTY_TILE)

                        merging_piece_index = free_tile_index

                        movement_done = True

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

                        movement_done = True

                        free_tile_index += 1
                        cursor_index += 1
                    else:
                        # no free tiles

                        merging_piece_index = cursor_index
                        cursor_index += 1

        return (merging_score, movement_done)

    # controller info
    #

    def get_game_state(self):
        return self.state

    def get_board_size(self):
        return (self.board_width, self.board_height)

    def get_board_state(self):
        return (self.pieces, self.current_score)

    # actions
    #

    def init_game(self):
        self.current_score = 0

        self.pieces = [[0 for col in range(self.board_width)]
                for row in range(self.board_height)]
        self.pieces[0][0] = 2
        self.pieces[0][1] = 4

        self.free_tiles = self.board_width * self.board_height
        self.free_tiles -= 2

    def move_merge_pieces(self, movement_direction):
        md = movement_direction
        mds = GameController.MovementDirections

        movement_done = False

        if md == mds.up:
            for col in range(self.board_width):
                def getter(index):
                    return self.pieces[index][col]
                def setter(index, value):
                    self.pieces[index][col] = value

                (ret_score, ret_movement_done) = self.__move_and_merge(
                        self.board_width, getter, setter)

                self.current_score += ret_score
                movement_done = movement_done or ret_movement_done

        elif md == mds.down:
            for col in range(self.board_width):
                def getter(index):
                    row = self.board_height - index - 1
                    return self.pieces[row][col]
                def setter(index, value):
                    row = self.board_height - index - 1
                    self.pieces[row][col] = value

                (ret_score, ret_movement_done) = self.__move_and_merge(
                        self.board_width, getter, setter)

                self.current_score += ret_score
                movement_done = movement_done or ret_movement_done

        elif md == mds.left:
            for row in range(self.board_height):
                def getter(index):
                    return self.pieces[row][index]
                def setter(index, value):
                    self.pieces[row][index] = value

                (ret_score, ret_movement_done) = self.__move_and_merge(
                        self.board_width, getter, setter)

                self.current_score += ret_score
                movement_done = movement_done or ret_movement_done

        elif md == mds.right:
            for row in range(self.board_height):
                def getter(index):
                    col = self.board_width - index - 1
                    return self.pieces[row][col]
                def setter(index, value):
                    col = self.board_width - index - 1
                    self.pieces[row][col] = value

                (ret_score, ret_movement_done) = self.__move_and_merge(
                        self.board_width, getter, setter)

                self.current_score += ret_score
                movement_done = movement_done or ret_movement_done

        return movement_done

    def moves_available(self):
        # first check - are there free tiles?
        if self.free_tiles > 0:
            return True

        # second check - are there mergings available?
        #

        # first pass - check by rows
        for row in range(self.board_height):
            for col in range(self.board_width - 1):
                if self.pieces[row][col] == self.pieces[row][col + 1]:
                    return True

        for col in range(self.board_width):
            for row in range(self.board_height - 1):
                if self.pieces[row][col] == self.pieces[row + 1][col]:
                    return True

        return False

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

    # game state control
    #

    def empty_event(self, *args):
        pass

    def active_movement_event(self, movement_direction):
        movement_done = self.move_merge_pieces(movement_direction)

        if (movement_done):
            self.generate_piece()
            self.notify_output_listeners()

        # check endgame
        if not self.moves_available():
            self.set_game_state(GameController.GameStates.gs_endgame)

    def active_restart_event(self):
        self.set_game_state(GameController.GameStates.gs_active)

    def active_help_event(self):
        self.set_game_state(GameController.GameStates.gs_help)

    def active_exit_event(self):
        self.set_game_state(GameController.GameStates.gs_terminated)

    def set_game_state(self, new_state):
        if new_state == GameController.GameStates.gs_endgame:
            for listener in self.output_listeners:
                listener.show_endgame_message()

            self.movement_event = self.empty_event

        elif new_state == GameController.GameStates.gs_active:

            self.movement_event = self.active_movement_event
            self.restart_event = self.active_restart_event
            self.help_event = self.active_help_event
            self.exit_event = self.active_exit_event

            if self.state == GameController.GameStates.gs_endgame:
                for listener in self.output_listeners:
                    listener.hide_endgame_message()

            self.init_game()
            self.notify_output_listeners()

        elif new_state == GameController.GameStates.gs_help:
            if self.state == GameController.GameStates.gs_help:
                new_state = self.pre_help_state

                self.movement_event = self.pre_help_movement_event
                self.restart_event = self.pre_help_restart_event

                for listener in self.output_listeners:
                    listener.close_help()
            else:
                self.pre_help_state = self.state

                self.pre_help_movement_event = self.movement_event
                self.pre_help_restart_event = self.restart_event
                self.movement_event = self.empty_event
                self.restart_event = self.empty_event

                for listener in self.output_listeners:
                    listener.open_help()

        self.state = new_state

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
        pass

    def restart_event(self):
        pass

    def exit_event(self):
        pass

    def help_event(self):
        pass

class CursesOutput:
    def __init__(self, window):
        self.window = window

        self.help_window = None
        self.endgame_message = None

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

        if self.endgame_message != None:
            self.draw_window(self.endgame_message, "Endgame!")
        if self.help_window != None:
            self.draw_window(self.help_window, "Help window.")

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

    def draw_window(self, window, message):
        window.border()
        window.addstr(1, 1, message)
        window.refresh()

    # listener interface
    #

    def register_notification(self, notifier):
        (self.board_width_tiles, self.board_height_tiles) = \
                notifier.get_board_size()
        self.generate_parametrized()
        (self.pieces, self.score) = notifier.get_board_state()
        self.redraw()

    def unregister_notification(self):
        pass

    def game_state_change_notification(self, notifier):
        (self.pieces, self.score) = notifier.get_board_state()
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

    def show_endgame_message(self):
        width = self.window_width - self.help_window_margin * 2
        height = self.window_height - self.help_window_margin * 2

        self.endgame_message = curses.newwin(
                height, width,
                self.help_window_margin, self.help_window_margin)
        self.redraw()
    
    def hide_endgame_message(self):
        self.endgame_message = None


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

    while(gc.get_game_state() !=
            GameController.GameStates.gs_terminated):
        ci.get_input()

if __name__ == "__main__":
    # needed for the faster reaction of <ESC> key
    os.environ["ESCDELAY"] = "10"

    curses.wrapper(main)
