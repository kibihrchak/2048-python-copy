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

    def __init__(self, window, output_ctrl):
        self.window = window
        self.input_listeners = []
        self._output_ctrl = output_ctrl

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
        elif (pressed_key == curses.KEY_RESIZE):
            self._output_ctrl.update_size()


    # notifier interface
    #

    def register_listener(self, input_listener):
        self.input_listeners.append(input_listener)

    def unregister_listener(self, input_listener):
        self.input_listeners.remove(input_listener)
