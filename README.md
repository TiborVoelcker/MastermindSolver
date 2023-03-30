# MastermindSolver

Solver for the board game [Mastermind](<https://en.wikipedia.org/wiki/Mastermind_(board_game)>).

```IPython
>>> from game import Mastermind
>>> from solver import Knuth
>>> logging.basicConfig(level=logging.INFO, format="%(message)s")
>>> m = MasterMind(solver=Knuth)
>>> m.play()
---------------------------
1. Guess: (1, 1, 2, 2)
Response: (0, 0)
---------------------------
2. Guess: (3, 3, 4, 5)
Response: (2, 0)
---------------------------
3. Guess: (3, 6, 3, 6)
Response: (3, 0)
---------------------------
4. Guess: (1, 1, 1, 4)
Response: (0, 0)
---------------------------
5. Guess: (3, 3, 3, 6)
Response: (4, 0)

Guesses: 5, Time: 2.420125s
```

## Knuth's algorithm

It uses Donald E. Knuth's [worst-case method](<https://en.wikipedia.org/wiki/Mastermind_(board_game)#Worst_case:_Five-guess_algorithm>). The next move is chosen by analyzing the minimum possible eliminations for this guess (a.k.a. the maximum eliminations in the worst-case).

This algorithm guarantees a maximum number of 5 guesses for the default game mode using 4 possible locations and 6 possible colors. This can be analyzed with the [`stats.py`](https://github.com/TiborVoelcker/MastermindSolver/blob/1.0/stats.py) script:
![Distribution of guesses with 4 places and 6 colors using the Knuth algorithm](https://github.com/TiborVoelcker/MastermindSolver/blob/1.0/results/stats_4_6_Knuth.png)

If 10 possible colors are used, there is a maximum of 8 guesses needed:
![Distribution of guesses with 4 places and 10 colors using the Knuth algorithm](https://github.com/TiborVoelcker/MastermindSolver/blob/1.0/results/stats_4_10_Knuth.png)

> :warning: **Warning:** running the script will use a lot of resources, as multiple processes are spawned and the solver is using a lot of memoization, resulting in a high CPU and Memory usage.

## Iterative-deepening Depth-First-Search

You can imagine the game of Mastermind as a tree graph. From the starting node, there exists a child node for every possible guess (guess-branch). Each of these guesses have child nodes for each possible response to this guess (response-branch).

Knuth's algorithm basically searches this graph and giving a score to each node corresponding to the number of still possible secret codes. It then searches this graph by using the worst possible result-branch, but the best possible guess-branch. But it only goes to a depth of one.

There also exists a different solver, which uses the Iterative-deepening Depth-First-Search. This algorithm also searches the graph using the worst possible result-branch, but the best possible guess-branch. But it searches with increasing depth until a initial guess is found, which will always solve the puzzle, disregarding of which results are returned. As the depth is increased iteratively, it returns the fastest way to solve the puzzle, in the worst-case for each single response in the branch.

This means this algorithm is very conservative. On average, this solver should be worse than the `Knuth` solver, but should decrease the maximum number of guesses. But this turned out to be only true in some scenarios.
The solver is also much slower, so extensive testing is not really feasible.

## Playing yourself

The game can also be played without using a solver:

```python
logging.basicConfig(level=logging.INFO, format="%(message)s")

m = MasterMind(n_places=2, n_colors=6)
m.play()
```

The guesses then need to be input in the format `(1, 4, 1, 2)`.

If instead you are playing a game and want to use only the solver, you can use the solvers `new_guess` method to generate a new guess, and the `feedback` method, to feed back the result you get into the solver:

```IPython
>>> from game import Mastermind
>>> from solver import Knuth
>>> logging.basicConfig(level=logging.INFO, format="%(message)s")
>>> m = MasterMind(solver=Knuth)
>>> m.solver.new_guess()
(1, 1, 2, 2)
>>> m.solver.feedback((0, 1))
```
