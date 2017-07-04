import random

import numpy as np

from generator import constants
from generator.sprite import Sprite


class SequenceGenerator:
    def __init__(self, sprites):
        self.sprites = sprites
        self.scene_sprites = []
        self.movement_functions = []
        self.scale_functions = []

        self.background_color = np.array([random.random() * 255 for i in range(3)])

        # Linear movement
        self.movement_functions.append(
            lambda initial_position, lifetime, velocity: initial_position + velocity * lifetime)
        # Linear scale with possible shearing
        self.scale_functions.append(
            lambda initial_scale, lifetime, scale_speed: np.clip(initial_scale + scale_speed * lifetime,
                                                                 constants.SPRITE_MIN_SCALE, 1))

    def _spawn_sprite(self):
        sprite = random.choice(self.sprites)
        # Select flipped sprite image with 50% probability
        sprite_image_index = random.randrange(1, 3)
        sprite_image = sprite[sprite_image_index]
        half_shape = np.array(sprite_image.shape) / 2
        initial_position = np.array((random.randrange(0, constants.RESOLUTION_HEIGHT) - half_shape[0],
                                     random.randrange(0, constants.RESOLUTION_WIDTH) - half_shape[1]))
        velocity = np.array((random.random() - 0.5, random.random() - 0.5))
        velocity /= np.linalg.norm(velocity)
        velocity *= random.gauss(mu=constants.MEAN_SPRITE_MOVEMENT_SPEED,
                                 sigma=constants.MEAN_SPRITE_MOVEMENT_SPEED / 2)

        if constants.ALLOW_SPRITE_SHEARING:
            initial_scale = np.array([random.uniform(constants.SPRITE_MIN_SCALE, 1) for i in range(0, 2)])
            scale_speed = np.array(
                [random.gauss(mu=constants.MEAN_SPRITE_SCALE_SPEED, sigma=constants.MEAN_SPRITE_SCALE_SPEED / 2)
                 for i in range(0, 2)])
        else:
            initial_scale = np.array([random.uniform(constants.SPRITE_MIN_SCALE, 0.8)] * 2)
            scale_speed = np.array([random.gauss(mu=constants.MEAN_SPRITE_SCALE_SPEED,
                                                 sigma=constants.MEAN_SPRITE_SCALE_SPEED / 2)] * 2)
        if random.random() >= 0.5:
            scale_speed *= -1
        return Sprite(sprite[0], sprite_image, initial_position, initial_scale,
                      velocity, random.choice(self.movement_functions),
                      scale_speed, random.choice(self.scale_functions))

    def _spawn_probability(self):
        zero_sprite_spawn_probability = 0.5
        slope = (0.2 - zero_sprite_spawn_probability) / constants.AVERAGE_SPRITE_COUNT
        return slope * len(self.scene_sprites) + zero_sprite_spawn_probability

    @staticmethod
    def _apply_gaussian_noise(frame, scale):
        noise = np.random.normal(size=frame.shape, scale=scale)
        frame += noise

    def generate_next_frame(self):
        for sprite in self.scene_sprites:
            sprite.increase_lifetime()

        if random.random() <= self._spawn_probability():
            self.scene_sprites.append(self._spawn_sprite())

        # Randomly adjust the background color
        # Adjust each element
        for i in range(3):
            self.background_color[i] += (random.random() - 0.5) * 2 * constants.BACKGROUND_COLOR_COMPONENT_MAX_DELTA
        # Adjust brightness
        self.background_color += [(random.random() - 0.5) * 3 * constants.BACKGROUND_COLOR_BRIGHTNESS_MAX_DELTA] * 3
        self.background_color = np.clip(self.background_color, 0, 255)

        frame = np.ones((constants.RESOLUTION_HEIGHT, constants.RESOLUTION_WIDTH, 3))
        for i in range(3):
            frame[:, :, i] *= self.background_color[i]
        SequenceGenerator._apply_gaussian_noise(frame, constants.BACKGROUND_NOISE_SCALE)

        frame_labels = []
        for i in range(len(self.scene_sprites) - 1, -1, -1):
            sprite_boundaries = self.scene_sprites[i].render(frame)
            if not sprite_boundaries:
                self.scene_sprites.pop(i)
            else:
                frame_labels.append((self.scene_sprites[i].type, sprite_boundaries))

        SequenceGenerator._apply_gaussian_noise(frame, constants.OVERALL_NOISE_SCALE)

        frame = np.clip(frame, 0, 255).astype(np.uint8)
        return frame, frame_labels
