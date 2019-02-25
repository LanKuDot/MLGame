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

	def _bounce(self, target_rect: pygame.Rect, target_speed):
		speed_diff_x = self._speed[0] - target_speed[0]
		speed_diff_y = self._speed[1] - target_speed[1]

		# The distance between top and bottom, or left and right of two objects
		# in the last frame.
		rect_diff_T_B = self.rect.top - target_rect.bottom - speed_diff_y
		rect_diff_B_T = self.rect.bottom - target_rect.top - speed_diff_y
		rect_diff_L_R = self.rect.left - target_rect.right - speed_diff_x
		rect_diff_R_L = self.rect.right - target_rect.left - speed_diff_x

		# Decide the relative position from the ball to the hit object
		# to adjust the ball's position and change the moving direction
		if rect_diff_T_B > 0 and rect_diff_B_T > 0:
			self.rect.top = target_rect.bottom
			self._speed[1] = -self._speed[1]
		elif rect_diff_T_B < 0 and rect_diff_B_T < 0:
			self.rect.bottom = target_rect.top
			self._speed[1] = -self._speed[1]

		if rect_diff_L_R > 0 and rect_diff_R_L > 0:
			self.rect.left = target_rect.right
			self._speed[0] = -self._speed[0]
		elif rect_diff_L_R < 0 and rect_diff_R_L < 0:
			self.rect.right = target_rect.left
			self._speed[0] = -self._speed[0]

	def check_bouncing(self, platform: Platform) -> bool:
		self._check_platform_bouncing(platform)
		self._check_wall_bouncing()

		# Game over
		if self.rect.top >= platform.rect.bottom:
			return False
		else:
			return True

	def _check_wall_bouncing(self):
		if self.rect.left <= self._play_area_rect.left:
			self.rect.left = self._play_area_rect.left
			self._speed[0] = -self._speed[0]
		elif self.rect.right >= self._play_area_rect.right:
			self.rect.right = self._play_area_rect.right
			self._speed[0] = -self._speed[0]

		if self.rect.top <= self._play_area_rect.top:
			self.rect.top = self._play_area_rect.top
			self._speed[1] = -self._speed[1]
		elif self.rect.bottom >= self._play_area_rect.bottom:
			self.rect.bottom = self._play_area_rect.bottom
			self._speed[1] = -self._speed[1]

	def _check_platform_bouncing(self, platform: Platform):
		if collide_or_tangent(self, platform):
			self._bounce(platform.rect, platform._speed)

	def check_hit_brick(self, group_brick: pygame.sprite.RenderPlain) -> int:
		hit_bricks = pygame.sprite.spritecollide(self, group_brick, 1, \
			collide_or_tangent)

		if len(hit_bricks) > 0:
			# XXX: Bad multiple collision bouncing handling
			if len(hit_bricks) == 2 and \
				hit_bricks[0].rect.y == hit_bricks[1].rect.y:
				combined_rect = hit_bricks[0].rect.union(hit_bricks[1].rect)
				self._bounce(combined_rect, (0, 0))
			else:
				self._bounce(hit_bricks[0].rect, (0, 0))

		return len(hit_bricks)
