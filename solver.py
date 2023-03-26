"""
  Copyright (c) Tibor Völcker <tibor.voelcker@hotmail.de>
  Created on 26.03.2023
"""

import logging
from pickle import dump, load

from game import CODE, GUESS, RESPONSE, MasterMind, Solver

RESPONSE_SHEET = dict[RESPONSE, list[CODE]]


class Knuth(Solver):
    """Solver using Donald E. Knuth's worst-case method.

    Attributes:
        S (list[CODE]): A list of all possible codes. This is updated with
            every response. The codes are represented as a tuple with length
            *n_places* and numbers in the range (1, *n_colors*).
    """

    def __init__(self, game: MasterMind) -> None:
        """Initializes the class."""
        super().__init__(game)

        self.S = self.game.combinations()
        self.__cached_response_sheet: dict[RESPONSE, list[CODE]] = {}

    def new_guess(self) -> GUESS:
        if self.is_first_round():
            return self.round1()

        return self._new_guess()

    def _new_guess(self) -> GUESS:
        """Calculate the best guess."""
        # Only one possible solution left.
        if len(self.S) == 1:
            self.__cached_response_sheet = {(self.game.n_places, 0): [self.S[0]]}
            return self.S[0]

        best_guess = ()
        max_score = 0

        # go though all possible guesses to find guess with best score
        guesses = self.game.combinations()
        for guess in guesses:
            response_sheet = self.response_sheet(guess)
            score = self.heuristic(response_sheet)
            if score > max_score:
                max_score, best_guess = (score, guess)
                # cache response sheet to speed up calculations later
                self.__cached_response_sheet = response_sheet
        return best_guess

    def heuristic(self, response_sheet: RESPONSE_SHEET) -> int:
        """The heuristic to evaluate a guess.

        This heuristic calculates the minimum possible eliminations for this
        guess. In other words, it returns amount of eliminations in the worst-case.

        Args:
            response_sheet (RESPONSE_SHEET): The response sheet for the guess
                to evaluate. See *respones_sheet* for more information.

        Returns:
            int: The minimum number of eliminations for this guess.
        """
        return len(self.S) - max(len(codes) for codes in response_sheet.values())

    def response_sheet(self, guess: GUESS) -> RESPONSE_SHEET:
        """Calculate the response sheet for a guess.

        Args:
            guess (GUESS): The guess to evaluate.

        Returns:
            RESPONSE_SHEET: The response sheet. It is a dictionary with all
                possible responses to this guess and their remaining possible
                codes.

        Example:
            Response sheet for guess (1, 2, 3, 4):
            {
                (1, 0): [(1, 1, 1, 1), (1, 1, 1, 5), ...],
                ...,
                (1, 2): [(1, 3, 2, 5), ...],
                ...,
                (4, 0): [(1, 2, 3, 4)]
            }
        """
        response_sheet = {}
        # go through all remaining possibilities, calculate their response and
        # add them to the dictionary
        for code in self.S:
            response = MasterMind.response(code, guess)
            try:
                response_sheet[response].append(code)
            except KeyError:
                response_sheet.update({response: [code]})
        return response_sheet

    def feedback(self, response: RESPONSE):
        # update remaining possibilities
        # use the cached response sheet to speed up calculations
        self.S = self.__cached_response_sheet[response]
        logging.debug("Updated possible combinations: %s", self.S)

    def is_first_round(self) -> bool:
        """Check if the current round is the first round."""
        return len(self.S) == self.game.n_colors**self.game.n_places

    def round1(self) -> GUESS:
        """Play the first round.

        The response sheet and best guess for round one is read from a file to
        speed up the next game with the same settings. If no file is found,
        the result of the first round is written into a file.

        Returns:
            GUESS: The best guess for the first round.
        """
        try:
            with open(f"round1_{self.game.n_places}_{self.game.n_colors}.pickle", "rb") as f:
                guess, self.__cached_response_sheet = load(f)
                logging.debug("Loaded first round successfully.")
        except FileNotFoundError:
            guess = self._new_guess()
            with open(f"round1_{self.game.n_places}_{self.game.n_colors}.pickle", "wb") as f:
                dump((guess, self.__cached_response_sheet), f)
            logging.debug("Wrote first round successfully")
        return guess
