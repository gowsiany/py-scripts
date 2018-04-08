#!/bin/python3

import argparse
import os
from multiprocessing.dummy import Pool as ThreadPool
import glob
import shutil


from PIL import Image
from tqdm import tqdm

from utils.image import apply_rotation_from_original


def fetch(path):

    files = os.listdir(path)

    hashes = sorted(list(set( filter(lambda f: len(f) > 0, map(lambda f: os.path.basename(f).split(".")[0].split("_")[0], files)))))
    progress = tqdm(range(len(hashes)), unit="file")

    def copy_all_matching(hash, from_dir):
        mask = f"{from_dir}/{hash}*.*"
        files = glob.glob(mask)

        for f in files:
            shutil.copy(f, path)


    def copy_all(hash):
        dirs = [ "/Users/gowsiany/ownCloud/cloth labels/training_set/hashed_images",
                "/Users/gowsiany/ownCloud/cloth labels/labels",
                "/Users/gowsiany/ownCloud/cloth labels/training_set/convex_hulls",
                 "/Users/gowsiany/ownCloud/cloth labels/training_set/concave_hulls",
                 "/Users/gowsiany/ownCloud/cloth labels/training_set/heatmaps"
        ]

        for dir in dirs:
            copy_all_matching(hash, dir)

        progress.update()

    pool = ThreadPool(4)
    results = pool.map(copy_all, hashes)
    pool.close()
    pool.join()

    progress.close()


def main():
    parser = argparse.ArgumentParser(description="Move all data related to hashes found in directory")
    parser.add_argument("dir", help="Source directory", type=str)

    args = parser.parse_args()
    fetch(args.dir)


if __name__ == "__main__":
    main()
