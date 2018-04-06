#!/bin/python3

import argparse
import fnmatch
import os
import warnings

from skimage import io, img_as_ubyte
from skimage.morphology import disk, rectangle,  binary_closing, remove_small_objects
from scipy.ndimage import binary_fill_holes, label

from tqdm import tqdm


def merge_and_save(label_file_name, expected_file_name):
    try:
        label_image = io.imread(label_file_name, as_grey=True)
        merged_image = label_image < 2.0/255.0
        merged_image = binary_fill_holes(merged_image)

        selem = disk(7)

        for i in range(20):
            components, number_of_components = label(merged_image)
            if number_of_components < 2:
                break

            merged_image = binary_closing(merged_image, selem=selem)
            merged_image = binary_fill_holes(merged_image)

            if i > 10 :
                merged_image = remove_small_objects(merged_image, min_size=10)

        try:
            expected_image = io.imread(expected_file_name, as_grey=True)
            merged_image = merged_image | (expected_image != 0)
        except IOError:
            pass

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            io.imsave(expected_file_name, img_as_ubyte(merged_image))
    except IOError:
        pass


def merge_labels(source_path, target_path):
    listdir = sorted(fnmatch.filter(os.listdir(source_path), '*_label*[!lpd].png'))
    progress = tqdm(range(len(listdir)), unit="file")

    target_dir = (source_path, target_path)[target_path != None]

    def convert(file_name):
        expected_file_name = file_name.split('_', 1)[0] + '_expected.png'
        merge_and_save(f"{source_path}/{file_name}", f"{target_dir}/{expected_file_name}")
        progress.update()

    for file_name in listdir:
        convert(file_name)

    progress.close()


def main():
    parser = argparse.ArgumentParser(description="Merge labels into expected bitmap")
    parser.add_argument("dir", help="Source directory", type=str)
    parser.add_argument("target_dir", nargs='?', help="Target directory", type=str)

    args = parser.parse_args()

    print("Merging labels into expected bitmaps...")
    merge_labels(args.dir, args.target_dir)


if __name__ == "__main__":
    main()
