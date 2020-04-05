import pygame
from pygame import Rect, Surface
from pygame.math import Vector2
from pygame.sprite import Sprite
import random

from mlgame.gamedev import physics
from mlgame.utils.enum import StringEnum, auto

class Brick(Sprite):
    def __init__(self, init_pos, *groups):
        super().__init__(*groups)

        self.rect = Rect(init_pos[0], init_pos[1], 25, 10)
        self.image = self._create_surface((244, 158, 66))   # Orange

    def _create_surface(self, color):
        surface = Surface((self.rect.width, self.rect.height))
        surface.fill(color)
        pygame.draw.line(surface, (0, 0, 0),
            (self.rect.width - 1, 0), (self.rect.width - 1, self.rect.height - 1))
        pygame.draw.line(surface, (0, 0, 0),
            (0, self.rect.height - 1), (self.rect.width - 1, self.rect.height - 1))
        return surface

    @property
    def pos(self):
        return self.rect.topleft

class HardBrick(Brick):
    def __init__(self, init_pos, *groups):
        super().__init__(init_pos, *groups)

        self.reset()

    def reset(self):
        self.hp = 2
        # Override the origin color
        self.image = self._create_surface((209, 31, 31))    # Red

    def hit(self):
        """
        Decrease 1 HP and change the color of image and return the remaining HP

        @return The remaining HP
        """
        self.hp -= 1
        self.image = self._create_surface((244, 158, 66))   # Orange

        return self.hp

class PlatformAction(StringEnum):
    SERVE_TO_LEFT = auto()
    SERVE_TO_RIGHT = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    NONE = auto()

SERVE_BALL_ACTIONS = (PlatformAction.SERVE_TO_LEFT, PlatformAction.SERVE_TO_RIGHT)

class Platform(Sprite):
    def __init__(self, init_pos, play_area_rect: Rect, *groups):
        super().__init__(*groups)

        self._play_area_rect = play_area_rect
        self._shift_speed = 5
        self._speed = [0, 0]
        self._init_pos = init_pos

        self.rect = Rect(init_pos[0], init_pos[1], 40, 5)
        self.image = self._create_surface()

    def _create_surface(self):
        surface = Surface((self.rect.width, self.rect.height))
        surface.fill((66, 226, 126)) # Green
        return surface

    @property
    def pos(self):
        return self.rect.topleft

    def reset(self):
        self.rect.topleft = self._init_pos

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

class Ball(Sprite):
    def __init__(self, init_pos, play_area_rect: Rect, enable_slide_ball: bool, *groups):
        super().__init__(*groups)

        self._play_area_rect = play_area_rect
        self._do_slide_ball = enable_slide_ball
        self._init_pos = init_pos
        self._speed = [0, 0]

        self.hit_platform_times = 0

        self.rect = Rect(*self._init_pos, 5, 5)
        self.image = self._create_surface()

        # For additional collision checking
        self._last_pos = self.rect.copy()

    def _create_surface(self):
        surface = pygame.Surface((self.rect.width, self.rect.height))
        surface.fill((44, 185, 214)) # Blue
        return surface

    @property
    def pos(self):
        return self.rect.topleft

    def reset(self):
        self.hit_platform_times = 0
        self.rect.topleft = self._init_pos
        self._speed = [0, 0]

    def stick_on_platform(self, platform_centerx):
        self.rect.centerx = platform_centerx

    def serve(self, platform_action: PlatformAction):
        if platform_action == PlatformAction.SERVE_TO_LEFT:
            self._speed = [-7, -7]
        elif platform_action == PlatformAction.SERVE_TO_RIGHT:
            self._speed = [7, -7]

    def move(self):
        self._last_pos.topleft = self.rect.topleft
        self.rect.move_ip(self._speed)

    def check_bouncing(self, platform: Platform):
        if (physics.collide_or_contact(self, platform) or
            self._platform_additional_check(platform)):
            self.hit_platform_times += 1

            rect_after_bounce, speed_after_bounce = physics.bounce_off(
                self.rect, self._speed, platform.rect, platform._speed)
            # Check slicing ball when the ball goes up after bouncing (not game over)
            if self._do_slide_ball and speed_after_bounce[1] < 0:
                speed_after_bounce[0] = self._slice_ball(self._speed[0], platform._speed[0])

            self.rect = rect_after_bounce
            self._speed = speed_after_bounce

        if physics.rect_break_or_contact_box(self.rect, self._play_area_rect):
            physics.bounce_in_box_ip(self.rect, self._speed, self._play_area_rect)

    def _platform_additional_check(self, platform: Platform):
        """
        The additional checking for the condition that the ball passes the corner of the platform
        """
        if self.rect.bottom > platform.rect.top:
            routine_a = (Vector2(self._last_pos.bottomleft), Vector2(self.rect.bottomleft))
            routine_b = (Vector2(self._last_pos.bottomright), Vector2(self.rect.bottomright))

            return (physics.rect_collideline(platform.rect, routine_a) or
                    physics.rect_collideline(platform.rect, routine_b))

        return False

    def _slice_ball(self, ball_speed_x, platform_speed_x):
        """
        Check if the platform slices the ball, and modify the ball speed.

        @return The new x speed of the ball after slicing
        """
        # If the platform doesn't move, bounce normally.
        if platform_speed_x == 0:
            return 7 if ball_speed_x > 0 else -7
        # If the platform moves at the same direction as the ball moving,
        # speed up the ball.
        elif ball_speed_x * platform_speed_x > 0:
            return 10 if ball_speed_x > 0 else -10
        # If the platform moves at the opposite direction against the ball moving,
        # hit the ball back.
        else:
            return -7 if ball_speed_x > 0 else 7

    def check_hit_brick(self, group_brick: pygame.sprite.RenderPlain) -> int:
        """
        Check if the ball hits bricks in the `group_brick`.
        The hit bricks will be removed from `group_brick`, but the alive hard brick will not.
        However, if the ball speed is high, the hard brick will be removed with only one hit.

        @param group_brick The sprite group containing bricks
        @return The number of destroyed bricks
        """
        hit_bricks = pygame.sprite.spritecollide(self, group_brick, 1,
            physics.collide_or_contact)
        num_of_destroyed_brick = len(hit_bricks)

        if num_of_destroyed_brick > 0:
            # XXX: Bad multiple collision bouncing handling
            if (num_of_destroyed_brick == 2 and
                (hit_bricks[0].rect.y == hit_bricks[1].rect.y or
                 hit_bricks[0].rect.x == hit_bricks[1].rect.x)):
                combined_rect = hit_bricks[0].rect.union(hit_bricks[1].rect)
                physics.bounce_off_ip(self.rect, self._speed, combined_rect, (0, 0))
            else:
                physics.bounce_off_ip(self.rect, self._speed, hit_bricks[0].rect, (0, 0))

            if abs(self._speed[0]) == 7:
                for brick in hit_bricks:
                    if isinstance(brick, HardBrick) and brick.hit():
                        group_brick.add((brick,))
                        num_of_destroyed_brick -= 1

        return num_of_destroyed_brick
