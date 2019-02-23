import pygame

def collide_or_tangent(sprite_a, sprite_b) -> bool:
	rect_a = sprite_a.rect
	rect_b = sprite_b.rect

	if rect_a.left <= rect_b.right and \
	   rect_a.right >= rect_b.left and \
	   rect_a.top <= rect_b.bottom and \
	   rect_a.bottom >= rect_b.top:
		return True
	return False

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
		self._init_pos = pygame.Rect(init_pos[0], init_pos[1], 50, 5)
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
			self.rect.move_ip(-self._shift_speed, 0)
		elif move_action == "RIGHT" and \
		     self.rect.right < self._play_area_rect.right:
			self.rect.move_ip(self._shift_speed, 0)

class Ball(pygame.sprite.Sprite):
	def __init__(self, init_pos, play_area_rect: pygame.Rect, *groups):
		pygame.sprite.Sprite.__init__(self, *groups)

		self._play_area_rect = play_area_rect
		self._speed = [5, 5]	# (x, y)
		self._init_pos = pygame.Rect(init_pos[0], init_pos[1], 5, 5)
		self.rect = self._init_pos.copy()

	def create_surface(self):
		self.image = pygame.Surface((self.rect.width, self.rect.height))
		self.image.fill((44, 185, 214)) # Blue
		self.image.convert()

	def reset(self):
		self.rect = self._init_pos.copy()
		self._speed = [5, 5]

	def move(self):
		self.rect.move_ip(self._speed)

	def _bounce(self, target_rect: pygame.Rect):
		if (self.rect.top == target_rect.bottom and self._speed[1] < 0) or \
		   (self.rect.bottom == target_rect.top and self._speed[1] > 0):
			self._speed[1] = -self._speed[1]
		if (self.rect.right == target_rect.left and self._speed[0] > 0) or \
		   (self.rect.left == target_rect.right and self._speed[0] < 0):
			self._speed[0] = -self._speed[0]

	def check_bouncing(self, platform: pygame.sprite.Sprite) -> bool:
		self._check_platform_bouncing(platform)
		self._check_wall_bouncing()

		# Game over
		if self.rect.top >= platform.rect.bottom:
			return False
		else:
			return True

	def _check_wall_bouncing(self):
		if self.rect.left <= self._play_area_rect.left or \
		   self.rect.right >= self._play_area_rect.right:
			self._speed[0] = -self._speed[0]
		if self.rect.top <= self._play_area_rect.top or \
		   self.rect.bottom >= self._play_area_rect.bottom:
			self._speed[1] = -self._speed[1]

	def _check_platform_bouncing(self, platform: pygame.sprite.Sprite):
		if collide_or_tangent(self, platform):
			self._bounce(platform.rect)

	def check_hit_brick(self, group_brick: pygame.sprite.RenderPlain) -> int:
		hit_bricks = pygame.sprite.spritecollide(self, group_brick, 1, \
			collide_or_tangent)

		if len(hit_bricks) > 0:
			self._bounce(hit_bricks[0].rect)

		return len(hit_bricks)

	def _print_rect(self, name, rect):
		print("{0}: (T: {1}, B: {2}, L: {3}, R: {4})" \
			.format(name, rect.top, rect.bottom, rect.left, rect.right))
