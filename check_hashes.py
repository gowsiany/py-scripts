#!/bin/python3

import argparse
import os
from multiprocessing.dummy import Pool as ThreadPool
import glob

from PIL import Image
from tqdm import tqdm

from utils.image import apply_rotation_from_original


def rename(path):#, not_labeled_path):
    progress = tqdm(range(len(os.listdir(path))), unit="file")

    def check(file_name):
        full_path = f"{path}/{file_name}"
        extension = full_path.split(".")[-1]
        file_name_without_extension = os.path.basename(file_name).split(".")[0]

        hashed_images_dir = "/Users/gowsiany/ownCloud/cloth labels/training_set/hashed_images"
        labels_dir = "/Users/gowsiany/ownCloud/cloth labels/labels"
        convexhulls_dir = "/Users/gowsiany/ownCloud/cloth labels/training_set/convex_hulls"
        heatmaps_dir = "/Users/gowsiany/ownCloud/cloth labels/training_set/heatmaps"



        hashed_image_path =  f"{hashed_images_dir}/{file_name_without_extension}.{extension.lower()}"
        not_in_hashed_images = " not_in_hashed_images" if not os.path.isfile(hashed_image_path) else ""

        not_in_labels = " not_in_labels" if not os.path.isfile(f"{hashed_images_dir}/{file_name_without_extension}.{extension.lower()}") else ""

        heatmap_path =  f"{heatmaps_dir}/{file_name_without_extension}_heatmap.png"
        not_in_heatmaps = " not_in_heatmaps" if not os.path.isfile(heatmap_path) else ""

        convexhull_path = f"{convexhulls_dir}/{file_name_without_extension}*_convexhull.png"
        not_in_convexhulls = " not_in_convexhulls" if not glob.glob(convexhull_path) else ""

        labels_path = f"{labels_dir}/{file_name_without_extension}_label*.png"
        not_in_labels = " not_in_labels" if not glob.glob(labels_path) else ""

        new_path = f"{path}/{file_name_without_extension}{not_in_hashed_images}{not_in_heatmaps}{not_in_convexhulls}{not_in_labels}.{extension}"

        if full_path != new_path:
            print(f"renaming {full_path} to {new_path}")
            os.rename(full_path, new_path)
        #
        progress.update()

    pool = ThreadPool(4)
    results = pool.map(check, os.listdir(path))
    pool.close()
    pool.join()

    progress.close()


def main():
    parser = argparse.ArgumentParser(description="Move all hash images to not labeled directory")
    parser.add_argument("dir", help="Source directory", type=str)
   # parser.add_argument("not_labeled_dir", help="Not labeled directory", type=str)

    args = parser.parse_args()
    rename(args.dir)#, args.not_labeled_dir)


if __name__ == "__main__":
    main()
