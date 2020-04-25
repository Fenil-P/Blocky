"""CSC148 Assignment 2

=== CSC148 Winter 2020 ===
Department of Computer Science,
University of Toronto

This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

Authors: Diane Horton, David Liu, Mario Badr, Sophia Huynh, Misha Schwartz,
and Jaisie Sin

All of the files in this directory and all subdirectories are:
Copyright (c) Diane Horton, David Liu, Mario Badr, Sophia Huynh,
Misha Schwartz, and Jaisie Sin

=== Module Description ===

This file contains the hierarchy of Goal classes.
"""
from __future__ import annotations
import random
from typing import List, Tuple
from block import Block
from settings import colour_name, COLOUR_LIST


def generate_goals(num_goals: int) -> List[Goal]:
    """Return a randomly generated list of goals with length num_goals.

    All elements of the list must be the same type of goal, but each goal
    must have a different randomly generated colour from COLOUR_LIST. No two
    goals can have the same colour.

    Precondition:
        - num_goals <= len(COLOUR_LIST)
    """
    lst = []
    colours = COLOUR_LIST[:]
    random.shuffle(colours)
    goal_type = random.randint(0, 1)
    if goal_type == 0:
        for i in range(num_goals):
            lst.append(PerimeterGoal(colours[i]))
    else:
        for i in range(num_goals):
            lst.append(BlobGoal(colours[i]))
    return lst


def _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    """Return a two-dimensional list representing <block> as rows and columns of
    unit cells.

    Return a list of lists L, where,
    for 0 <= i, j < 2^{max_depth - self.level}
        - L[i] represents column i and
        - L[i][j] represents the unit cell at column i and row j.

    Each unit cell is represented by a tuple of 3 ints, which is the colour
    of the block at the cell location[i][j]

    L[0][0] represents the unit cell in the upper left corner of the Block.
    """
    if len(block.children) == 0:
        sl = 2 ** (block.max_depth - block.level)
        res = []
        for i in range(sl):
            res.append([block.colour] * sl)
        return res
    else:
        tr = _flatten(block.children[0])
        tl = _flatten(block.children[1])
        bl = _flatten(block.children[2])
        br = _flatten(block.children[3])
        left = []
        right = []
        for i in range(len(tr)):
            left.append(tl[i] + bl[i])
            right.append(tr[i] + br[i])
        return left + right


class Goal:
    """A player goal in the game of Blocky.

    This is an abstract class. Only child classes should be instantiated.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def __init__(self, target_colour: Tuple[int, int, int]) -> None:
        """Initialize this goal to have the given target colour.
        """
        self.colour = target_colour

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given board.

        The score is always greater than or equal to 0.
        """
        raise NotImplementedError

    def description(self) -> str:
        """Return a description of this goal.
        """
        raise NotImplementedError


class PerimeterGoal(Goal):
    """A player goal in the game of Blocky where the aim is to
     put the most possible units of a given target colour on the outer
     perimeter of the board.

    The player’s score is the total number of unit cells of the target
    colour that are on the perimeter. The corner cells count twice towards
    the score because 2 edges are touching the outer perimeter.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given <board> based on
        the number of unit cells of target colours on the outer perimeter. The
        board should not be mutated and corner cells count twice towards the
        score because 2 edges are touching the outer perimeter. The score is
        always greater than or equal to 0 because no penalties are included.
        """
        flat = _flatten(board)
        score = 0
        for i in range(len(flat)):
            if flat[i][0] == self.colour:
                score += 1
            if flat[0][i] == self.colour:
                score += 1
            if flat[i][-1] == self.colour:
                score += 1
            if flat[-1][i] == self.colour:
                score += 1
        return score

    def description(self) -> str:
        """Return a description of this goal.
        """
        return "Put the most possible units of " + colour_name(self.colour) +\
               " on the outer perimeter of the board"


class BlobGoal(Goal):
    """A player goal in the game of Blocky where the aim is to create
    the largest group of connected blocks (a blob) with the target colour.

    Two blocks are connected if their sides touch and touching corners
    does not count. The player’s score is the number of unit cells
    in the largest blob of the target colour.

    === Attributes ===
    colour:
        The target colour for this goal, that is the colour to which
        this goal applies.
    """
    colour: Tuple[int, int, int]

    def score(self, board: Block) -> int:
        """Return the current score for this goal on the given <board> based on
        the number of unit cells in the largest blob of the target colour. The
        board should not be mutated and the score is always greater than or
        equal to 0 because no penalties are included.
        """
        flat = _flatten(board)
        visited = []
        score = 0
        for _ in range(len(flat)):
            visited.append([-1] * len(flat))
        for i in range(len(flat)):
            for j in range(len(flat)):
                test = self._undiscovered_blob_size((i, j), flat, visited)
                score = max(score, test)
        return score

    def _undiscovered_blob_size(self, pos: Tuple[int, int],
                                board: List[List[Tuple[int, int, int]]],
                                visited: List[List[int]]) -> int:
        """Return the size of the largest connected blob that (a) is of this
        Goal's target colour, (b) includes the cell at <pos>, and (c) involves
        only cells that have never been visited.

        If <pos> is out of bounds for <board>, return 0.

        <board> is the flattened board on which to search for the blob.
        <visited> is a parallel structure that, in each cell, contains:
            -1 if this cell has never been visited
            0  if this cell has been visited and discovered
               not to be of the target colour
            1  if this cell has been visited and discovered
               to be of the target colour

        Update <visited> so that all cells that are visited are marked with
        either 0 or 1.
        """
        x, y = pos[0], pos[1]
        score = 0
        if 0 <= x < len(board) and 0 <= y < len(board) and visited[x][y] == -1:
            if board[x][y] == self.colour:
                visited[x][y] = 1
                score += 1
                score += self._undiscovered_blob_size((x-1, y), board, visited)
                score += self._undiscovered_blob_size((x+1, y), board, visited)
                score += self._undiscovered_blob_size((x, y-1), board, visited)
                score += self._undiscovered_blob_size((x, y+1), board, visited)
            else:
                visited[x][y] = 0
        return score

    def description(self) -> str:
        """Return a description of this goal.
        """
        return "Connect units of " + colour_name(self.colour) + \
               " to create the largest  group of connected blocks"


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'block', 'settings',
            'math', '__future__'
        ],
        'max-attributes': 15
    })
