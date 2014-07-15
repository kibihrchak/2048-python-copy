#!/usr/bin/env python3

"""
Curses output module
"""

import curses
import textwrap
from . import helpdocs

class _DrawCharacters:
    game_area_border_char = "="
    tile_border_char = "."
    tile_inner_char = " "
    piece_border_char = "x"
    piece_hl_char = "-"
    piece_vl_char = "|"
    piece_inner_char = " "

class _SubWindow:
    _BORDER_WIDTH = 1

    def _change_wh(self, new_width, new_height):
        self._draw_area_xy = (
                _SubWindow._BORDER_WIDTH,
                _SubWindow._BORDER_WIDTH)
        self._draw_area_wh = (
                new_width - 2 * _SubWindow._BORDER_WIDTH,
                new_height - 2 * _SubWindow._BORDER_WIDTH)

    def __init__(self, x, y, width, height):
        self._window = curses.newwin(height, width, y, x)
        self._change_wh(width, height)

    def resize_window(self, new_width, new_height):
        self._window.resize(new_height, new_width)
        self._change_wh(new_width, new_height)

    def move_window(self, new_x, new_y):
        self._window.mvwin(new_y, new_x)

    def redraw(self):
        self._window.erase()
        self._window.border()
        self._actual_draw()
        self._window.refresh()

class _MessageWindow(_SubWindow):
    """
    Message window helper class

    This class represents the message window. Its position, and size are
    externaly specified. Its duties are to reflow, and repage the
    message text, so it can fit inside the window, and provide the
    drawing.
    """

    def __init__(self, title, message, x, y, width, height):
        super().__init__(x, y, width, height)

        self._title = title
        self._message = message

        self._reflow_message()

    def _reflow_message(self):
        self._message_lines = []

        for paragraph in self._message.splitlines():
            if paragraph != "":
                wrapped_paragraph = textwrap.wrap(
                        paragraph,
                        width = self._draw_area_wh[0])
                self._message_lines.extend(wrapped_paragraph)
            else:
                # [TODO] quick fix for avoiding the newline skips
                self._message_lines.append("")

        self._num_pages = -(
                -len(self._message_lines) // self._draw_area_wh[1])
        self._page_index = 0

    def resize_window(self, new_width, new_height):
        super(_MessageWindow, self).resize_window(new_width, new_height)
        self._reflow_message()

    def _actual_draw(self):
        TITLE_INDENT = 2

        prepared_title = textwrap.shorten(
                self._title,
                width = self._draw_area_wh[0] - (TITLE_INDENT * 2),
                placeholder = "...")

        self._window.addstr(0, TITLE_INDENT, prepared_title)

        start_line = self._page_index * self._draw_area_wh[1]
        line_cnt = self._draw_area_wh[1]
        if start_line + line_cnt > len(self._message_lines):
            line_cnt = len(self._message_lines) - start_line

        for msg_line in range(0, line_cnt):
            self._window.addstr(
                    self._draw_area_xy[1] + msg_line,
                    self._draw_area_xy[0],
                    self._message_lines[start_line + msg_line])

    def get_num_pages(self):
        return self._num_pages

    def get_page_index(self):
        return self._page_index

    def set_page_index(self, index):
        self._page_index = index

class _BoardWindow(_SubWindow):
    def __init__(self, x, y, width, height, board_wh_tiles, 
            free_tile_value):
        super().__init__(x, y, width, height)

        self._free_tile_value = free_tile_value
        self._board_wh_tiles = board_wh_tiles
        self._calc_tile_size()

    def _calc_tile_size(self):
        self._tile_wh = tuple(win_dim // cnt
                for (win_dim, cnt) in
                zip(self._draw_area_wh, self._board_wh_tiles))
        self._inside_tile_wh = tuple(
                tile_dim - 2 for tile_dim in self._tile_wh)
        self._board_wh = tuple(tile_dim * board_dim
                for (tile_dim, board_dim) in
                zip(self._tile_wh, self._board_wh_tiles))

    def get_board_wh(self):
        return self._board_wh

    def resize_window(self, new_width, new_height):
        super().resize_window(new_width, new_height)
        self._calc_tile_size()
    
    def change_board_dimensions(self, horizontal_tiles, vertical_tiles):
        self._board_wh_tiles = (horizontal_tiles, vertical_tiles)
        self._calc_tile_size()

    def set_board_pieces(self, pieces):
        self._pieces = pieces

    def _actual_draw(self):
        self._draw_tiles()
        self._draw_pieces()

    def _draw_tiles(self):
        dc = _DrawCharacters
        border_line = \
                dc.tile_border_char * self._board_wh[0]
        inner_line_tile = "".join((
                dc.tile_border_char,
                dc.tile_inner_char * self._inside_tile_wh[0],
                dc.tile_border_char))
        inner_line = inner_line_tile * self._board_wh_tiles[0]

        draw_y = self._draw_area_xy[1]
    
        def draw_tile_line(line_text):
            nonlocal draw_y
            self._window.addstr(draw_y, self._draw_area_xy[0], 
                    line_text)
            draw_y += 1

        for tile_row in range(self._board_wh_tiles[1]):
            draw_tile_line(border_line)
            for inside_tile_row in range(self._inside_tile_wh[1]):
                draw_tile_line(inner_line)
            draw_tile_line(border_line)

    def _draw_pieces(self):
        for row in range(self._board_wh_tiles[1]):
            for col in range(self._board_wh_tiles[0]):
                piece_value = self._pieces[row][col]
                if piece_value != self._free_tile_value:
                    self._draw_piece(col, row, piece_value)

    def _draw_piece(self, tile_x, tile_y, value):
        dc = _DrawCharacters
        border_line = "".join((
                dc.piece_border_char,
                dc.piece_hl_char * self._inside_tile_wh[0],
                dc.piece_border_char))
        middle_empty_line = "".join((
                dc.piece_vl_char,
                dc.piece_inner_char * self._inside_tile_wh[0],
                dc.piece_vl_char))
        middle_value_line = "".join((
                dc.piece_vl_char,
                "{:{fill}^{width}d}".format(
                    value,
                    fill = dc.piece_inner_char,
                    width = self._inside_tile_wh[0]),
                dc.piece_vl_char))

        draw_x = tile_x * self._tile_wh[0] + self._draw_area_xy[0]
        draw_y = tile_y * self._tile_wh[1] + self._draw_area_xy[1]

        def draw_piece_line(line_text):
            nonlocal draw_y
            self._window.addstr(draw_y, draw_x, line_text)
            draw_y += 1

        draw_piece_line(border_line)

        for inner_row in range(self._inside_tile_wh[1]):
            if inner_row == self._inside_tile_wh[1] // 2:
                draw_piece_line(middle_value_line)
            else:
                draw_piece_line(middle_empty_line)

        draw_piece_line(border_line)

class CursesOutput:
    """
    Curses output class

    Encapsulate all the necessary data to provide the visual output of 
    the game to the specified curses window.
    """

    def __init__(self, window, gamectrl):
        self._window = window
        self._gamectrl = gamectrl

        (self._win_height, self._win_width) = self._window.getmaxyx()
        (board_win_width, board_win_height) = (self._win_width, 
                self._win_height - 3)
        
        self._board = _BoardWindow(
                0, 2,
                board_win_width, board_win_height,
                self._gamectrl.get_board_dimensions(),
                self._gamectrl.get_free_tile_value())

        self._help_window = None
        self._endgame_message = None

        self.update_game_state()

    def resize(self):
        (self._win_height, self._win_width) = self._window.getmaxyx()
        (board_win_width, board_win_height) = (self._win_width, 
                self._win_height - 3)
        self._board.resize_window(board_win_width, board_win_height)
        self.redraw()

    def redraw(self):
        self._window.erase()
        self._draw_outer_elements()
        self._window.refresh()

        self._board.redraw()

        if self._endgame_message != None:
            self._endgame_message.redraw()
        if self._help_window != None:
            self._help_window.redraw()

    def _draw_outer_elements(self):
        dc = _DrawCharacters
        board_wh = self._board.get_board_wh()

        game_area_border = dc.game_area_border_char * board_wh[0]

        draw_y = 0

        def draw_line(line_text):
            nonlocal draw_y
            # `insstr` needed because of the bottom line
            self._window.insstr(draw_y, 0, line_text)
            draw_y += 1

        draw_line("2048 copy")
        draw_line("Score: {}".format(self._score))
        draw_y += board_wh[1]
        draw_line("Status line")

    def update_game_state(self):
        self._board.set_board_pieces(self._gamectrl.get_board_state())
        self._score = self._gamectrl.get_current_score()
        self.redraw()

    def open_help(self):
        board_wh = self._board.get_board_wh()

        self._help_window = _MessageWindow(
                "2048 game help",
                helpdocs.get_help_text(),
                1, 1,
                board_wh[0] - 2, board_wh[1])
        self.redraw()

    def close_help(self):
        self.help_window = None
        self.redraw()

    def open_endgame_message(self):
        board_wh = self._board.get_board_wh()

        self._endgame_message = _MessageWindow(
                "Game End",
                "No more moves available. Current score is"
                "{}.".format(self._score),
                2, 2,
                board_wh[0] - 4, board_wh[1] - 4)
        self.redraw()
    
    def hide_endgame_message(self):
        self.endgame_message = None
        self.redraw()
