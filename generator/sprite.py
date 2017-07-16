import numpy as np
from scipy import misc

from generator import constants


class Sprite:
    def __init__(self, type, image, initial_position, initial_scale, velocity, movement_function,
                 scale_speed, scale_function):
        self.type = type
        self.image = image
        self.lifetime = 0
        self.initial_position = initial_position
        self.initial_scale = initial_scale
        self.velocity = velocity
        self.movement_function = movement_function
        self.scale_speed = scale_speed
        self.scale_function = scale_function

    def increase_lifetime(self):
        self.lifetime += 1 / constants.FRAMES_PER_SECOND

    def render(self, frame):
        position = np.round(self.movement_function(self.initial_position, self.lifetime, self.velocity)) \
            .astype(np.int64)
        scale = self.scale_function(self.initial_scale, self.lifetime, self.scale_speed)

        scaled_sprite_image_size \
            = (round(scale[0] * self.image.shape[0]), round(scale[1] * self.image.shape[1]))
        scaled_sprite_image_size = [int(a) for a in scaled_sprite_image_size]
        top = position[0]
        bottom = top + scaled_sprite_image_size[0]
        left = position[1]
        right = left + scaled_sprite_image_size[1]
        if bottom < 0 or top >= constants.RESOLUTION_HEIGHT \
                or right < 0 or left >= constants.RESOLUTION_WIDTH:
            return None
        else:
            scaled_sprite = misc.imresize(self.image, scaled_sprite_image_size)
            # Take only the visible part of sprite
            overlap_top = max(top * -1, 0)
            overlap_bottom = max(bottom - constants.RESOLUTION_HEIGHT + 1, 0)
            overlap_left = max(left * -1, 0)
            overlap_right = max(right - constants.RESOLUTION_WIDTH + 1, 0)
            scaled_sprite \
                = scaled_sprite[overlap_top:scaled_sprite_image_size[0] - overlap_bottom,
                  overlap_left:scaled_sprite_image_size[1] - overlap_right, :]
            position = np.clip(position,
                               0, max(constants.RESOLUTION_HEIGHT, constants.RESOLUTION_WIDTH))
            sprite_alpha = scaled_sprite[:, :, 3] / 255
            background_alpha = -sprite_alpha + 1
            for i in range(0, 3):
                frame[position[0]:position[0] + scaled_sprite.shape[0],
                position[1]:position[1] + scaled_sprite.shape[1], i] \
                    *= background_alpha
                frame[position[0]:position[0] + scaled_sprite.shape[0],
                position[1]:position[1] + scaled_sprite.shape[1], i] \
                    += scaled_sprite[:, :, i] * sprite_alpha

            return 0 if overlap_top > 0 else top, bottom - overlap_bottom, \
                   0 if overlap_left > 0 else left, right - overlap_right
