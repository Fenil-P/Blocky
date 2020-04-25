from typing import List, Optional, Tuple
import os
import pygame
import pytest
from typing import List, Optional, Tuple
import os
import pygame
import pytest
import  unittest
from block import Block
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals
from player import _get_block
from renderer import Renderer
from settings import COLOUR_LIST
# Oi Fennie Pennie, you asked for test cases, not a good or even complete set
# of test cases. And if you don't think this is a good reason for not sending you
# good or complete test cases, I said we can COLLABORATE on test cases meaning
# you have to add stuff too.

#DAAAAWWWWWG THIS SHIT HAS SOOO MANY ERRORS THAT I'M DEBUGGING THE
#SHIT THAT’S SUPPOSED TO HELP ME DEBUG!!! ~Fennie P

# Colours that we could use in the game(HAD TO PUT ITTE UP HEARE BECAUSE PYTHON
# WON'T LISTENNE)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PACIFIC_POINT = (1, 128, 181)
OLD_OLIVE = (138, 151, 71)
REAL_RED = (199, 44, 58)
MELON_MAMBO = (234, 62, 112)
DAFFODIL_DELIGHT = (255, 211, 92)
TEMPTING_TURQUOISE = (75, 196, 213)

# A pallette of the colours we use in the game
COLOUR_LIST = [PACIFIC_POINT, REAL_RED, OLD_OLIVE, DAFFODIL_DELIGHT]

from block import Block, generate_board
from blocky import _block_to_squares
from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals
from player import _get_block, create_players, Player, \
    SmartPlayer, RandomPlayer, HumanPlayer
from renderer import Renderer
from settings import COLOUR_LIST
import random


def standard_borde() -> Block:
    borde = Block((0, 0), 400, None, 0, 3)
    blocke1 = Block((200, 0), 200, None, 1, 3)
    # childrenne of blocke 1
    blocke1_1 = Block((300, 0), 100, PACIFIC_POINT, 2, 3)
    blocke1_2 = Block((200, 0), 100, REAL_RED, 2, 3)
    blocke1_3 = Block((200, 100), 100, OLD_OLIVE, 2, 3)
    blocke1_4 = Block((300, 100), 100, DAFFODIL_DELIGHT, 2, 3)
    blocke1.children = [blocke1_1, blocke1_2, blocke1_3, blocke1_4]
    blocke2 = Block((0, 0), 200, DAFFODIL_DELIGHT, 1, 3)
    blocke3 = Block((0, 200), 200, None, 1, 3)
    # childrenne of blocke 3
    blocke2_1 = Block((100, 200), 100, PACIFIC_POINT, 2, 3)
    blocke2_2 = Block((0, 200), 100, REAL_RED, 2, 3)
    blocke2_3 = Block((0, 300), 100, OLD_OLIVE, 2, 3)
    blocke2_4 = Block((100, 300), 100, PACIFIC_POINT, 2, 3)
    blocke3.children = [blocke2_1, blocke2_2, blocke2_3, blocke2_4]
    blocke4 = Block((200, 200), 100, PACIFIC_POINT, 1, 3)
    borde.children = [blocke1, blocke2, blocke3, blocke4]
    return borde
    # this is description figure 1 for easy reference


class TestBlock:
    # Block._update_children_positions(self, position: Tuple[int, int]) -> None:
    def test_update_children_positions(self) -> None:
        borde = standard_borde()
        borde.children[0]._update_children_positions((0, 0))
        assert borde.children[0].children[0].position == (100, 0)
        assert borde.children[0].children[1].position == (0, 0)
        assert borde.children[0].children[2].position == (0, 100)
        assert borde.children[0].children[3].position == (100, 100)

    # Block.smash(self) -> bool:
    def test_smash_cant_smash(self) -> None:
        borde = standard_borde()
        assert borde.children[0].children[0].smash() is True
        assert borde.children[0].children[0].children[0].smash() is False # max depth reached

    # Block.swap(self, direction: int) -> bool:
    def test_swap_horizontal(self) -> None:
        borde = standard_borde()
        assert borde.children[1].swap(0) is False
        assert borde.children[0].swap(0) is True
        expected = [REAL_RED, PACIFIC_POINT, DAFFODIL_DELIGHT, OLD_OLIVE]
        for i in range(len(borde.children[0].children)):
            assert borde.children[0].children[i].colour == expected[i]

    # Block.rotate(self, direction: int) -> bool:
    def rotate_cw(self) -> None:
        borde = standard_borde()
        assert borde.children[1].rotate(1) is False
        assert borde.children[0].rotate(1) is True
        expected = [REAL_RED, OLD_OLIVE, DAFFODIL_DELIGHT, PACIFIC_POINT]
        for i in range(len(borde.children[0])):
            assert borde.children[0][i].colour == expected[i]

    # Block.paint(self, colour: Tuple[int, int, int]) -> bool:
    def test_paint(self) -> None:
        boarde = standard_borde()
        assert boarde.paint(PACIFIC_POINT) is False
        assert boarde.children[0].children[0].paint(OLD_OLIVE) is False
        boarde.children[0].children[0].smash()
        assert boarde.children[0].children[0].children[0]. \
                   paint((0, 0, 0)) is True  # not legal colour, so
        # will be true

    # Block.combine(self) -> bool
    def combine(self) -> None:
        borde = standard_borde()
        assert borde.children[0].combine() is False
        assert borde.children[2].combine() is True
        assert borde.children[2].colour == PACIFIC_POINT
        assert borde.children[2].size == 200
        assert borde.children[2].position == (0, 200)


class TestBlocky:
    # _block_to_squares(board: Block) -> List[Tuple[Tuple[int, int, int],Tuple[int, int], int]]:
    def test_blocks_to_squares(self) -> None:
        borde = standard_borde()
        # print(borde)
        expected = ((PACIFIC_POINT, (300, 0), 100), (REAL_RED, (200, 0), 100),
                    (OLD_OLIVE, (200, 100), 100),
                    (DAFFODIL_DELIGHT, (300, 100), 100),
                    (DAFFODIL_DELIGHT, (0, 0), 200), (REAL_RED, (0, 200), 100),
                    (PACIFIC_POINT, (100, 200), 100),
                    (OLD_OLIVE, (0, 300), 100),
                    (PACIFIC_POINT, (100, 300), 100),
                    (PACIFIC_POINT, (200, 200), 100))
        for item in _block_to_squares(borde):
            assert item in expected


class TestPlayer:
    # create_players(num_human: int, num_random: int, smart_players: List[int])-> List[Player]:
    def test_create_players_(self) -> None:
        h = random.randint(0, 2)
        r = random.randint(0, 2)
        diffs = []
        for i in range(random.randint(0, 2)):
            diffs.append(random.randint(1, 50))
        players = create_players(h, r, diffs)
        assert len(players) == h + r + len(diffs)
        c = 0
        for i in players[h + r:]:
            assert i._difficulty == diffs[c]
            c += 1

    # _get_block(block: Block, location: Tuple[int, int], level: int) -> Optional[Block]:
    def test_get_block_level_0(self) -> None:
        borde = standard_borde()
        assert _get_block(borde, (0, 0), 0) == borde

    def test_get_block_max_level(self) -> None:
        borde = standard_borde()
        # print(_get_block(borde, (50, 50), 3))
        assert _get_block(borde, (50, 50), 3) is None

    # RandomPlayer.generate_move(self, board: Block) -> Optional[Tuple[str, Optional[int], Block]]:

    # SmartPlayer.generate_move(self, board: Block) -> Optional[Tuple[str, Optional[int], Block]]:
    def test_SPGM_good_idea(self) -> None:
        borde = standard_borde()
        bobbito = SmartPlayer(1, BlobGoal(DAFFODIL_DELIGHT))
        bobbito._proceed = True
        assert bobbito.generate_move(borde) == 1 \
               or bobbito.generate_move(borde) == 2
        # 1 is command for horizontally swap borde.children[0]
        # 2 is command for cw rotate borde.children[0]


class TestGoal:
    # generate_goals(num_goals: int) -> List[Goal]:
    def test_generate_goals(self) -> None:
        n = random.randint(1, 100)
        assert len(generate_goals(4)) == 4

    # _flatten(block: Block) -> List[List[Tuple[int, int, int]]]:
    # [PACIFIC_POINT, REAL_RED, OLD_OLIVE, DAFFODIL_DELIGHT]
    def test_flatten_(self) -> None:
        assert _flatten(standard_borde()) == [
            [DAFFODIL_DELIGHT, DAFFODIL_DELIGHT, DAFFODIL_DELIGHT,
             DAFFODIL_DELIGHT, REAL_RED, REAL_RED, OLD_OLIVE, OLD_OLIVE],
            [DAFFODIL_DELIGHT, DAFFODIL_DELIGHT, DAFFODIL_DELIGHT,
             DAFFODIL_DELIGHT, REAL_RED, REAL_RED, OLD_OLIVE, OLD_OLIVE],
            [DAFFODIL_DELIGHT, DAFFODIL_DELIGHT, DAFFODIL_DELIGHT,
             DAFFODIL_DELIGHT
                , PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT],
            [DAFFODIL_DELIGHT, DAFFODIL_DELIGHT, DAFFODIL_DELIGHT,
             DAFFODIL_DELIGHT
                , PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT],
            [REAL_RED, REAL_RED, OLD_OLIVE, OLD_OLIVE, PACIFIC_POINT,
             PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT],
            [REAL_RED, REAL_RED, OLD_OLIVE, OLD_OLIVE, PACIFIC_POINT,
             PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT],
            [PACIFIC_POINT, PACIFIC_POINT, DAFFODIL_DELIGHT, DAFFODIL_DELIGHT,
             PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT],
            [PACIFIC_POINT, PACIFIC_POINT, DAFFODIL_DELIGHT, DAFFODIL_DELIGHT,
             PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT, PACIFIC_POINT]
        ]

    # PerimeterGoal.score(self, board: Block) -> int:
    def test_PG_no_perimeter(self) -> None:
        gol = PerimeterGoal(DAFFODIL_DELIGHT)
        borde = standard_borde()
        borde.children[1] = Block((0, 0), 200, OLD_OLIVE, 1, 3)
        borde.children[0].children[3] = \
            Block((300, 100), 100, OLD_OLIVE, 2, 3)
        assert gol.score(borde) == 0

    def test_PG_no_corner(self) -> None:
        gol = PerimeterGoal(REAL_RED)
        borde = standard_borde()
        assert gol.score(borde) == 4

    def test_PG_with_corner(self) -> None:
        gol = PerimeterGoal(DAFFODIL_DELIGHT)
        borde = standard_borde()
        assert gol.score(borde) == 10
        # unit block is half size of smallest block in this case

    # BlobGoal.score(self, board: Block) -> int:
    def test_BG_2_blobs(self) -> None:
        gol = BlobGoal(PACIFIC_POINT)
        borde = standard_borde()
        assert gol.score(borde) == 24

    # BlobGoal.score(self, board: Block) -> int:
    def test_BG_many_blob_not_connected(self) -> None:
        gol = BlobGoal(PACIFIC_POINT)
        borde = standard_borde()
        # print(borde)
        borde.children[2].children[0] = Block((100, 200), 100, OLD_OLIVE, 2, 3)
        # print(borde)
        assert gol.score(borde) == 20
        assert borde.children[2].children[0].smash() is True

    # BlobGoal._undiscovered_blob_size(self, pos: Tuple[int, int],
    # board: List[List[Tuple[int, int, int]]],
    # visited: List[List[int]]) -> int:
    pass


if __name__ == '__main__':
    pytest.main(['test.py'])
# from typing import List, Optional, Tuple
# import os
# import pygame
# import pytest
# import  unittest
# from block import Block
# from blocky import _block_to_squares
# from goal import BlobGoal, PerimeterGoal, _flatten, generate_goals
# from player import _get_block
# from renderer import Renderer
# from settings import COLOUR_LIST
#
# """
# PACIFIC_POINT = (1, 128, 181)
# REAL_RED = (199, 44, 58)
# OLD_OLIVE = (138, 151, 71)
# DAFFODIL_DELIGHT = (255, 211, 92)
#
# A palette of the colours we use in the game
# COLOUR_LIST = [PACIFIC_POINT, REAL_RED, OLD_OLIVE, DAFFODIL_DELIGHT]
# """
#
#
# def set_children(block: Block, colours: List[Optional[Tuple[int, int, int]]]) \
#         -> None:
#     """Set the children at <level> for <block> using the given <colours>.
#
#     Precondition:
#         - len(colours) == 4
#         - block.level + 1 <= block.max_depth
#     """
#     size = block._child_size()
#     positions = block._children_positions()
#     level = block.level + 1
#     depth = block.max_depth
#
#     block.children = []  # Potentially discard children
#     for i in range(4):
#         b = Block(positions[i], size, colours[i], level, depth)
#         block.children.append(b)
#
#
# @pytest.fixture
# def renderer() -> Renderer:
#     os.environ['SDL_VIDEODRIVER'] = 'dummy'
#     pygame.init()
#     return Renderer(750)
#
#
# @pytest.fixture
# def child_block() -> Block:
#     """Create a reference child block with a size of 750 and a max_depth of 0.
#     """
#     return Block((0, 0), 750, COLOUR_LIST[0], 0, 0)
#
#
# @pytest.fixture
# def board_16x16() -> Block:
#     """Create a reference board with a size of 750 and a max_depth of 2.
#     """
#     # Level 0
#     board = Block((0, 0), 750, None, 0, 2)
#
#     # Level 1
#     colours = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3]]
#     set_children(board.children[0], colours)
#
#     return board
#
#
# @pytest.fixture
# def board_16x16_swap0() -> Block:
#     """Create a reference board that is swapped along the horizontal plane.
#     """
#     # Level 0
#     board = Block((0, 0), 750, None, 0, 2)
#
#     # Level 1
#     colours = [COLOUR_LIST[2], None, COLOUR_LIST[3], COLOUR_LIST[1]]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3]]
#     set_children(board.children[1], colours)
#
#     return board
#
#
# @pytest.fixture
# def board_16x16_swap1() -> Block:
#     """Create a reference board that is swapped along the horizontal plane.
#     """
#     # Level 0
#     board = Block((0, 0), 750, None, 0, 2)
#
#     # Level 1
#     colours = [COLOUR_LIST[3], COLOUR_LIST[1], COLOUR_LIST[2], None]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3]]
#     set_children(board.children[3], colours)
#
#     return board
#
#
# @pytest.fixture
# def board_16x16_rotate1() -> Block:
#     """Create a reference board where the top-right block on level 1 has been
#     rotated clockwise.
#     """
#     # Level 0
#     board = Block((0, 0), 750, None, 0, 2)
#
#     # Level 1
#     colours = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[0]]
#     set_children(board.children[0], colours)
#
#     return board
#
#
# @pytest.fixture
# def board_16x16_rotate3() -> Block:
#     """Create a reference board where the top-right block on level 1 has been
#     rotated clockwise.
#     """
#     # Level 0
#     board = Block((0, 0), 750, None, 0, 2)
#
#     # Level 1
#     colours = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[3], COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[1]]
#     set_children(board.children[0], colours)
#
#     return board
#
#
# @pytest.fixture
# def flattened_board_16x16() -> List[List[Tuple[int, int, int]]]:
#     """Create a list of the unit cells inside the reference board."""
#     return [
#         [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]],
#         [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]],
#         [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3]],
#         [COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]]
#     ]
#
#
# @pytest.fixture
# def flattened_board_16x16_swap0() -> List[List[Tuple[int, int, int]]]:
#     """Create a list of the unit cells inside the reference board."""
#     return [
#         [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3]],
#         [COLOUR_LIST[0], COLOUR_LIST[3], COLOUR_LIST[3], COLOUR_LIST[3]],
#         [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]],
#         [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]],
#     ]
#
#
# @pytest.fixture
# def flattened_board_16x16_rotate3() -> List[List[Tuple[int, int, int]]]:
#     """Create a list of the unit cells inside the reference board."""
#     return [
#         [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]],
#         [COLOUR_LIST[2], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[1]],
#         [COLOUR_LIST[0], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3]],
#         [COLOUR_LIST[3], COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[3]]
#     ]
#
#
# class TestBlock:
#     def test_smash(self) -> None:
#         bk = Block((0, 0), 750, None, 0, 0)
#         assert not bk.smash()
#         bk2 = Block((0, 0), 750, None, 0, 1)
#         assert bk2.smash()
#         assert len(bk2.children) == 4
#
#     def test_swap_vertical(self, board_16x16, board_16x16_swap0) -> None:
#         board_16x16.swap(0)
#         assert board_16x16 == board_16x16_swap0
#
#     def test_swap_horizontal(self, board_16x16, board_16x16_swap1) -> None:
#         board_16x16.swap(1)
#         assert board_16x16 == board_16x16_swap1
#
#     def test_swap_no_children(self, child_block) -> None:
#         assert not child_block.swap(1)
#
#     def test_rotate_clockwise(self, board_16x16, board_16x16_rotate1) -> None:
#         board_16x16.children[0].rotate(1)
#         assert board_16x16 == board_16x16_rotate1
#
#     def test_rotate_counter(self, board_16x16, board_16x16_rotate3) -> None:
#         board_16x16.children[0].rotate(3)
#         assert board_16x16 == board_16x16_rotate3
#
#     def test_rotate_no_children(self, child_block) -> None:
#         assert not child_block.rotate(0)
#         assert not child_block.rotate(3)
#
#     def test_paint_not_max_depth(self, board_16x16) -> None:
#         assert not board_16x16.children[0].paint(COLOUR_LIST[0])
#         assert not board_16x16.children[1].paint(COLOUR_LIST[2])
#         assert not board_16x16.children[3].paint(COLOUR_LIST[3])
#
#     def test_paint_max_depth(self, board_16x16) -> None:
#         # same colour
#         assert not board_16x16.children[0].children[0].paint(COLOUR_LIST[0])
#         # not the same colour
#         assert board_16x16.children[0].children[0].paint(COLOUR_LIST[1])
#
#     def test_combine(self, board_16x16) -> None:
#         # no children
#         assert not board_16x16.children[1].combine()
#         assert not board_16x16.children[0].children[0].combine()
#         # not at max depth
#         assert not board_16x16.combine()
#         # works
#         assert board_16x16.children[0].combine()
#         assert board_16x16.children[0].colour == COLOUR_LIST[1]
#
#     def test_combine_no_majority(self) -> None:
#         board = Block((0, 0), 750, None, 0, 1)
#         colours = [COLOUR_LIST[0], COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
#         set_children(board, colours)
#         assert not board.combine()
#
#     def test_create_copy(self, board_16x16) -> None:
#         new = board_16x16.create_copy()
#         assert id(new) != id(board_16x16)
#         assert id(new.children[0]) != id(board_16x16.children[0])
#         assert id(new.children[0].children[1]) != id(board_16x16.children[0]
#                                                      .children[1])
#
# # Blocky tests
#     """
#     PACIFIC_POINT = (1, 128, 181)
#     REAL_RED = (199, 44, 58)
#     OLD_OLIVE = (138, 151, 71)
#     DAFFODIL_DELIGHT = (255, 211, 92)
#     """
#
#
# def test_block_to_squares(board_16x16) -> None:
#     squares = set(_block_to_squares(board_16x16))
#     expected = {((1, 128, 181), (563, 0), 188),  # 0
#             ((199, 44, 58), (375, 0), 188),  # 1
#             ((199, 44, 58), (375, 188), 188),  # 1
#             ((255, 211, 92), (563, 188), 188),  # 3
#             ((138, 151, 71), (0, 0), 375),  # 2
#             ((199, 44, 58), (0, 375), 375),  # 1
#             ((255, 211, 92), (375, 375), 375)  # 3
#             }
#
#     self.assertSetEqual(squares,expected)
#
#     board_16x16.swap(0)
#     squares = set(_block_to_squares(board_16x16))
#     expected = {((1, 128, 181), (188, 0), 188),  # 0
#                 ((199, 44, 58), (0, 0), 188),  # 1
#                 ((199, 44, 58), (0, 188), 188),  # 1
#                 ((255, 211, 92), (188, 188), 188),  # 3
#                 ((138, 151, 71), (375, 0), 375),  # 2
#                 ((199, 44, 58), (0, 375), 375),  # 1
#                 ((255, 211, 92), (375, 375), 375)  # 3
#                 }
#     assert squares == expected
#
#
# # Goal Tests
#
# def test_generate_goals() -> None:
#     goals = generate_goals(4)
#     assert len(goals) == 4
#     t = type(goals[0])
#     for goal in goals:
#         assert type(goal) == t
#         assert goal.colour in COLOUR_LIST
#
#
# def test__flatten(flattened_board_16x16, board_16x16,
#                   flattened_board_16x16_swap0, flattened_board_16x16_rotate3,
#                   board_16x16_rotate3) -> None:
#     expected = flattened_board_16x16
#     assert _flatten(board_16x16) == expected
#     expected = flattened_board_16x16_swap0
#     board_16x16.swap(0)
#     assert _flatten(board_16x16) == expected
#     expected = flattened_board_16x16_rotate3
#     assert _flatten(board_16x16_rotate3) == expected
#
#
# def test__flatten_child() -> None:
#     board = Block((0, 0), 750, COLOUR_LIST[0], 0, 0)
#     expected = [[COLOUR_LIST[0]]]
#     assert _flatten(board) == expected
#
#
# # def test_perimeter_goal_score(board_16x16, board_16x16_rotate3) -> None:
#     # g = PerimeterGoal(COLOUR_LIST[1])
#     # assert g.score(board_16x16) == 3
#     # assert g.score(board_16x16_swap0) == 5
#     # g2 = PerimeterGoal(COLOUR_LIST[0])
#     # assert g2.score(board_16x16_rotate3) == 1
#
#
# def test_perimeter_goal_score_fail() -> None:
#     board = Block((0, 0), 750, None, 0, 2)
#     # Level 1
#     colours = [None, COLOUR_LIST[2], COLOUR_LIST[1], COLOUR_LIST[3]]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[0],
#                COLOUR_LIST[3]]
#     set_children(board.children[0], colours)
#     g3 = PerimeterGoal(COLOUR_LIST[3])
#     print(board)
#     assert g3.score(board) == 5
#     board.children[0].rotate(1)
#     assert g3.score(board) == 4
#
#
# def test_perimeter_goal_score_depth_3() -> None:
#     board = Block((0, 0), 750, None, 0, 3)
#     # Level 1
#     colours = [None, COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[1]]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[1],
#                None]
#     set_children(board.children[0], colours)
#
#     # Level 3
#     colours = [COLOUR_LIST[2], COLOUR_LIST[3], COLOUR_LIST[0],
#                COLOUR_LIST[2]]
#     set_children(board.children[0].children[3], colours)
#
#     correct_scores = [
#         (COLOUR_LIST[0], 2),
#         (COLOUR_LIST[1], 20),
#         (COLOUR_LIST[2], 2),
#         (COLOUR_LIST[3], 8)
#     ]
#
#     # Set up a goal for each colour and check the results
#     for colour, expected in correct_scores:
#         goal = PerimeterGoal(colour)
#         assert goal.score(board) == expected
#
#
# def test_blob_goal_score_all() -> None:
#     board = Block((0, 0), 750, None, 0, 2)
#     # Level 1
#     colours = [None, COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1]]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[1], COLOUR_LIST[1], COLOUR_LIST[1],
#                COLOUR_LIST[1]]
#     set_children(board.children[0], colours)
#     blob_goal = BlobGoal(COLOUR_LIST[1])
#     assert blob_goal.score(board) == 16
#     blob_goal2 = BlobGoal(COLOUR_LIST[2])
#     assert blob_goal2.score(board) == 0
#
#
# def test_blob_goal_score_depth_3() -> None:
#     board = Block((0, 0), 750, None, 0, 3)
#     # Level 1
#     colours = [None, COLOUR_LIST[1], COLOUR_LIST[3], COLOUR_LIST[1]]
#     set_children(board, colours)
#
#     # Level 2
#     colours = [COLOUR_LIST[1], COLOUR_LIST[0], COLOUR_LIST[1],
#                None]
#     set_children(board.children[0], colours)
#
#     # Level 3
#     colours = [COLOUR_LIST[2], COLOUR_LIST[3], COLOUR_LIST[0],
#                COLOUR_LIST[2]]
#     set_children(board.children[0].children[3], colours)
#
#     correct_scores = [
#         (COLOUR_LIST[0], 4),
#         (COLOUR_LIST[1], 36),
#         (COLOUR_LIST[2], 2),
#         (COLOUR_LIST[3], 16)
#     ]
#
#     # Set up a goal for each colour and check the results
#     for colour, expected in correct_scores:
#         goal = BlobGoal(colour)
#         assert goal.score(board) == expected
#
# # Player tests
#
#
# if __name__ == '__main__':
#     pytest.main(['test.py'])
