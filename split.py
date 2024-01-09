import argparse
import json
import os
import random
import time

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--datasets", nargs="+", required=True)
    args = parser.parse_args()

    split2data = dict(test=[], dev=[], train=[])
    for ds in args.datasets:
        with open(ds, "r") as f:
            dataset = json.load(f)
        dataset = np.array(dataset)

        idxes = np.arange(len(dataset))
        test_size = len(idxes) // 10
        dev_size = len(idxes) // 10

        split2idxes = dict(
            test=idxes[:test_size],
            dev=idxes[test_size : test_size + dev_size],
            train=idxes[test_size + dev_size :],
        )

        np.random.shuffle(dataset)
        for split, ids in split2idxes.items():
            split2data[split].extend(dataset[ids])

    os.makedirs(args.output_dir, exist_ok=True)
    time_label = time.strftime("%Y-%m-%d_%H.%M.%S")
    for split, data in split2data.items():
        random.shuffle(data)
        filename = f"{time_label}_{split}.json"
        filepath = os.path.join(args.output_dir, filename)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()
