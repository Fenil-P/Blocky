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
Misha Schwartz, and Jaisie Sin.

=== Module Description ===

This file contains the hierarchy of player classes.
"""
from __future__ import annotations
from typing import List, Optional, Tuple
import random
import pygame

from block import Block
from goal import Goal, generate_goals

from actions import KEY_ACTION, ROTATE_CLOCKWISE, ROTATE_COUNTER_CLOCKWISE, \
    SWAP_HORIZONTAL, SWAP_VERTICAL, SMASH, PASS, PAINT, COMBINE


def create_players(num_human: int, num_random: int, smart_players: List[int]) \
        -> List[Player]:
    """Return a new list of Player objects.

    <num_human> is the number of human player, <num_random> is the number of
    random players, and <smart_players> is a list of difficulty levels for each
    SmartPlayer that is to be created.

    The list should contain <num_human> HumanPlayer objects first, then
    <num_random> RandomPlayer objects, then the same number of SmartPlayer
    objects as the length of <smart_players>. The difficulty levels in
    <smart_players> should be applied to each SmartPlayer object, in order.
    """
    lst = []
    goals = generate_goals(num_human + num_random + len(smart_players))
    for i in range(len(goals)):
        if i < num_human:
            lst.append(HumanPlayer(i, goals[i]))
        elif i < num_human + num_random:
            lst.append(RandomPlayer(i, goals[i]))
        else:
            k = i - num_human - num_random
            lst.append(SmartPlayer(i, goals[i], smart_players[k]))
    return lst


def _get_block(block: Block, location: Tuple[int, int], level: int) -> \
        Optional[Block]:
    """Return the Block within <block> that is at <level> and includes
    <location>. <location> is a coordinate-pair (x, y).

    A block includes all locations that are strictly inside of it, as well as
    locations on the top and left edges. A block does not include locations that
    are on the bottom or right edge.

    If a Block includes <location>, then so do its ancestors. <level> specifies
    which of these blocks to return. If <level> is greater than the level of
    the deepest block that includes <location>, then return that deepest block.

    If no Block can be found at <location>, return None.

    Preconditions:
        - 0 <= level <= max_depth
    """
    x = block.position[0]
    y = block.position[1]
    size = block.size
    if x <= location[0] < x + size and y <= location[1] < y + size:
        if level == block.level or block.level == block.max_depth or \
                len(block.children) == 0:
            return block
        for child in block.children:
            if _get_block(child, location, level) is not None:
                return _get_block(child, location, level)
    return None


class Player:
    """A player in the Blocky game.

    This is an abstract class. Only child classes should be instantiated.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this Player.
        """
        self.goal = goal
        self.id = player_id

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player.

        If no block is selected by the player, return None.
        """
        raise NotImplementedError

    def process_event(self, event: pygame.event.Event) -> None:
        """Update this player based on the pygame event.
        """
        raise NotImplementedError

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a potential move to make on the game board.

        The move is a tuple consisting of a string, an optional integer, and
        a block. The string indicates the move being made (i.e., rotate, swap,
        or smash). The integer indicates the direction (i.e., for rotate and
        swap). And the block indicates which block is being acted on.

        Return None if no move can be made, yet.
        """
        raise NotImplementedError


def _create_move(action: Tuple[str, Optional[int]], block: Block) -> \
        Tuple[str, Optional[int], Block]:
    """Return a move in a valid format in a tuple with the move type, direction,
    and the block the move is being performed.
    """
    return action[0], action[1], block


class HumanPlayer(Player):
    """A human player.
    """
    # === Private Attributes ===
    # _level:
    #     The level of the Block that the user selected most recently.
    # _desired_action:
    #     The most recent action that the user is attempting to do.
    #
    # == Representation Invariants concerning the private attributes ==
    #     _level >= 0
    _level: int
    _desired_action: Optional[Tuple[str, Optional[int]]]

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <renderer>, <player_id>
        and <goal>.
        """
        Player.__init__(self, player_id, goal)

        # This HumanPlayer has not yet selected a block, so set _level to 0
        # and _selected_block to None.
        self._level = 0
        self._desired_action = None

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the block that is currently selected by the player based on
        the position of the mouse on the screen and the player's desired level.

        If no block is selected by the player, return None.
        """
        mouse_pos = pygame.mouse.get_pos()
        block = _get_block(board, mouse_pos, self._level)

        return block

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the relevant keyboard events made by the player based on
        the mapping in KEY_ACTION, as well as the W and S keys for changing
        the level.
        """
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_ACTION:
                self._desired_action = KEY_ACTION[event.key]
            elif event.key == pygame.K_w:
                self._level = max(0, self._level - 1)
                self._desired_action = None
            elif event.key == pygame.K_s:
                self._level += 1
                self._desired_action = None

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return the move that the player would like to perform. The move may
        not be valid.

        Return None if the player is not currently selecting a block.
        """
        block = self.get_selected_block(board)

        if block is None or self._desired_action is None:
            return None
        else:
            move = _create_move(self._desired_action, block)

            self._desired_action = None
            return move


class RandomPlayer(Player):
    """A player who chooses a valid move randomly and plays it.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal
    # === Private Attributes ===
    # _proceed:
    #     True when the player should make a move, False when the player should
    #     wait.
    _proceed: bool

    def __init__(self, player_id: int, goal: Goal) -> None:
        """Initialize this HumanPlayer with the given <player_id> and <goal>.
        """
        Player.__init__(self, player_id, goal)
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the selected by this player. Return None since Random Player
        does not select a block. <board> is not used.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the left-click event made with mouse (which is does not
        have to be done by human player) and set _proceed to True so player can,
        make a move.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) ->\
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid, randomly generated move.

        A valid move is a move other than PASS that can be successfully
        performed on the <board>.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove

        dup = board.create_copy()
        pos = (random.randint(0, dup.size - 1), random.randint(0, dup.size - 1))
        level = random.randint(0, dup.max_depth)
        block = _get_block(dup, pos, level)
        move = None
        while move is None:
            move_type = random.randint(0, 6)
            if move_type == 0 and block.smash():
                move = SMASH
            elif move_type == 1 and block.paint(self.goal.colour):
                move = PAINT
            elif move_type == 2 and block.combine():
                move = COMBINE
            elif move_type == 3 and block.swap(0):
                move = SWAP_HORIZONTAL
            elif move_type == 4 and block.swap(1):
                move = SWAP_VERTICAL
            elif move_type == 5 and block.rotate(1):
                move = ROTATE_CLOCKWISE
            elif move_type == 6 and block.rotate(3):
                move = ROTATE_COUNTER_CLOCKWISE
            if level == dup.max_depth and move is None and\
                    not block.paint(self.goal.colour):
                dup = board.create_copy()
                pos = (random.randint(0, dup.size - 1),
                       random.randint(0, dup.size - 1))
                level = random.randint(0, dup.max_depth)
                block = _get_block(dup, pos, level)

        real_block = _get_block(board, pos, level)
        self._proceed = False  # Must set to False before returning!
        return _create_move(move, real_block)


class SmartPlayer(Player):
    """A player who  generates a set of random moves and, for each move, checks
    what its score would be if it were to make that move. Then it picks the one
    that yields the best score without taking into account any penalty that
    might apply to that action.

    The player will PASS if all of the randomized moves decrease the score.

    === Public Attributes ===
    id:
        This player's number.
    goal:
        This player's assigned goal for the game.
    """
    id: int
    goal: Goal
    # === Private Attributes ===
    # _proceed:
    #     True when the player should make a move, False when the player should
    #     wait.
    # _difficulty:
    #     The number of valid moves to randomly generate and compare each turn.
    #
    # === Representation Invariants ===
    # - _difficulty > 0
    _proceed: bool
    _difficulty: int

    def __init__(self, player_id: int, goal: Goal, difficulty: int) -> None:
        """Initialize this HumanPlayer with the given <difficulty>, <player_id>
        and <goal>. The <difficulty> refers to the number of valid moves the
        player compares and picks the one with the highest score from.
        """
        Player.__init__(self, player_id, goal)
        self._difficulty = difficulty
        self._proceed = False

    def get_selected_block(self, board: Block) -> Optional[Block]:
        """Return the selected by this player. Return None since Random Player
        does not select a block. <board> is not used.
        """
        return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Respond to the left-click event made with mouse (which is does not
        have to be done by human player) and set _proceed to True so player can,
        make a move.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._proceed = True

    def generate_move(self, board: Block) -> \
            Optional[Tuple[str, Optional[int], Block]]:
        """Return a valid move by assessing multiple valid moves and choosing
        the move that results in the highest score for this player's goal (i.e.,
        disregarding penalties).

        A valid move is a move other than PASS that can be successfully
        performed on the <board>. If no move can be found that is better than
        the current score, this player will pass.

        This function does not mutate <board>.
        """
        if not self._proceed:
            return None  # Do not remove
        score = self.goal.score(board)
        best = PASS
        real_block = board
        for _ in range(self._difficulty):
            dup = board.create_copy()
            pos = (random.randint(0, dup.size - 1),
                   random.randint(0, dup.size - 1))
            level = random.randint(0, dup.max_depth)
            block = _get_block(dup, pos, level)
            move = None
            while move is None:
                move_type = random.randint(0, 6)
                if move_type == 0 and block.smash():
                    move = SMASH
                elif move_type == 1 and block.paint(self.goal.colour):
                    move = PAINT
                elif move_type == 2 and block.combine():
                    move = COMBINE
                elif move_type == 3 and block.swap(0):
                    move = SWAP_HORIZONTAL
                elif move_type == 4 and block.swap(1):
                    move = SWAP_VERTICAL
                elif move_type == 5 and block.rotate(1):
                    move = ROTATE_CLOCKWISE
                elif move_type == 6 and block.rotate(3):
                    move = ROTATE_COUNTER_CLOCKWISE
                if level == dup.max_depth and move is None and \
                        not block.paint(self.goal.colour):
                    dup = board.create_copy()
                    pos = (random.randint(0, dup.size - 1),
                           random.randint(0, dup.size - 1))
                    level = random.randint(0, dup.max_depth)
                    block = _get_block(dup, pos, level)
            new = self.goal.score(dup)
            if new > score:
                score = new
                real_block = _get_block(board, pos, level)
                best = move

        self._proceed = False  # Must set to False before returning!
        return _create_move(best, real_block)


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-io': ['process_event'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing', 'actions', 'block',
            'goal', 'pygame', '__future__'
        ],
        'max-attributes': 10,
        'generated-members': 'pygame.*'
    })
