"""
The helper functions for physics
"""

from pygame import Rect
from pygame.sprite import Sprite

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
