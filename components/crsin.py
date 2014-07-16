#!/usr/bin/env python3

from . import gamectrl

import curses

class CursesInput:
    """
    Cuses input class

    Contains everything necessary to translate the input events from the 
    given curses window.
    """

    MOVEMENT_KEYS_TRANSLATION = {
            curses.KEY_UP: gamectrl.MovementDirections.up,
            curses.KEY_DOWN: gamectrl.MovementDirections.down,
            curses.KEY_LEFT: gamectrl.MovementDirections.left,
            curses.KEY_RIGHT: gamectrl.MovementDirections.right
            }

    def __init__(self, window, game_ctrl, output_ctrl):
        self.window = window
        self.input_listeners = []

        self._game_ctrl = game_ctrl
        self._output_ctrl = output_ctrl

        self._game_ctrl.attach_input(self)

    def get_input(self):
        pressed_key = self.window.getch()

        if (pressed_key == ord('r')):
            self._game_ctrl.reset_game()
        elif (pressed_key == 0x1b):
            self._game_ctrl.close_game()
        elif (pressed_key in CursesInput.MOVEMENT_KEYS_TRANSLATION):
            self._game_ctrl.move_pieces(
                    CursesInput.MOVEMENT_KEYS_TRANSLATION[pressed_key])
        elif (pressed_key == ord('?')):
            self._output_ctrl.open_help()
        elif (pressed_key == curses.KEY_RESIZE):
            self._output_ctrl.update_size()

    def is_operational(self):
        return True
