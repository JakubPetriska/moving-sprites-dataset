import os.path
import sys
from os import listdir

from scipy import misc


def crop_sprites(sprites_dir, output_dir):
    """Crop all sprites in sprites_dir of any overhanging background and save them to output_dir.

    :param sprites_dir: Directory with sprites to be cropped.
    :param output_dir: Directory in which cropped sprites will be saved.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_names = listdir(sprites_dir)
    index = 0
    for file_name in file_names:
        file_path = os.path.join(sprites_dir, file_name)
        sprite = misc.imread(file_path)

        # Cut out top empty pixels
        for i in range(0, sprite.shape[0]):
            should_break = False
            for j in range(0, sprite.shape[1]):
                if not sprite[i, j, 3] == 0:
                    sprite = sprite[i:, :]
                    should_break = True
                    break
            if should_break:
                break

        # Cut out empty bottom pixels
        for i in range(sprite.shape[0] - 1, -1, -1):
            should_break = False
            for j in range(0, sprite.shape[1]):
                if not sprite[i, j, 3] == 0:
                    sprite = sprite[0:i, :]
                    should_break = True
                    break
            if should_break:
                break

        # Cut out empty left pixels
        for j in range(0, sprite.shape[1]):
            should_break = False
            for i in range(0, sprite.shape[0]):
                if not sprite[i, j, 3] == 0:
                    sprite = sprite[:, j:]
                    should_break = True
                    break
            if should_break:
                break

        # Cut out empty right pixels
        for j in range(sprite.shape[1] - 1, -1, -1):
            should_break = False
            for i in range(0, sprite.shape[0]):
                if not sprite[i, j, 3] == 0:
                    sprite = sprite[:, 0:j]
                    should_break = True
                    break
            if should_break:
                break

        output_file_path = os.path.join(output_dir, file_name)
        misc.imsave(output_file_path, sprite)
        index += 1
        print('%s/%s' % (index, len(file_names)))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: <sprites_dir> <output_dir>")
        sys.exit(1)
    crop_sprites(sys.argv[1], sys.argv[2])
