import pygame
import time

def quit_or_esc() -> bool:
    """
    Check if the quit event is triggered or the ESC key is pressed.
    """
    for event in pygame.event.get():
        if (event.type == pygame.QUIT or
            (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
            return True
    return False

class KeyCommandMap:
    """
    Map the keys to the commands and return the mapped command when the corresponding
    key is pressed
    """
    def __init__(self, command_map: dict):
        """
        Constructor

        @param command_map A dict which maps the keys to the commands.
               The key of the dict is the key-code defined in pygame, and
               the value is the command that will be returned when the corresponding
               key is pressed.
        """
        if not isinstance(command_map, dict):
            raise TypeError("The 'command_map' should be a 'dict'.")

        self._command_map = command_map

    def get_commands(self):
        """
        Check the pressed keys and return the corresponding commands

        @return A list of commands of which corresponding keys are pressed
                If there is no registered key pressed, return an empty list.
        """
        key_pressed_list = pygame.key.get_pressed()
        pressed_commands = []
        for key, command in self._command_map.items():
            if key_pressed_list[key]:
                pressed_commands.append(command)

        return pressed_commands

class FPSCounter:
    """
    The counter for calculating the FPS

    Invoke `get_FPS()` at each frame. The counter will count how many calls within
    a specified updating interval. Within a updating interval, the returned FPS value
    won't be updated until the starting of next updating interval.
    """

    def __init__(self, update_interval = 1.0):
        """
        Constructor

        @param update_interval The time interval in seconds for updating the FPS value
        """
        self._update_interval = update_interval
        self._fps = 0
        self._tick_count = 0
        self._last_time_updated = time.time()

    def get_FPS(self) -> int:
        """
        Update and get the calculated FPS
        """
        self._tick_count += 1

        current_time = time.time()
        if current_time - self._last_time_updated > self._update_interval:
            self._fps = int(round(self._tick_count / (current_time - self._last_time_updated)))
            self._tick_count = 0
            self._last_time_updated = current_time

        return self._fps