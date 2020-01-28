from mlgame.gamedev import physics
from mlgame.utils.enum import StringEnum

from pygame.math import Vector2
import pygame
import random

class PlatformAction(StringEnum):
    MOVE_LEFT = "LEFT"
    MOVE_RIGHT = "RIGHT"
    NONE = "NONE"

class Platform(pygame.sprite.Sprite):
    def __init__(self, init_pos, play_area_rect: pygame.Rect, \
            side, color, *groups):
        super().__init__(*groups)

        self._play_area_rect = play_area_rect
        self._shift_speed = 5
        self._speed = [0, 0]
        self._init_pos = pygame.Rect(*init_pos, 40, 30)

        self.rect = self._init_pos.copy()
        self.image = self._create_surface(side, color)

    def _create_surface(self, side, color):
        surface = pygame.Surface((self.rect.width, self.rect.height))

        # Draw the platform image
        platform_image = pygame.Surface((self.rect.width, 10))
        platform_image.fill(color)
        # The platform image of 1P is at the top of the rect
        if side == "1P":
            surface.blit(platform_image, (0, 0))
        # The platform image of 2P is at the bottom of the rect
        else:
            surface.blit(platform_image, (0, surface.get_height() - 10))

        # Draw the outline of the platform rect
        pygame.draw.rect(surface, color, \
            pygame.Rect(0, 0, self.rect.width, self.rect.height), 1)

        return surface

    @property
    def pos(self):
        return self.rect.topleft

    def reset(self):
        self.rect = self._init_pos.copy()

    def move(self, move_action: PlatformAction):
        if move_action == PlatformAction.MOVE_LEFT and \
            self.rect.left > self._play_area_rect.left:
            self._speed[0] = -self._shift_speed
        elif move_action == PlatformAction.MOVE_RIGHT and \
            self.rect.right < self._play_area_rect.right:
            self._speed[0] = self._shift_speed
        else:
            self._speed[0] = 0

        self.rect.move_ip(*self._speed)

class Ball(pygame.sprite.Sprite):
    def __init__(self, play_area_rect: pygame.Rect, *groups):
        super().__init__(*groups)

        self._play_area_rect = play_area_rect
        self._speed = [7, 7]
        self._size = [5, 5]
        self._serve_from_1P = True

        self.rect = pygame.Rect(0, 0, *self._size)
        self.image = self._create_surface()

        # Used in additional collision detection
        self._last_pos = Vector2(self.rect.x, self.rect.y)

    def _create_surface(self):
        surface = pygame.Surface((self.rect.width, self.rect.height))
        surface.fill((66, 226, 126))    # Green
        return surface

    @property
    def pos(self):
        return self.rect.topleft

    def reset(self):
        """
        Reset the ball status and serve the ball
        """
        # Serving the ball
        if self._serve_from_1P:
            reset_pos_x = 120
            reset_pos_y = int(self._play_area_rect.height * 0.8 - self.rect.height)
            self._speed = [-7, -7]
        else:
            reset_pos_x = 75
            reset_pos_y = int(self._play_area_rect.height * 0.2)
            self._speed = [7, 7]

        self.rect = pygame.Rect(reset_pos_x, reset_pos_y, *self._size)
        # Change side next time
        self._serve_from_1P = not self._serve_from_1P

    def move(self):
        self._last_pos = Vector2(self.rect.x, self.rect.y)
        self.rect.move_ip(self._speed)

    def speed_up(self):
        self._speed[0] += 1 if self._speed[0] > 0 else -1
        self._speed[1] += 1 if self._speed[1] > 0 else -1

    def check_bouncing(self, platform_1p: Platform, platform_2p: Platform):
        if physics.rect_break_or_tangent_box(self.rect, self._play_area_rect):
            physics.bounce_in_box_ip(self.rect, self._speed, self._play_area_rect)

        # Check if the ball hits the platform or not
        target_platform = None
        cur_pos = Vector2(self.rect.x, self.rect.y)

        if physics.collide_or_tangent(self, platform_1p):
            target_platform = platform_1p
        elif physics.collide_or_tangent(self, platform_2p):
            target_platform = platform_2p
        # Additional checking for the ball passing through the corner of the platform
        # Determine if the routine of the ball intersects with the platform
        elif self.rect.bottom < platform_1p.rect.bottom:
            line_top_right = (cur_pos + Vector2(self.rect.width, 0), \
                self._last_pos + Vector2(self.rect.width, 0))
            line_top_left = (cur_pos, self._last_pos)

            if self._ball_routine_hit_platform( \
                platform_1p, line_top_right, line_top_left):
                target_platform = platform_1p

        elif self.rect.top > platform_2p.rect.top:
            line_bottom_right = (cur_pos + Vector2(self.rect.width, self.rect.height), \
                self._last_pos + Vector2(self.rect.width, self.rect.height))
            line_bottom_left = (cur_pos + Vector2(0, self.rect.height), \
                self._last_pos + Vector2(0, self.rect.height))

            if self._ball_routine_hit_platform( \
                platform_2p, line_bottom_right, line_bottom_left):
                target_platform = platform_2p

        if target_platform:
            physics.bounce_off_ip(self.rect, self._speed, \
                target_platform.rect, target_platform._speed)

    def _ball_routine_hit_platform(self, target_platform: Platform, \
        routine_for_left, routine_for_right) -> bool:
        """
        Check if the ball routine hits the platform

        @param target_platform Specify the target platform
        @param routine_for_left A tuple (Vector2, Vector2) presenting the checking routine
               for the condition that the ball is at the left side of the platform
        @param routine_for_right Similar to `routine_for_left` but
               for the condition that the ball is at the right side of the platform
        """
        return (self.rect.right < target_platform.rect.left and \
                physics.rect_collideline(target_platform.rect, routine_for_left)) or \
               (self.rect.left > target_platform.rect.right and \
                physics.rect_collideline(target_platform.rect, routine_for_right))
