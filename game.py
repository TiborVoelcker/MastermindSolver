"""
  Copyright (c) Tibor Völcker <tibor.voelcker@hotmail.de>
  Created on 26.03.2023
"""

import logging
import time
from abc import ABC, abstractmethod
from itertools import product
from random import choice

RESPONSE = tuple[int, int]
GUESS = tuple[int, ...]
CODE = GUESS


class MasterMind:
    """Solver for a game of Master Mind.

    Attributes:
        solver (Solver, optional): The solver to use to generate guesses.
            If omitted, the game will wait for input from the user.
        n_colors (int): The number of available colors in the game.
            Defaults to 6.
        n_places (int): The number of available slots for the code and each
            guess in the game. Defaults to 4.
    """

    def __init__(self, solver: type["Solver"] | None = None, n_colors: int = 6, n_places: int = 4):
        """Initializes the class."""
        self.n_colors = n_colors
        self.n_places = n_places
        self.solver = solver(self) if solver else None

    def combinations(self) -> list[CODE]:
        """Calculate all possible combinations.

        Returns:
            list[CODE]: All combinations with *n_colors* and *n_places*,
                with duplicates. It's length is *n_colors*^*n_places*.
        """
        return list(product(range(1, self.n_colors + 1), repeat=self.n_places))

    @staticmethod
    def response(code: CODE, guess: GUESS) -> RESPONSE:
        """Calculate the response to a specific guess.

        Args:
            code (CODE): The secret code, the answer, that was chosen.
            guess (GUESS): The guess to evaluate.

        Returns:
            RESULT: The response code. The first number indicates the number
                pins of correct color and location, the second number
                indicates the number of pins of correct color and wrong
                location.
                If a pin is counted towards the first number, it is excluded
                in the second (making the maximum sum of first and second number the
                number of available places).

        Examples:
            >>> m = MasterMind()

            >>> m.calc_response(code=(1, 1, 2, 2), guess=(1, 1, 1, 1))
            (2, 0)
            >>> m.calc_response(code=(1, 1, 2, 2), guess=(1, 2, 1, 1))
            (1, 2)
            >>> m.calc_response(code=(1, 2, 3, 4), guess=(1, 2, 3, 4))
            (4, 0)
        """
        colors, places = 0, 0
        for i, color in enumerate(code):
            if color == guess[i]:
                places += 1

        guessed_colors = list(guess)
        for color in code:
            if color in guessed_colors:
                colors += 1
                guessed_colors.remove(color)

        return places, colors - places

    def play(self) -> int:
        """Play a game of Master Mind.

        Returns:
            int: The number of guesses needed.
        """
        starting_time = time.time()
        # choose random secret code
        secret_code = choice(self.combinations())
        logging.debug("Secret Code: %s", secret_code)

        i = 0
        response = (0, 0)
        while response != (self.n_places, 0):
            if i > 100:
                raise RecursionError("The solver could not find a solution!")

            i += 1
            logging.info("---------------------------")
            if self.solver:
                guess = self.solver.new_guess()
                logging.info("%i. Guess: %s", i, guess)
            else:
                guess = self.user_input(i)
            response = self.response(secret_code, guess)
            logging.info("Response: %s", response)
            if self.solver:
                self.solver.feedback(response)
        logging.info("\nGuesses: %i, Time: %fs", i, time.time() - starting_time)
        return i

    def user_input(self, i: int) -> GUESS:
        """Ask the user for a new guess.

        The input should be comma-separated integers.

        Args:
            i (int): The current round.

        Returns:
            GUESS: The user input.
        """
        guess = input(f"{i}. Guess: ").strip("()")
        guess = tuple(int(c.strip()) for c in guess.split(","))
        if not all(0 < i < self.n_colors + 1 for i in guess):
            raise ValueError(f"Each color must be between 1 and {self.n_colors}")
        if len(guess) > self.n_places:
            raise ValueError(f"The guess must be of length {self.n_places}")

        return guess


class Solver(ABC):
    """The base class for a Mastermind solver.

    Attributes:
        game: A instance of the game it should try to solve.
    """

    def __init__(self, game: MasterMind):
        """Initializes the class."""
        self.game = game

    @abstractmethod
    def new_guess(self) -> GUESS:
        """Generate a new guess."""

    @abstractmethod
    def feedback(self, response: RESPONSE):
        """Feed the response to the last guess back to the solver."""


if __name__ == "__main__":
    from solver import Knuth

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    m = MasterMind(solver=Knuth)
    m.play()
