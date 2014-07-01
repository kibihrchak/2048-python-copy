#!/usr/bin/env python3

"""
Game controller module

Has `MovementDirections` enum, and the `GameController` class.
"""

import enum
import random

class MovementDirections(enum.Enum):
    """
    Piece movement directions

    Specifies possible directions when moving pieces.
    """

    up = 1
    down = 2
    left = 3
    right = 4

class GameController:
    """
    Game controller class

    Contains everything needed to represent, and control one instance of 
    the game.
    """

    EMPTY_TILE = 0

    class GameStates(enum.Enum):
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

    def is_active(self):
        return self.state != GameController.GameStates.gs_terminated

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
        mds = MovementDirections

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
