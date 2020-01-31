import pygame

from mlgame.utils.enum import StringEnum

from .gameobject import Ball, Platform, Brick, HardBrick, PlatformAction

class Difficulty(StringEnum):
    EASY = "EASY"
    NORMAL = "NORMAL"

class GameStatus(StringEnum):
    GAME_ALIVE = "GAME_ALIVE"
    GAME_OVER = "GAME_OVER"
    GAME_PASS = "GAME_PASS"

class SceneInfo:
    """
    The data structure for the information of the scene

    Containing the frame no, the status, and the position of the gameobjects.
    Note that the position is the coordinate at the top-left corner of the gameobject.

    @var frame The frame number of the game. Used as the timestamp.
    @var status The status of the game. It will only be one of `GameStatus`
    @var ball A (x, y) tuple which is the position of the ball.
    @var platform A (x, y) tuple which is the position of the platform.
    @var bricks A list storing (x, y) tuples which are
         the position of the remaining bricks.
    @var hard_bricks Similar to `bricks` but for hard bricks
    @var command The command decided according to this scene information
    """

    def __init__(self):
        # These members will be filled in the `Scene.get_scene_info()`.
        self.frame = -1
        self.status = None
        self.ball = None
        self.platform = None
        self.bricks = []
        self.hard_bricks = []

        # The member is filled after received the command
        self.command = None

    def __str__(self):
        output_str = \
            "# Frame {}\n".format(self.frame) + \
            "# Status {}\n".format(self.status) + \
            "# Ball {}\n".format(self.ball) + \
            "# Platform {}\n".format(self.platform) + \
            "# Brick {}\n".format(" ".join(str(brick) for brick in self.bricks)) + \
            "# HardBrick {}\n".format(" ".join(str(brick) for brick in self.hard_bricks)) + \
            "# Command {}".format(self.command)

        return output_str

class Scene:
    area_rect = pygame.Rect(0, 0, 200, 500)

    def __init__(self, difficulty, level):
        self._level = level
        self._difficulty = difficulty
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE

        self._create_scene()

    def _create_scene(self):
        self._create_moves()
        self._create_bricks(self._level)

    def _create_moves(self):
        self._group_move = pygame.sprite.RenderPlain()
        enable_slide_ball = False if self._difficulty == Difficulty.EASY else True
        self._ball = Ball(350, Scene.area_rect, enable_slide_ball, self._group_move)
        self._platform = Platform((75, 400), Scene.area_rect, self._group_move)

    def _create_bricks(self, level: int):
        def get_coordinate_and_type(string):
            string = string.rstrip("\n").split(' ')
            return int(string[0]), int(string[1]), int(string[2])

        self._group_brick = pygame.sprite.RenderPlain()
        self._brick_container = []

        import os.path
        dir_path = os.path.dirname(__file__)
        level_file_path = os.path.join(dir_path, "level_data/{0}.dat".format(level))

        with open(level_file_path, 'r') as input_file:
            offset_x, offset_y, _ = get_coordinate_and_type(input_file.readline())
            for input_pos in input_file:
                pos_x, pos_y, type = get_coordinate_and_type(input_pos.rstrip("\n"))
                if type == 0:
                    BrickType = Brick
                else:
                    BrickType = HardBrick

                brick = BrickType((pos_x + offset_x, pos_y + offset_y), \
                    self._group_brick)
                self._brick_container.append(brick)

    def reset(self):
        self._frame_count = 0
        self._game_status = GameStatus.GAME_ALIVE
        self._ball.reset()
        self._platform.reset()
        self._group_brick.empty()
        self._group_brick.add(*self._brick_container)

        # Reset the HP of hard bricks
        for brick in self._brick_container:
            if isinstance(brick, HardBrick):
                brick.reset()

    def update(self, move_action: PlatformAction) -> GameStatus:
        self._frame_count += 1

        self._ball.move()
        self._platform.move(move_action)

        self._ball.check_hit_brick(self._group_brick)
        self._ball.check_bouncing(self._platform)

        if len(self._group_brick) == 0:
            self._game_status = GameStatus.GAME_PASS
        elif self._ball.rect.top >= self._platform.rect.bottom:
            self._game_status = GameStatus.GAME_OVER
        else:
            self._game_status = GameStatus.GAME_ALIVE

        return self._game_status

    def draw_gameobjects(self, surface):
        self._group_brick.draw(surface)
        self._group_move.draw(surface)

    def get_scene_info(self) -> SceneInfo:
        """
        Get the scene information
        """
        scene_info = SceneInfo()
        scene_info.frame = self._frame_count
        scene_info.status = self._game_status.value
        scene_info.ball = self._ball.pos
        scene_info.platform = self._platform.pos
        for brick in self._group_brick:
            if isinstance(brick, HardBrick) and brick.hp == 2:
                scene_info.hard_bricks.append(brick.pos)
            else:
                scene_info.bricks.append(brick.pos)

        return scene_info
