from essential import physics
from essential.game_base import StringEnum

import pygame
import random

class PlatformMoveAction(StringEnum):
	LEFT = "LEFT"
	RIGHT = "RIGHT"
	NONE = "NONE"

class Platform(pygame.sprite.Sprite):
	def __init__(self, init_pos, play_area_rect: pygame.Rect, *groups):
		super().__init__(*groups)

		self._play_area_rect = play_area_rect
		self._shift_speed = 5
		self._speed = [0, 0]
		self._init_pos = pygame.Rect(*init_pos, 40, 30)

		self.rect = self._init_pos.copy()

	def create_surface(self, side, color):
		self.image = pygame.Surface((self.rect.width, self.rect.height))

		# Draw the plarform image
		platform_image = pygame.Surface((self.rect.width, 10))
		platform_image.fill(color)
		# 1P is at the bottom of the platform rect
		if side == "1P":
			self.image.blit(platform_image, (0, self.image.get_height() - 10))
		# 2P is at the top of the platform rect
		else:
			self.image.blit(platform_image, (0, 0))

		# Draw the outline of the platform rect
		pygame.draw.rect(self.image, color, \
			pygame.Rect(0, 0, self.rect.width, self.rect.height), 1)

		self.image.convert()

	def reset(self):
		self.rect = self._init_pos.copy()

	def move(self, move_action: PlatformMoveAction):
		if move_action == PlatformMoveAction.LEFT and \
			self.rect.left > self._play_area_rect.left:
			self._speed[0] = -self._shift_speed
		elif move_action == PlatformMoveAction.RIGHT and \
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

	def create_surface(self):
		self.image = pygame.Surface((self.rect.width, self.rect.height))
		self.image.fill((66, 226, 126))	# Green
		self.image.convert()

	def reset(self):
		"""
		Reset the ball status and serve the ball
		"""
		# Serving the ball
		if self._serve_from_1P:
			reset_pos_x = 75
			reset_pos_y = int(self._play_area_rect.height * 0.2)
			self._speed = [7, 7]
		else:
			reset_pos_x = 120
			reset_pos_y = int(self._play_area_rect.height * 0.8 - self.rect.height)
			self._speed = [-7, -7]

		self.rect = pygame.Rect(reset_pos_x, reset_pos_y, *self._size)
		# Change side next time
		self._serve_from_1P = not self._serve_from_1P

	def move(self):
		self.rect.move_ip(self._speed)

	def speed_up(self):
		self._speed[0] += 1 if self._speed[0] > 0 else -1
		self._speed[1] += 1 if self._speed[1] > 0 else -1

	def check_bouncing(self, platform_1p: Platform, platform_2p: Platform):
		physics.bounce_in_box(self.rect, self._speed, self._play_area_rect)

		# Check if the ball hits the platform or not
		if physics.collide_or_tangent(self, platform_1p):
			target_platform = platform_1p
		elif physics.collide_or_tangent(self, platform_2p):
			target_platform = platform_2p
		else:
			target_platform = None

		if target_platform:
			physics.bounce_off_ip(self.rect, self._speed, \
				target_platform.rect, target_platform._speed)
