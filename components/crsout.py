#!/usr/bin/env python3

"""
Curses output module
"""

import curses

class CursesOutput:
    """
    Curses output class

    Encapsulate all the necessary data to provide the visual output of 
    the game to the specified curses window.
    """

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
