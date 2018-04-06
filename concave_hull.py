#!/bin/python3

import argparse
import os
import fnmatch
import warnings
from multiprocessing.dummy import Pool as ThreadPool

from skimage import io, img_as_ubyte
from skimage.morphology import disk, rectangle,  binary_closing, remove_small_objects
from scipy.ndimage import binary_fill_holes, label
from tqdm import tqdm

def convert_and_save(file_name, new_file_name):
    try:
        original = io.imread(file_name, as_grey=True)
        concave_hull = original < 2.0/255.0

        selem = disk(7)

        for i in range(20):

            if i > 2:
                components, number_of_components = label(concave_hull)
                if number_of_components < 2:
                    break

            concave_hull = binary_closing(concave_hull, selem=selem)
            concave_hull = binary_fill_holes(concave_hull)

            if i > 10:
                concave_hull = remove_small_objects(concave_hull, min_size=10)

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            io.imsave(new_file_name, img_as_ubyte(concave_hull))
    except IOError:
        pass


def generate_concave_hull(source_dir, target_dir):
    listdir = sorted(fnmatch.filter(os.listdir(source_dir), '*_label*[!lp].png'))
    progress = tqdm(range(len(listdir)), unit="file")

    target_dir = (source_dir, target_dir)[target_dir != None]

    def convert(file_name):
        new_file_name = file_name.replace('.png', '_concavehull.png')
        convert_and_save(f"{source_dir}/{file_name}", f"{target_dir}/{new_file_name}")
        progress.update()

    pool = ThreadPool(4)
    results = pool.map(convert, listdir)
    pool.close()
    pool.join()

    progress.close()


def main():
    parser = argparse.ArgumentParser(description="Converts all images to concave hull images")
    parser.add_argument("dir", help="Source directory", type=str)
    parser.add_argument("target_dir", nargs='?', help="Target directory", type=str)
    args = parser.parse_args()

    print("Converting to concave hull...")
    generate_concave_hull(args.dir, args.target_dir)


if __name__ == "__main__":
    main()
