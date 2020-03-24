"""
The helper functions for physics
"""

from pygame import Rect
from pygame.sprite import Sprite
from pygame.math import Vector2

def collide_or_contact(sprite_a: Sprite, sprite_b: Sprite) -> bool:
    """
    Check if two sprites are colliding or contacting
    """
    rect_a = sprite_a.rect
    rect_b = sprite_b.rect

    if (rect_a.left <= rect_b.right and
        rect_a.right >= rect_b.left and
        rect_a.top <= rect_b.bottom and
        rect_a.bottom >= rect_b.top):
        return True
    return False

def moving_collide_or_contact(moving_sprite: Sprite, sprite: Sprite) -> bool:
    """
    Check if the moving sprite collides or contacts another sprite.

    @param moving_sprite The sprite that moves in the scene.
           It must contain `rect` and `last_pos` attributes, which both are `pygame.Rect`.
    @param sprite The sprite that will be collided or contacted by `moving_sprite`.
           It must contain `rect` attribute, which is also `pygame.Rect`.
    """
    # Generate the routine of 4 corners of the moving sprite
    move_rect = moving_sprite.rect
    move_last_pos = moving_sprite.last_pos
    routines = (
        (Vector2(move_last_pos.topleft), Vector2(move_rect.topleft)),
        (Vector2(move_last_pos.topright), Vector2(move_rect.topright)),
        (Vector2(move_last_pos.bottomleft), Vector2(move_rect.bottomleft)),
        (Vector2(move_last_pos.bottomright), Vector2(move_rect.bottomright))
    )

    # Check any of routines collides the rect
    ## Take the bottom and right into account when using the API of pygame
    rect_expanded = sprite.rect.inflate(1, 1)
    for routine in routines:
        # Exclude the case that the `moving_sprite` goes from the surface of `sprite`
        if (not rect_expanded.collidepoint(routine[0]) and
            rect_collideline(sprite.rect, routine)):
            return True

    return False

def line_intersect(line_a, line_b) -> bool:
    """
    Check if two line segments intersect

    @param line_a A tuple (Vector2, Vector2) representing both end points
           of line segment
    @param line_b Same as `line_a`
    """
    # line_a and line_b have the same end point
    if (line_a[0] == line_b[0] or
        line_a[1] == line_b[0] or
        line_a[0] == line_b[1] or
        line_a[1] == line_b[1]):
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

    if ((det > 0 and 0 <= s_det <= det and 0 <= t_det <= det) or
        (det < 0 and det <= s_det <= 0 and det <= t_det <= 0)):
        return True

    return False

def rect_collideline(rect: Rect, line) -> bool:
    """
    Check if line segment intersects with a rect

    @param rect The Rect of the target rectangle
    @param line A tuple (Vector2, Vector2) representing both end points
           of line segment
    """
    # Either of line ends is in the target rect.
    rect_expanded = rect.inflate(1, 1)  # Take the bottom and right line into account
    if rect_expanded.collidepoint(line[0]) or rect_expanded.collidepoint(line[1]):
        return True

    line_top = (Vector2(rect.topleft), Vector2(rect.topright))
    line_bottom = (Vector2(rect.bottomleft), Vector2(rect.bottomright))
    line_left = (Vector2(rect.topleft), Vector2(rect.bottomleft))
    line_right = (Vector2(rect.topright), Vector2(rect.bottomright))

    return (line_intersect(line_top, line) or
        line_intersect(line_bottom, line) or
        line_intersect(line_left, line) or
        line_intersect(line_right, line))

def rect_break_or_contact_box(rect: Rect, box: Rect):
    """
    Determine if the `rect` breaks the `box` or it contacts the border of `box`

    @param rect The Rect of the target rectangle
    @param box The target box
    """
    return (
        rect.left <= box.left or
        rect.right >= box.right or
        rect.top <= box.top or
        rect.bottom >= box.bottom)

def bounce_off_ip(bounce_obj_rect: Rect, bounce_obj_speed,
    hit_obj_rect: Rect, hit_obj_speed):
    """
    Calculate the speed and position of the `bounce_obj` after it bounces off the `hit_obj`.
    The position of `bounce_obj_rect` and the value of `bounce_obj_speed` will be updated.

    This function should be called only when two objects are colliding.

    @param bounce_obj_rect The Rect of the bouncing object
    @param bounce_obj_speed The 2D speed vector of the bouncing object.
    @param hit_obj_rect The Rect of the hit object
    @param hit_obj_speed The 2D speed vector of the hit object
    """
    # Treat the hit object as an unmovable object
    speed_diff_x = bounce_obj_speed[0] - hit_obj_speed[0]
    speed_diff_y = bounce_obj_speed[1] - hit_obj_speed[1]

    # The relative position between top and bottom, and left and right
    # of two objects at the last frame
    rect_diff_bT_hB = hit_obj_rect.bottom - bounce_obj_rect.top + speed_diff_y
    rect_diff_bB_hT = hit_obj_rect.top - bounce_obj_rect.bottom + speed_diff_y
    rect_diff_bL_hR = hit_obj_rect.right - bounce_obj_rect.left + speed_diff_x
    rect_diff_bR_hL = hit_obj_rect.left - bounce_obj_rect.right + speed_diff_x

    # Get the surface distance from the bouncing object to the hit object
    # and the new position for the bouncing object if it really hit the object
    # according to their relative position
    ## The bouncing object is at the bottom
    if rect_diff_bT_hB < 0 and rect_diff_bB_hT < 0:
        surface_diff_y = rect_diff_bT_hB
        extract_pos_y = hit_obj_rect.bottom
    ## The bouncing object is at the top
    elif rect_diff_bT_hB > 0 and rect_diff_bB_hT > 0:
        surface_diff_y = rect_diff_bB_hT
        extract_pos_y = hit_obj_rect.top - bounce_obj_rect.height
    else:
        surface_diff_y = -1 if speed_diff_y > 0 else 1

    ## The bouncing object is at the right
    if rect_diff_bL_hR < 0 and rect_diff_bR_hL < 0:
        surface_diff_x = rect_diff_bL_hR
        extract_pos_x = hit_obj_rect.right
    ## The bouncing object is at the left
    elif rect_diff_bL_hR > 0 and rect_diff_bR_hL > 0:
        surface_diff_x = rect_diff_bR_hL
        extract_pos_x = hit_obj_rect.left - bounce_obj_rect.width
    else:
        surface_diff_x = -1 if speed_diff_x > 0 else 1

    # Calculate the duration to hit the surface for x and y coordination.
    time_hit_y = surface_diff_y / speed_diff_y
    time_hit_x = surface_diff_x / speed_diff_x

    if time_hit_y >= 0 and time_hit_y >= time_hit_x:
        bounce_obj_speed[1] *= -1
        bounce_obj_rect.y = extract_pos_y

    if time_hit_x >= 0 and time_hit_y <= time_hit_x:
        bounce_obj_speed[0] *= -1
        bounce_obj_rect.x = extract_pos_x

def bounce_off(bounce_obj_rect: Rect, bounce_obj_speed,
    hit_obj_rect: Rect, hit_obj_speed):
    """
    The alternative version of `bounce_off_ip`. The function returns the result
    instead of updating the value of `bounce_obj_rect` and `bounce_obj_speed`.

    @return A tuple (`new_bounce_obj_rect`, `new_bounce_obj_speed`)
    """
    new_bounce_obj_rect = bounce_obj_rect.copy()
    new_bounce_obj_speed = bounce_obj_speed.copy()

    bounce_off_ip(new_bounce_obj_rect, new_bounce_obj_speed,
        hit_obj_rect, hit_obj_speed)

    return new_bounce_obj_rect, new_bounce_obj_speed

def bounce_in_box_ip(bounce_obj_rect: Rect, bounce_obj_speed,
    box_rect: Rect):
    """
    Bounce the object if it hits the border of the box.
    The speed and the position of the `bounce_obj` will be updated.

    @param bounce_obj_rect The Rect of the bouncing object
    @param bounce_obj_speed The 2D speed vector of the bouncing object.
    """
    if bounce_obj_rect.left <= box_rect.left:
        bounce_obj_rect.left = box_rect.left
        bounce_obj_speed[0] *= -1
    elif bounce_obj_rect.right >= box_rect.right:
        bounce_obj_rect.right = box_rect.right
        bounce_obj_speed[0] *= -1

    if bounce_obj_rect.top <= box_rect.top:
        bounce_obj_rect.top = box_rect.top
        bounce_obj_speed[1] *= -1
    elif bounce_obj_rect.bottom >= box_rect.bottom:
        bounce_obj_rect.bottom = box_rect.bottom
        bounce_obj_speed[1] *= -1

def bounce_in_box(bounce_obj_rect: Rect, bounce_obj_speed,
    box_rect: Rect):
    """
    The alternative version of `bounce_in_box_ip`. The function returns the result
    instead of updating the value of `bounce_obj_rect` and `bounce_obj_speed`.

    @return A tuple (new_bounce_obj_rect, new_bounce_obj_speed)
    """
    new_bounce_obj_rect = bounce_obj_rect.copy()
    new_bounce_obj_speed = bounce_obj_speed.copy()

    bounce_in_box_ip(new_bounce_obj_rect, new_bounce_obj_speed, box_rect)

    return (new_bounce_obj_rect, new_bounce_obj_speed)
