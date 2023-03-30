"""
  Copyright (c) Tibor Völcker <tibor.voelcker@hotmail.de>
  Created on 28.03.2023
"""
import multiprocessing
from collections import Counter
from pickle import dump, load

import tqdm
from matplotlib import pyplot as plt

from solver import Knuth, MasterMind

filename_template = "results/stats_%i_%i_%s"


def plot(result: list[int], info: tuple[int, int, str]):
    """Plot the results in a bar graph."""
    ctr = Counter(result)
    data = sorted((str(i), n) for i, n in ctr.items())
    bars = plt.bar(*zip(*data))

    plt.bar_label(bars)
    plt.xlabel("Number of tries")

    plt.title(f"Mastermind with {info[2]} solver ({info[0]} places, {info[1]} colors)")

    plt.show()
    plt.savefig(filename_template % info + ".png")


def load_data(info: tuple[int, int, str]):
    """Load and plot a result."""
    with open(filename_template % info + ".pickle", "rb") as f:
        result = load(f)

    plot(result, info)


def main():
    """Run a game with every possible secret code and plot the results."""
    m = MasterMind(solver=Knuth, n_colors=10)

    codes = m.combinations()

    with multiprocessing.Pool(processes=12) as pool:
        result = list(
            tqdm.tqdm(
                pool.imap_unordered(m.play, codes, chunksize=100),
                total=m.n_colors**m.n_places,
            )
        )

    info = (m.n_places, m.n_colors, m.solver.__class__.__name__)
    with open(filename_template % info + ".pickle", "wb") as f:
        dump(result, f)

    plot(result, info)


if __name__ == "__main__":
    main()
