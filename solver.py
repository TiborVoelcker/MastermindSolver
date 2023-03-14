import time
from itertools import product
from pickle import dump, load
from random import choice

RESPONSE = tuple[int, int]
GUESS = tuple[int, ...]
CODE = GUESS
RESPONSE_SHEET = dict[RESPONSE, list[CODE]]


class MasterMind:
    """Solver for a game of Master Mind.

    Attributes:
        n_colors (int): The number of available colors in the game.
            Defaults to 6.
        n_places (int): The number of available slots for the code and each
            guess in the game. Defaults to 4.
        S (list): A list of all possible codes. This is updated with every
            response. The codes are represented as a tuple with length
            *n_places* and numbers in the range (1, *n_colors*).
    """

    def __init__(self, n_colors: int = 6, n_places: int = 4):
        """Initializes the class."""
        self.n_colors = n_colors
        self.n_places = n_places
        self.S = self.combinations()

        self.__cached_response_sheet = None

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

    def heuristic(self, guess: GUESS) -> tuple[int, RESPONSE_SHEET]:
        """The heuristic to evaluate a guess.

        This heuristic calculates the minimum possible eliminations for this
        guess. In other words, it returns amount of eliminations in the worst-case.

        Args:
            guess (GUESS): The guess to evaluate.

        Returns tuple[int, RESPONSE_SHEET]:
            int: The minimum number of eliminations for this guess.
            RESPONSE_SHEET: The corresponding response sheet for this guess.
        """
        response_sheet = self.response_sheet(guess)
        return len(self.S) - max(len(codes) for codes in response_sheet.values()), response_sheet

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
            response = self.response(code, guess)
            try:
                response_sheet[response].append(code)
            except KeyError:
                response_sheet.update({response: [code]})
        return response_sheet

    def best_guess(self) -> GUESS:
        """Calculate the best guess."""
        # Only one possible solution left.
        if len(self.S) == 1:
            self.__cached_response_sheet = None
            return self.S[0]

        best_guess = ()
        max_score = 0

        # go though all possible guesses to find guess with best score
        guesses = self.combinations()
        for guess in guesses:
            score, response_sheet = self.heuristic(guess)
            if score > max_score:
                max_score, best_guess = (score, guess)
                # cache response sheet to speed up calculations later
                self.__cached_response_sheet = response_sheet
        return best_guess

    def next_round(self, secret_code: CODE) -> tuple[GUESS, RESPONSE]:
        """Play one round.

        Args:
            secret_code (CODE): The secret code that needs to be guessed.

        Returns:
            tuple[GUESS, RESPONSE]: The new guess and its response.
        """
        if len(self.S) == self.n_colors**self.n_places:
            guess = self.round1()
        else:
            guess = self.best_guess()
        response = self.response(secret_code, guess)

        # update remaining possibilities
        # use the cached response sheet if possible to speed up calculations
        if self.__cached_response_sheet:
            self.S = self.__cached_response_sheet[response]
        else:
            self.S = self.response_sheet(guess)[response]
        return guess, response

    def play_game(self) -> int:
        """Simulate a game of Master Mind.

        Returns:
            int: The number of guesses needed.
        """
        starting_time = time.time()
        # choose random secret code
        secret_code = choice(self.combinations())
        print(f"Secret Code: {secret_code}")

        i = 0
        response = (0, 0)
        while response != (4, 0):
            i += 1
            print("---------------------------")
            guess, response = self.next_round(secret_code)
            print(f"{i}. Guess: {guess}")
            print(f"Response: {response}")
        print(f"\nGuesses: {i}, Time: {time.time()-starting_time}s")
        return i

    def round1(self) -> GUESS:
        """Play the first round.

        The response sheet and best guess for round one is read from a file to
        speed up the next game with the same settings. If no file is found,
        the result of the first round is written into a file.

        Returns:
            GUESS: The best guess for the first round.
        """
        try:
            read_file = open(f"round1_{self.n_places}_{self.n_colors}.pickle", "rb")
            guess, self.__cached_response_sheet = load(read_file)
            print("Loaded first round successfully.")
            read_file.close()
        except FileNotFoundError:
            guess = self.best_guess()
            with open(f"round1_{self.n_places}_{self.n_colors}.pickle", "wb") as write_file:
                dump((guess, self.__cached_response_sheet), write_file)
            print("Wrote first round successfully")
        return guess


if __name__ == "__main__":
    m = MasterMind()
    m.play_game()
