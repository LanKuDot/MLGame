from mlgame.gamedev import physics
from mlgame.utils.enum import StringEnum, auto

from pygame.math import Vector2
import pygame
import random

class PlatformAction(StringEnum):
    SERVE_TO_LEFT = auto()
    SERVE_TO_RIGHT = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    NONE = auto()

SERVE_BALL_ACTIONS = (PlatformAction.SERVE_TO_LEFT, PlatformAction.SERVE_TO_RIGHT)

class Platform(pygame.sprite.Sprite):
    def __init__(self, init_pos: tuple, play_area_rect: pygame.Rect,
            side, color, *groups):
        super().__init__(*groups)

        self._play_area_rect = play_area_rect
        self._shift_speed = 5
        self._speed = [0, 0]
        self._init_pos = init_pos

        self.rect = pygame.Rect(*init_pos, 40, 30)
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
        pygame.draw.rect(surface, color,
            pygame.Rect(0, 0, self.rect.width, self.rect.height), 1)

        return surface

    @property
    def pos(self):
        return self.rect.topleft

    def reset(self):
        self.rect.x, self.rect.y = self._init_pos

    def move(self, move_action: PlatformAction):
        if (move_action == PlatformAction.MOVE_LEFT and
            self.rect.left > self._play_area_rect.left):
            self._speed[0] = -self._shift_speed
        elif (move_action == PlatformAction.MOVE_RIGHT and
            self.rect.right < self._play_area_rect.right):
            self._speed[0] = self._shift_speed
        else:
            self._speed[0] = 0

        self.rect.move_ip(*self._speed)

class Blocker(pygame.sprite.Sprite):
    def __init__(self, init_pos_y, play_area_rect: pygame.Rect, *groups):
        super().__init__(*groups)

        self._play_area_rect = play_area_rect
        self._speed = [random.choice((5 , -5)), 0]

        self.rect = pygame.Rect(
            random.randrange(0, play_area_rect.width - 10, 20), init_pos_y, 30, 20)
        self.image = self._create_surface()

    def _create_surface(self):
        surface = pygame.Surface((self.rect.width, self.rect.height))
        surface.fill((213, 224, 0)) # Yellow-green
        return surface

    @property
    def pos(self):
        return self.rect.topleft

    def reset(self):
        self.rect.x = random.randrange(0, self._play_area_rect.width - 10, 20)
        self._speed = [random.choice((5, -5)), 0]

    def move(self):
        self.rect.move_ip(self._speed)

        if self.rect.left <= self._play_area_rect.left:
            self.rect.left = self._play_area_rect.left
            self._speed[0] *= -1
        elif self.rect.right >= self._play_area_rect.right:
            self.rect.right = self._play_area_rect.right
            self._speed[0] *= -1

class Ball(pygame.sprite.Sprite):
    def __init__(self, play_area_rect: pygame.Rect, enable_slide_ball: bool, *groups):
        super().__init__(*groups)

        self._play_area_rect = play_area_rect
        self._speed = [0, 0]
        self._size = [5, 5]
        self._do_slide_ball = enable_slide_ball

        self.serve_from_1P = True

        self.rect = pygame.Rect(0, 0, *self._size)
        self.image = self._create_surface()

        # Used in additional collision detection
        self.last_pos = pygame.Rect(self.rect)

    def _create_surface(self):
        surface = pygame.Surface((self.rect.width, self.rect.height))
        surface.fill((66, 226, 126))    # Green
        return surface

    @property
    def pos(self):
        return self.rect.topleft

    @property
    def speed(self):
        return tuple(self._speed)

    def reset(self):
        """
        Reset the ball status
        """
        self._speed = [0, 0]
        # Change side next time
        self.serve_from_1P = not self.serve_from_1P

    def stick_on_platform(self, platform_1P_rect, platform_2P_rect):
        """
        Stick on the either platform according to the status of `_serve_from_1P`
        """
        if self.serve_from_1P:
            self.rect.centerx = platform_1P_rect.centerx
            self.rect.y = platform_1P_rect.top - self.rect.height
        else:
            self.rect.centerx = platform_2P_rect.centerx
            self.rect.y = platform_2P_rect.bottom

    def serve(self, serve_ball_action: PlatformAction):
        """
        Set the ball speed according to the action of ball serving
        """
        self._speed[0] = {
            PlatformAction.SERVE_TO_LEFT: -7,
            PlatformAction.SERVE_TO_RIGHT: 7,
        }.get(serve_ball_action)

        self._speed[1] = -7 if self.serve_from_1P else 7

    def move(self):
        self.last_pos.topleft = self.rect.topleft
        self.rect.move_ip(self._speed)

    def speed_up(self):
        self._speed[0] += 1 if self._speed[0] > 0 else -1
        self._speed[1] += 1 if self._speed[1] > 0 else -1

    def check_bouncing(self, platform_1p: Platform, platform_2p: Platform,
        blocker: Blocker):
        # If the ball hits the play_area, adjust the position first
        # and preserve the speed after bouncing.
        hit_box = physics.rect_break_or_contact_box(self.rect, self._play_area_rect)
        if hit_box:
            self.rect, speed_after_hit_box = (
                physics.bounce_in_box(self.rect, self._speed, self._play_area_rect))

        # If the ball hits the specified sprites, adjust the position again
        # and preserve the speed after bouncing.
        hit_sprite = self._check_ball_hit_sprites((platform_1p, platform_2p, blocker))
        if hit_sprite:
            self.rect, speed_after_bounce = physics.bounce_off(
                self.rect, self._speed,
                hit_sprite.rect, hit_sprite._speed)

            # Check slicing ball when the ball is caught by the platform
            if (self._do_slide_ball and
               ((hit_sprite is platform_1p and speed_after_bounce[1] < 0) or
                (hit_sprite is platform_2p and speed_after_bounce[1] > 0))):
                speed_after_bounce[0] = self._slice_ball(self._speed, hit_sprite._speed[0])

        # Decide the final speed
        if hit_box:
            self._speed[0] = speed_after_hit_box[0]
        if hit_sprite:
            self._speed[1] = speed_after_bounce[1]
            if not hit_box:
                self._speed[0] = speed_after_bounce[0]

    def _check_ball_hit_sprites(self, sprites):
        """
        Get the first sprite in the `sprites` that the ball hits

        @param sprites An iterable object that storing the target sprites
        @return The first sprite in the `sprites` that the ball hits.
                Return None, if none of them is hit by the ball.
        """
        for sprite in sprites:
            if physics.moving_collide_or_contact(self, sprite):
                return sprite

        return None

    def _slice_ball(self, ball_speed, platform_speed_x):
        """
        Check if the platform slices the ball, and modify the ball speed
        """
        # The y speed won't be changed after ball slicing.
        # It's good for determining the x speed.
        origin_ball_speed = abs(ball_speed[1])

        # If the platform moves at the same direction as the ball moving,
        # speed up the ball.
        if platform_speed_x * ball_speed[0] > 0:
            origin_ball_speed += 3
        # If they move to the different direction,
        # reverse the ball direction.
        elif platform_speed_x * ball_speed[0] < 0:
            origin_ball_speed *= -1

        return origin_ball_speed if ball_speed[0] > 0 else -origin_ball_speed
