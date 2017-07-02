import os.path
import os.path
import shutil
from os import listdir

from scipy import misc

try:
    from tqdm import tqdm
except ImportError:
    print('!!! Install tqdm library for better progress information !!!\n')

from generator import constants
from generator import utils
from generator.sequence_generator import SequenceGenerator
from utils import timing

SHOW_VIDEO_ENCODING_INFO_LOG = False
SHOW_TIME_LOG = False


def generate_sequence(frame_count, folder_path):
    if frame_count <= 0:
        return

    images_dir = os.path.join(folder_path, constants.DATASET_IMAGES_DIR)
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    sprites = []
    for sprite_file_name in listdir(constants.SPRITES_DIR):
        sprite_type = sprite_file_name.split('_')[0]
        image = misc.imread(os.path.join(constants.SPRITES_DIR, sprite_file_name))
        scale_factor = constants.RESOLUTION_WIDTH / image.shape[1]
        scaled_shape = [int(d * scale_factor) for d in image.shape]
        scaled_shape[2:] = image.shape[2:]
        image = misc.imresize(image, scaled_shape)
        sprites.append((sprite_type, image))

    # Generate the video frames
    sequence_generator = SequenceGenerator(sprites)
    frame_image_path_format = os.path.join(images_dir, constants.FRAME_IMAGE_FILE_NAME_FORMAT)
    sequence_labels = []

    def generate_frame(index):
        frame, frame_labels = sequence_generator.generate_next_frame()
        sequence_labels.append([index] + frame_labels)
        misc.imsave(frame_image_path_format % index, frame)

    frame_indexes = range(0, frame_count)
    try:
        for i in tqdm(frame_indexes, unit='frames'):
            generate_frame(i)
    except NameError:
        for i in frame_indexes:
            generate_frame(i)

    print('\tFrames generated')

    # Generate video file
    video_encoding_start = timing.start_timer()
    utils.create_video(images_dir, os.path.join(folder_path, constants.DATASET_VIDEO_FILE),
                       SHOW_VIDEO_ENCODING_INFO_LOG)
    print('\tVideo file generated')
    if SHOW_TIME_LOG:
        print('\t\tGenerated video in %.1f seconds' % timing.get_duration_secs(video_encoding_start))

    utils.write_labels(os.path.join(folder_path, constants.DATASET_LABELS_FILE), sequence_labels)
    print('\tLabels saved')

    annotation_start = timing.start_timer()
    utils.annotate_dataset(images_dir, os.path.join(folder_path, constants.DATASET_LABELS_FILE),
                           os.path.join(folder_path, constants.DATASET_IMAGES_ANNOTATED_DIR),
                           os.path.join(folder_path, constants.DATASET_VIDEO_ANNOTATED_FILE),
                           SHOW_VIDEO_ENCODING_INFO_LOG)
    print('\tAnnotated data created')
    if SHOW_TIME_LOG:
        print('\t\tAnnotated dataset in %.1f seconds' % timing.get_duration_secs(annotation_start))


if __name__ == "__main__":
    print('Saving dataset into %s' % constants.OUTPUT_PATH)
    if os.path.exists(constants.OUTPUT_PATH):
        print('\nOld dataset needs to be removed')
        input('Are you sure? (Press Enter to continue)')
        shutil.rmtree(constants.OUTPUT_PATH, ignore_errors=True)

    print('\nGenerating training data')
    generate_sequence(constants.FRAME_COUNT_TRAINING,
                      os.path.join(constants.OUTPUT_PATH, constants.TRAINING_DATASET_PATH))
    print('\nGenerating validation data')
    generate_sequence(constants.FRAME_COUNT_VALIDATION,
                      os.path.join(constants.OUTPUT_PATH, constants.VALIDATION_DATASET_PATH))
    print('\nGenerating test data')
    generate_sequence(constants.FRAME_COUNT_TEST,
                      os.path.join(constants.OUTPUT_PATH, constants.TEST_DATASET_PATH))
