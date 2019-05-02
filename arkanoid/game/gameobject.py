import pygame
from essential import physics

class Brick(pygame.sprite.Sprite):
	def __init__(self, init_pos, *groups):
		pygame.sprite.Sprite.__init__(self, *groups)

		self.rect = pygame.Rect(init_pos[0], init_pos[1], 25, 10)

	def create_surface(self):
		self.image = pygame.Surface((self.rect.width, self.rect.height))
		self.image.fill((244, 158, 66)) # Orange
		pygame.draw.line(self.image, (0, 0, 0), \
			(self.rect.width - 1, 0), (self.rect.width - 1, self.rect.height - 1))
		pygame.draw.line(self.image, (0, 0, 0), \
			(0, self.rect.height - 1), (self.rect.width - 1, self.rect.height - 1))
		self.image.convert()

class Platform(pygame.sprite.Sprite):
	def __init__(self, init_pos, play_area_rect: pygame.Rect, *groups):
		pygame.sprite.Sprite.__init__(self, *groups)

		self._play_area_rect = play_area_rect
		self._shift_speed = 5
		self._speed = [0, 0]
		self._init_pos = pygame.Rect(init_pos[0], init_pos[1], 40, 5)
		self.rect = self._init_pos.copy()

	def create_surface(self):
		self.image = pygame.Surface((self.rect.width, self.rect.height))
		self.image.fill((66, 226, 126)) # Green
		self.image.convert()

	def reset(self):
		self.rect = self._init_pos.copy()

	def move(self, move_action: str):
		if move_action == "LEFT" and \
		   self.rect.left > self._play_area_rect.left:
			self._speed[0] = -self._shift_speed
		elif move_action == "RIGHT" and \
		     self.rect.right < self._play_area_rect.right:
			self._speed[0] = self._shift_speed
		else:
			self._speed[0] = 0

		self.rect.move_ip(*self._speed)

class Ball(pygame.sprite.Sprite):
	def __init__(self, init_pos, play_area_rect: pygame.Rect, *groups):
		pygame.sprite.Sprite.__init__(self, *groups)

		self._play_area_rect = play_area_rect
		self._speed = [7, 7]	# (x, y)
		self._init_pos = pygame.Rect(init_pos[0], init_pos[1], 5, 5)
		self.rect = self._init_pos.copy()

	def create_surface(self):
		self.image = pygame.Surface((self.rect.width, self.rect.height))
		self.image.fill((44, 185, 214)) # Blue
		self.image.convert()

	def reset(self):
		self.rect = self._init_pos.copy()
		self._speed = [7, 7]

	def move(self):
		self.rect.move_ip(self._speed)

	def check_bouncing(self, platform: Platform) -> bool:
		if physics.collide_or_tangent(self, platform):
			physics.bounce_off_ip(self.rect, self._speed, platform.rect, platform._speed)
		physics.bounce_in_box(self.rect, self._speed, self._play_area_rect)

		# Game over
		if self.rect.top >= platform.rect.bottom:
			return False
		else:
			return True

	def check_hit_brick(self, group_brick: pygame.sprite.RenderPlain) -> int:
		hit_bricks = pygame.sprite.spritecollide(self, group_brick, 1, \
			physics.collide_or_tangent)

		if len(hit_bricks) > 0:
			# XXX: Bad multiple collision bouncing handling
			if len(hit_bricks) == 2 and \
				hit_bricks[0].rect.y == hit_bricks[1].rect.y:
				combined_rect = hit_bricks[0].rect.union(hit_bricks[1].rect)
				physics.bounce_off_ip(self.rect, self._speed, combined_rect, (0, 0))
			else:
				physics.bounce_off_ip(self.rect, self._speed, hit_bricks[0].rect, (0, 0))

		return len(hit_bricks)
