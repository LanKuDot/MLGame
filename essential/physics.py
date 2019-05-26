"""
The helper functions for physics
"""

from pygame import Rect
from pygame.sprite import Sprite

from collections import namedtuple

# ====== Data structure ======
class Vector2D(namedtuple("Vector2D", ["x", "y"])):
	__slots__ = ()

	def __add__(self, other):
		return Vector2D(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return Vector2D(self.x - other.x, self.y - other.y)

def collide_or_tangent(sprite_a: Sprite, sprite_b: Sprite) -> bool:
	"""
	Check if two sprites are colliding or targent
	"""
	rect_a = sprite_a.rect
	rect_b = sprite_b.rect

	if rect_a.left <= rect_b.right and \
	   rect_a.right >= rect_b.left and \
	   rect_a.top <= rect_b.bottom and \
	   rect_a.bottom >= rect_b.top:
		return True
	return False

def line_intersect(line_a, line_b) -> bool:
	"""
	Check if two line segments intersect

	@param line_a A tuple (Vector2D, Vector2D) representing both end points
	       of line segment
	@param line_b Same as `line_a`
	"""
	# line_a and line_b have the same end point
	if line_a[0] == line_b[0] or \
	   line_a[1] == line_b[0] or \
	   line_a[0] == line_b[1] or \
	   line_a[1] == line_b[1]:
		return True

	# Set line_a to (u0, u0 + v0) and p0 = u0 + s * v0, and
	# set line_b to (u1, u1 + v1) and p1 = u1 + t * v1,
	# where u, v, p are vectors and s, t is in [0, 1].
	# If line_a and line_b intersects, then p0 = p1
	# -> u0 - u1 = -s * v0 + t * v1
	# -> | u0.x - u1.x |   | v0.x  v1.x | |-s |
	#    | u0.y - u1.y | = | v0.y  v1.y | | t |
	#
	# If left-hand vector is a zero vector, then two line segments has the same end point.
	# If the right-hand matrix is not invertible, then two line segments are parallel.
	# If none of above conditions is matched, find the solution of s and t,
	# if both s and t are in [0, 1], then two line segments intersect.

	v0 = line_a[1] - line_a[0]
	v1 = line_b[1] - line_b[0]
	det = v0.x * v1.y - v0.y * v1.x
	# Two line segments are parallel
	if det == 0:
		# TODO Determine if two lines overlap
		return False

	du = line_a[0] - line_b[0]
	s_det = v1.x * du.y - v1.y * du.x
	t_det = v0.x * du.y - v0.y * du.x

	if (det > 0 and 0 <= s_det <= det and 0 <= t_det <= det) or \
	   (det < 0 and det <= s_det <= 0 and det <= t_det <= 0):
		return True

	return False

def rect_collideline(rect: Rect, line) -> bool:
	"""
	Check if line segment intersects with a rect

	@param rect The Rect of the target rectangle
	@param line A tuple (Vector2D, Vector2D) representing both end points
	       of line segment
	"""
	line_top = (Vector2D(rect.left, rect.top), Vector2D(rect.right, rect.top))
	line_bottom = (Vector2D(rect.left, rect.bottom), Vector2D(rect.right, rect.bottom))
	line_left = (Vector2D(rect.left, rect.top), Vector2D(rect.left, rect.bottom))
	line_right = (Vector2D(rect.right, rect.top), Vector2D(rect.right, rect.bottom))

	intersect_num = 0
	if line_intersect(line_top, line):    intersect_num += 1
	if line_intersect(line_bottom, line): intersect_num += 1
	if line_intersect(line_left, line):   intersect_num += 1
	if line_intersect(line_right, line):  intersect_num += 1

	if intersect_num >= 2:
		return True
	
	return False

def bounce_off_ip(bounce_obj_rect: Rect, bounce_obj_speed, \
	hit_obj_rect: Rect, hit_obj_speed):
	"""
	Update the speed and position of the `bounce_obj` after it bounces off the `hit_obj`.

	This function is called only when two objects are colliding.

	@param bounce_obj_rect The Rect of the bouncing object
	@param bounce_obj_speed The 2D speed vector of the bouncing object.
	@param hit_obj_rect The Rect of the hit object
	@param hit_obj_speed The 2D speed vector of the hit object
	"""
	# Treat the hit object as an unmoveable object
	speed_diff_x = bounce_obj_speed[0] - hit_obj_speed[0]
	speed_diff_y = bounce_obj_speed[1] - hit_obj_speed[1]

	# The relative position between top and bottom, and left and right
	# of two objects at the last frame
	rect_diff_T_B = bounce_obj_rect.top - hit_obj_rect.bottom - speed_diff_y
	rect_diff_B_T = bounce_obj_rect.bottom - hit_obj_rect.top - speed_diff_y
	rect_diff_L_R = bounce_obj_rect.left - hit_obj_rect.right - speed_diff_x
	rect_diff_R_L = bounce_obj_rect.right - hit_obj_rect.left - speed_diff_x

	# Set the position and speed of the bouncing object
	# acccroding to the relative position of two objects
	if rect_diff_T_B > 0 and rect_diff_B_T > 0:
		bounce_obj_rect.top = hit_obj_rect.bottom
		bounce_obj_speed[1] *= -1
	elif rect_diff_T_B < 0 and rect_diff_B_T < 0:
		bounce_obj_rect.bottom = hit_obj_rect.top
		bounce_obj_speed[1] *= -1

	if rect_diff_L_R > 0 and rect_diff_R_L > 0:
		bounce_obj_rect.left = hit_obj_rect.right
		bounce_obj_speed[0] *= -1
	elif rect_diff_L_R < 0 and rect_diff_R_L < 0:
		bounce_obj_rect.right = hit_obj_rect.left
		bounce_obj_speed[0] *= -1

def bounce_in_box(bounce_obj_rect: Rect, bounce_object_speed, \
	box_rect: Rect) -> bool:
	"""
	Bounce the object if it hits the border of the box.
	The speed and the position of the `bounce_obj` will be updated.

	@param bounce_obj_rect The Rect of the bouncing object
	@param bounce_obj_speed The 2D speed vector of the bouncing object.
	@return Whether the `bounce_obj` hits the box or not.
	"""
	hit = False

	if bounce_obj_rect.left <= box_rect.left:
		bounce_obj_rect.left = box_rect.left
		bounce_object_speed[0] *= -1
		hit = True
	elif bounce_obj_rect.right >= box_rect.right:
		bounce_obj_rect.right = box_rect.right
		bounce_object_speed[0] *= -1
		hit = True

	if bounce_obj_rect.top <= box_rect.top:
		bounce_obj_rect.top = box_rect.top
		bounce_object_speed[1] *= -1
		hit = True
	elif bounce_obj_rect.bottom >= box_rect.bottom:
		bounce_obj_rect.bottom = box_rect.bottom
		bounce_object_speed[1] *= -1
		hit = True

	return hit
