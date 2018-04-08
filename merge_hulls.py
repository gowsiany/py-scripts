#!/bin/python3

import argparse
import fnmatch
import os
import warnings
import glob


from skimage import io, img_as_ubyte
from tqdm import tqdm
from multiprocessing.dummy import Pool as ThreadPool



def merge_hulls(source_path, target_path):
    files = fnmatch.filter(os.listdir(source_path),'*hull.png')

    hashes = sorted(list(set(filter(lambda f: len(f) > 0, map(lambda f: os.path.basename(f).split(".")[0].split("_")[0], files)))))
    progress = tqdm(range(len(hashes)), unit="file")
    
    target_dir = (source_path, target_path)[target_path != None]

    def merge_hulls_with_hash(hash):
        heatmap_initialized = False

        mask = f"{source_path}/{hash}*hull*.png"
        files = glob.glob(mask)

        for f in files:
            try:
                hull_image = (io.imread(f, as_grey=True) != 0)
                if not heatmap_initialized:
                    heatmap = hull_image
                    heatmap_initialized = True
                else:
                    heatmap = heatmap | hull_image

            except IOError:
                pass

        if heatmap_initialized:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                heatmap_file_name =  f"{target_dir}/{hash}_heatmap.png"
                io.imsave(heatmap_file_name, img_as_ubyte(heatmap))

        progress.update()

    pool = ThreadPool(4)
    results = pool.map(merge_hulls_with_hash, hashes)
    pool.close()
    pool.join()

    progress.close()

def main():
    parser = argparse.ArgumentParser(description="Merge hull images into heatmaps")
    parser.add_argument("dir", help="Source directory", type=str)
    parser.add_argument("target_dir", nargs='?', help="Target directory", type=str)

    args = parser.parse_args()

    print("Merging hulls into heatmaps...")
    merge_hulls(args.dir, args.target_dir)

if __name__ == "__main__":
    main()
