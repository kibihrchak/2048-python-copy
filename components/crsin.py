#!/usr/bin/env python3

from . import gamectrl

import curses
import enum

class _CursesInputStates(enum.Enum):
    cis_init = 1
    cis_normal = 2
    cis_help_window = 3

class CursesInput:
    """
    Cuses input class

    Contains everything necessary to translate the input events from the 
    given curses window.
    """

    _MOVEMENT_KEYS_TRANSL = {
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

        self._state = _CursesInputStates.cis_init

    def get_input(self):
        pressed_key = self.window.getch()

        if self._state == _CursesInputStates.cis_init:
            # skip if the keypress is one of the always checked
            if pressed_key != 0x1b and pressed_key != ord('?'):
                self._output_ctrl.close_intro_window()
                self._game_ctrl.resume_game()
                # state change
                self._state = _CursesInputStates.cis_normal
        elif self._state == _CursesInputStates.cis_normal:
            if pressed_key == ord('r'):
                self._game_ctrl.reset_game()
            elif pressed_key in CursesInput._MOVEMENT_KEYS_TRANSL:
                self._game_ctrl.move_pieces(
                        CursesInput._MOVEMENT_KEYS_TRANSL[pressed_key])

        # always checked keypresses
        if pressed_key == curses.KEY_RESIZE:
            self._output_ctrl.update_size()
        elif pressed_key == 0x1b:
            self._game_ctrl.close_game()

        # help check
        if pressed_key == ord('?'):
            if self._state != _CursesInputStates.cis_help_window:
                self._output_ctrl.open_help()
                # state change
                self._old_state = self._state
                self._state = _CursesInputStates.cis_help_window
            else:
                self._output_ctrl.close_help()
                self._state = self._old_state

    def is_operational(self):
        return True
