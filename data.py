import os
import sys

import cv2
import numpy as np
import tensorflow as tf

import config
import download

class SALICON:
    """This class represents the SALICON dataset. It consists of 10000 training
       and 5000 validation images. The corresponding mouse tracking maps were
       acquired from 16 observers during free-viewing of images for 5 seconds.
       All stimuli are of size 480x640 pixels (height by width).

    Attributes:
        n_train: Number of training instances as defined in the dataset.
        n_valid: Number of validation instances as defined in the dataset.

    Returns:
        tuple: A tuple that consists of dataset objects holding the training
               and validation set instances respectively.

    .. seealso:: M. Jiang, S. Huang, J. Duan, Q. Zhao, SALICON: Saliency in
                 context, Proceedings of the IEEE Conference on Computer Vision
                 and Pattern Recognition (2015) 1072–1080.
    """

    n_train = 10000
    n_valid = 5000

    def __init__(self, data_path):
        self._target_size = config.DIMS["image_size_salicon"]

        self._dir_stimuli_train = data_path + "stimuli/train"
        self._dir_stimuli_valid = data_path + "stimuli/val"

        self._dir_saliency_train = data_path + "saliency/train"
        self._dir_saliency_valid = data_path + "saliency/val"

        if not os.path.exists(data_path):
            parent_path = os.path.dirname(data_path[:-1])
            parent_path = os.path.join(parent_path, "")

            download.download_salicon(parent_path)

    def load_data(self):
        train_list_x = _get_file_list(self._dir_stimuli_train)
        train_list_y = _get_file_list(self._dir_saliency_train)

        _check_consistency(zip(train_list_x, train_list_y), 10000)

        train_set = _fetch_dataset((train_list_x, train_list_y),
                                   self._target_size, True)

        valid_list_x = _get_file_list(self._dir_stimuli_valid)
        valid_list_y = _get_file_list(self._dir_saliency_valid)

        _check_consistency(zip(valid_list_x, valid_list_y), 5000)

        valid_set = _fetch_dataset((valid_list_x, valid_list_y),
                                   self._target_size, False)

        return (train_set, valid_set)


class MIT1003:
    """This class represents the MIT1003 dataset. It consists of 1003 natural
       images. The corresponding fixation maps were acquired from 15 observers
       during free-viewing of images for 3 seconds. The largest dimension of
       all stimuli is of size 1024 pixels.

    Attributes:
        n_train: Assigned number of training instances (must sum to 1003).
        n_valid: Assigned number of validation instances (must sum to 1003).

    Returns:
        tuple: A tuple that consists of dataset objects holding the training
               and validation set instances respectively.

    .. seealso:: T. Judd, K. Ehinger, F. Durand, A. Torralba, Learning to
                 predict where humans look, Proceedings of the International
                 Conference on Computer Vision (2009) 2106–2113.
    """

    n_train = 803
    n_valid = 200

    def __init__(self, data_path):
        self._target_size = config.DIMS["image_size_mit1003"]

        self._dir_stimuli = data_path + "stimuli"
        self._dir_saliency = data_path + "saliency"

        if not os.path.exists(data_path):
            parent_path = os.path.dirname(data_path[:-1])
            parent_path = os.path.join(parent_path, "")

            download.download_mit1003(parent_path)

    def load_data(self):
        list_x = _get_file_list(self._dir_stimuli)
        list_y = _get_file_list(self._dir_saliency)

        _check_consistency(zip(list_x, list_y), 1003)

        indices = _get_random_indices(1003)
        excerpt = indices[:self.n_train]

        train_list_x = [list_x[idx] for idx in excerpt]
        train_list_y = [list_y[idx] for idx in excerpt]

        train_set = _fetch_dataset((train_list_x, train_list_y),
                                   self._target_size, True)

        excerpt = indices[self.n_train:]

        valid_list_x = [list_x[idx] for idx in excerpt]
        valid_list_y = [list_y[idx] for idx in excerpt]

        valid_set = _fetch_dataset((valid_list_x, valid_list_y),
                                   self._target_size, False)

        return (train_set, valid_set)


class CAT2000:
    """This class represents the CAT2000 dataset. It consists of 2000 images
       evenly divided into 20 categories. The corresponding fixation maps were
       acquired from 18 observers during free-viewing of images for 5 seconds.
       All stimuli are of size 1080x1920 pixels (height by width).

    Attributes:
        n_train: Assigned number of training instances (must sum to 2000).
        n_valid: Assigned number of validation instances (must sum to 2000).

    Returns:
        tuple: A tuple that consists of dataset objects holding the training
               and validation set instances respectively.

    .. seealso:: A. Borji, L. Itti, CAT2000: A large scale fixation dataset for
                 boosting saliency research, arXiv preprint arXiv:1505.03581
                 (2015).
    """

    n_train = 1600
    n_valid = 400

    def __init__(self, data_path):
        self._target_size = config.DIMS["image_size_cat2000"]

        self._dir_stimuli = data_path + "stimuli"
        self._dir_saliency = data_path + "saliency"

        if not os.path.exists(data_path):
            parent_path = os.path.dirname(data_path[:-1])
            parent_path = os.path.join(parent_path, "")

            download.download_cat2000(parent_path)

    def load_data(self):
        list_x = _get_file_list(self._dir_stimuli)
        list_y = _get_file_list(self._dir_saliency)

        _check_consistency(zip(list_x, list_y), 2000)

        indices = _get_random_indices(100)

        # sample uniformly from all 20 categories
        ratio = self.n_train * 100 // 2000
        excerpt = np.tile(indices[:ratio], 20)

        for idx, _ in enumerate(excerpt):
            excerpt[idx] = excerpt[idx] + idx // ratio * 100

        train_list_x = [list_x[idx] for idx in excerpt]
        train_list_y = [list_y[idx] for idx in excerpt]

        train_set = _fetch_dataset((train_list_x, train_list_y),
                                   self._target_size, True)

        # sample uniformly from all 20 categories
        ratio = self.n_valid * 100 // 2000
        excerpt = np.tile(indices[-ratio:], 20)

        for idx, _ in enumerate(excerpt):
            excerpt[idx] = excerpt[idx] + idx // ratio * 100

        valid_list_x = [list_x[idx] for idx in excerpt]
        valid_list_y = [list_y[idx] for idx in excerpt]

        valid_set = _fetch_dataset((valid_list_x, valid_list_y),
                                   self._target_size, False)

        return (train_set, valid_set)


class TEST:
    """This class represents test set instances used for inference through
       a trained network. All stimuli are resized to the preferred spatial
       dimensions of the chosen model. This can, however, lead to cases of
       excessive image padding.

    Returns:
        object: A dataset object that holds all test set instances
                specified under the path variable.
    """

    def __init__(self, dataset, data_path, video_file):
        self._target_size = config.DIMS["image_size_%s" % dataset]
        self.video_file = video_file
        self._dir_stimuli_test = data_path

    def load_data(self):
        test_list_x = _get_file_list(self._dir_stimuli_test)

        test_set = _fetch_dataset(test_list_x, self._target_size,
                                  False, self.video_file, online=True)
        return test_set


def get_dataset_iterator(phase, dataset, data_path, video_file):
    """Entry point to make an initializable dataset iterator for either
       training or testing a model by calling the respective dataset class.

    Args:
        phase (str): Holds the current phase, which can be "train" or "test".
        dataset (str): Denotes the dataset to be used during training or the
                       suitable resizing procedure when testing a model.
        data_path (str): Points to the directory where training or testing
                         data instances are stored.

    Returns:
        iterator: An initializable dataset iterator holding the relevant data.
        initializer: An operation required to initialize the correct iterator.
    """

    if phase == "train":
        current_module = sys.modules[__name__]
        class_name = "%s" % dataset.upper()

        dataset_class = getattr(current_module, class_name)(data_path)
        train_set, valid_set = dataset_class.load_data()

        iterator = tf.data.Iterator.from_structure(train_set.output_types,
                                                   train_set.output_shapes)
        next_element = iterator.get_next()

        train_init_op = iterator.make_initializer(train_set)
        valid_init_op = iterator.make_initializer(valid_set)

        return next_element, train_init_op, valid_init_op

    if phase == "test":
        test_class = TEST(dataset, data_path, video_file)
        test_set = test_class.load_data()

        iterator = tf.data.Iterator.from_structure(test_set.output_types,
                                                   test_set.output_shapes)
        next_element = iterator.get_next()

        init_op = iterator.make_initializer(test_set)

        return next_element, init_op


def postprocess_saliency_map(saliency_map, target_size):
    """This function resizes and crops a single saliency map to the original
       dimensions of the input image. The output is then encoded as a jpeg
       file suitable for saving to disk.

    Args:
        saliency_map (tensor, float32): 3D tensor that holds the values of a
                                        saliency map in the range from 0 to 1.
        target_size (tensor, int32): 1D tensor that specifies the size to which
                                     the saliency map is resized and cropped.

    Returns:
        tensor, str: A tensor of the saliency map encoded as a jpeg file.
    """

    saliency_map *= 255.0

    saliency_map = _resize_image(saliency_map, target_size, True)
    saliency_map = _crop_image(saliency_map, target_size)

    saliency_map = tf.round(saliency_map)
    saliency_map = tf.cast(saliency_map, tf.uint8)

    saliency_map_jpeg = tf.image.encode_jpeg(saliency_map, "grayscale", 100)

    return saliency_map_jpeg

def _fetch_dataset(files, target_size, shuffle, video_file, online=False):
    """Here the list of file directories is shuffled (only when training),
       loaded, batched, and prefetched to ensure high GPU utilization.

    Args:
        files (list, str): A list that holds the paths to all file instances.
        target_size (tuple, int): A tuple that specifies the size to which
                                  the data will be reshaped.
        shuffle (bool): Determines whether the dataset will be shuffled or not.
        online (bool, optional): Flag that decides whether the batch size must
                                 be 1 or can take any value. Defaults to False.

    Returns:
        object: A dataset object that contains the batched and prefetched data
                instances along with their shapes and file paths.
    """
    # if shuffle:
    #     dataset = dataset.shuffle(len(files[0]))
    #
    # dataset = dataset.map(lambda *files: _tf_parse_video_files(files, target_size),
    #                       num_parallel_calls=4)

    video, original_size, files = _tf_parse_video_files([video_file], target_size)
    # We process the video 50 frames at a time
    dataset = tf.data.Dataset.from_tensor_slices(video)
    dataset = dataset.map(lambda frame: (frame, original_size, files))
    dataset = dataset.batch(100)
    dataset = dataset.prefetch(2)

    return dataset

def _tf_parse_video_files(files, target_size):
  [image, original_size, files] = \
        tf.py_func(_parse_video_files,
            [files, target_size], [tf.float32, tf.int64, tf.string])
  image.set_shape([None, target_size[0], target_size[1], 3])
  return image, original_size, files

def _parse_video_files(files, target_size):
    assert len(files) == 1

    frames_list = []

    path_tensor = files[0]
    path = path_tensor.decode("utf-8")

    cap = cv2.VideoCapture(path)
    while cap.isOpened():
      ret, frame = cap.read()
      if ret:
        original_size = frame.shape[:2]
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = _resize_image(image, target_size, is_numpy=True)
        image = _np_pad_image(image, target_size)
        image = image.astype(np.float32)

        frames_list.append(image)
      else:
        break
    cap.release()

    # Stack all frames along the 0th dimension, as if there was a batch of frames to feed to the
    # network.
    video = np.stack(frames_list)
    return video, original_size, files

def _parse_image_files(files, target_size):
    """This function reads image data dependent on the image type and
       whether it constitutes a stimulus or saliency map. All instances
       are then reshaped and padded to yield the target dimensionality.

    Args:
        files (tuple, str): A tuple with the paths to all file instances.
                            The first element contains the stimuli and, if
                            present, the second one the ground truth maps.
        target_size (tuple, int): A tuple that specifies the size to which
                                  the data will be reshaped.

    Returns:
        list: A list that holds the image instances along with their
              shapes and file paths.
    """

    image_list = []

    for count, filename in enumerate(files):
        image_str = tf.read_file(filename)
        channels = 3 if count == 0 else 1

        image = tf.cond(tf.image.is_jpeg(image_str),
                        lambda: tf.image.decode_jpeg(image_str,
                                                     channels=channels),
                        lambda: tf.image.decode_png(image_str,
                                                    channels=channels))
        original_size = tf.shape(image)[:2]

        image = _resize_image(image, target_size)
        image = _pad_image(image, target_size)

        image_list.append(image)

    image_list.append(original_size)
    image_list.append(files)

    return image_list


def _resize_image(image, target_size, overfull=False, is_numpy=False):
    """This resizing procedure preserves the original aspect ratio and might be
       followed by padding or cropping. Depending on whether the target size is
       smaller or larger than the current image size, the area or bicubic
       interpolation method will be utilized.

    Args:
        image (tensor, uint8): A tensor with the values of an image instance.
        target_size (tuple, int): A tuple that specifies the size to which
                                  the data will be resized.
        overfull (bool, optional): Denotes whether the resulting image will be
                                   larger or equal to the specified target
                                   size. This is crucial for the following
                                   padding or cropping. Defaults to False.

    Returns:
        tensor, float32: 4D tensor that holds the values of the resized image.

    .. seealso:: The reasoning for using either area or bicubic interpolation
                 methods is based on the OpenCV documentation recommendations.
                 [https://bit.ly/2XAavw0]
    """

    if is_numpy:
        lb = np
    else:
        lb = tf

    current_size = lb.shape(image)[:2]

    height_ratio = target_size[0] / current_size[0]
    width_ratio = target_size[1] / current_size[1]

    if overfull:
        target_ratio = lb.maximum(height_ratio, width_ratio)
    else:
        target_ratio = lb.minimum(height_ratio, width_ratio)

    if is_numpy:
        target_size = np.array(current_size).astype(np.float64) * target_ratio
        target_size = np.round(target_size).astype(np.int32)
        target_size = (target_size[1], target_size[0])

        if current_size[0] > target_size[0] or current_size[1] > target_size[1]:
           interpolation = cv2.INTER_AREA
        else:
           interpolation = cv2.INTER_CUBIC
        image = cv2.resize(image, target_size, interpolation=interpolation)
        image = np.clip(image, 0, 255)
    else:
        target_size = tf.cast(current_size, tf.float64) * target_ratio
        target_size = tf.cast(tf.round(target_size), tf.int32)

        shrinking = tf.cond(tf.logical_or(current_size[0] > target_size[0],
                                          current_size[1] > target_size[1]),
                            lambda: tf.constant(True),
                            lambda: tf.constant(False))

        image = tf.expand_dims(image, 0)

        image = tf.cond(shrinking,
                        lambda: tf.image.resize_area(image, target_size,
                                                     align_corners=True),
                        lambda: tf.image.resize_bicubic(image, target_size,
                                                        align_corners=True))

        image = tf.clip_by_value(image[0], 0.0, 255.0)

    return image

def _pad_image(image, target_size):
    """A single image, either stimulus or saliency map, will be padded
       symmetrically with the constant value 126 or 0 respectively.
    Args:
        image (tensor, float32): 3D tensor with the values of the image data.
        target_size (tuple, int): A tuple that specifies the size to which
                                  the data will be resized.
    Returns:
        tensor, float32: 3D tensor that holds the values of the padded image.
    """

    current_size = tf.shape(image)

    pad_constant_value = tf.cond(tf.equal(current_size[2], 3),
                                 lambda: tf.constant(126.0),
                                 lambda: tf.constant(0.0))

    pad_vertical = (target_size[0] - current_size[0]) / 2
    pad_horizontal = (target_size[1] - current_size[1]) / 2

    pad_top = tf.floor(pad_vertical)
    pad_bottom = tf.ceil(pad_vertical)
    pad_left = tf.floor(pad_horizontal)
    pad_right = tf.ceil(pad_horizontal)

    padding = [[pad_top, pad_bottom], [pad_left, pad_right], [0, 0]]
    image = tf.pad(image, padding, constant_values=pad_constant_value)

    return image

def _np_pad_image(image, target_size):
    current_size = np.shape(image)
    pad_constant_value = 126 if current_size[2] == 3 else 0
    pad_vertical = (target_size[0] - current_size[0]) / 2
    pad_horizontal = (target_size[1] - current_size[1]) / 2

    pad_top = np.floor(pad_vertical).astype(np.int32)
    pad_bottom = np.ceil(pad_vertical).astype(np.int32)
    pad_left = np.floor(pad_horizontal).astype(np.int32)
    pad_right = np.ceil(pad_horizontal).astype(np.int32)

    padding = [[pad_top, pad_bottom], [pad_left, pad_right], [0, 0]]
    image = np.pad(
        image, padding, mode='constant', constant_values=pad_constant_value)

    return image


def _crop_image(image, target_size, is_numpy=False):
    """A single saliency map will be cropped according the specified target
       size by extracting the central region of the image and correctly
       removing the added padding.

    Args:
        image (tensor, float32): 3D tensor with the values of a saliency map.
        target_size (tensor, int32): 2D tensor that specifies the size to
                                     which the data will be cropped.

    Returns:
        tensor, float32: 3D tensor that holds the values of the saliency map
                         with cropped dimensionality.
    """

    if is_numpy:
        lb = np
    else:
        lb = tf

    current_size = lb.shape(image)[:2]

    crop_vertical = (current_size[0] - target_size[0]) / 2
    crop_horizontal = (current_size[1] - target_size[1]) / 2

    if is_numpy:
        crop_top = lb.floor(crop_vertical).astype(lb.int32)
        crop_left = lb.floor(crop_horizontal).astype(lb.int32)
    else:
        crop_top = tf.cast(lb.floor(crop_vertical), lb.int32)
        crop_left = tf.cast(lb.floor(crop_horizontal), lb.int32)

    border_bottom = crop_top + target_size[0]
    border_right = crop_left + target_size[1]

    image = image[crop_top:border_bottom, crop_left:border_right, ...]

    return image


def _get_file_list(data_path):
    """This function detects all image files within the specified parent
       directory for either training or testing. The path content cannot
       be empty, otherwise an error occurs.

    Args:
        data_path (str): Points to the directory where training or testing
                         data instances are stored.

    Returns:
        list, str: A sorted list that holds the paths to all file instances.
    """

    data_list = []

    if os.path.isfile(data_path):
        data_list.append(data_path)
    else:
        for subdir, dirs, files in os.walk(data_path):
            for file in files:
                if file.lower().endswith((".png", ".jpg", ".jpeg", ".avi")):
                    data_list.append(os.path.join(subdir, file))

    data_list.sort()

    if not data_list:
        raise FileNotFoundError("No data was found")

    return data_list


def _get_random_indices(list_length):
    """A helper function to generate an array of randomly shuffled indices
       to divide the MIT1003 and CAT2000 datasets into training and validation
       instances.

    Args:
        list_length (int): The number of indices that is randomly shuffled.

    Returns:
        array, int: A 1D array that contains the shuffled data indices.
    """

    indices = np.arange(list_length)
    prng = np.random.RandomState(42)
    prng.shuffle(indices)

    return indices


def _check_consistency(zipped_file_lists, n_total_files):
    """A consistency check that makes sure all files could successfully be
       found and stimuli names correspond to the ones of ground truth maps.

    Args:
        zipped_file_lists (tuple, str): A tuple of train and valid path names.
        n_total_files (int): The total number of files expected in the list.
    """

    assert len(list(zipped_file_lists)) == n_total_files, "Files are missing"

    for file_tuple in zipped_file_lists:
        file_names = [os.path.basename(entry) for entry in list(file_tuple)]
        file_names = [os.path.splitext(entry)[0] for entry in file_names]
        file_names = [entry.replace("_fixMap", "") for entry in file_names]
        file_names = [entry.replace("_fixPts", "") for entry in file_names]

        assert len(set(file_names)) == 1, "File name mismatch"
