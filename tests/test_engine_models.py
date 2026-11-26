import pytest
from pydantic import ValidationError

from tempo.engine.models import Line, Score, flip, score_key


def test_cp_score():
    assert Score(cp=35).cp == 35


def test_both_set_rejected():
    with pytest.raises(ValidationError):
        Score(mate=2, cp=10)


def test_both_unset_rejected():
    with pytest.raises(ValidationError):
        Score()


def test_empty_moves_rejected():
    with pytest.raises(ValidationError):
        Line(moves=[], score=Score(cp=2))


def test_frozen():
    score = Score(cp=2)
    with pytest.raises(ValidationError):
        score.cp = 3


def test_json_round_trip():
    line = Line(score=Score(cp=4), moves=["e4e5", "f4f5"])
    line_json = line.model_dump_json()
    assert Line.model_validate_json(line_json) == line


def test_score_key_order():
    best_to_worst = [
        Score(mate=1),
        Score(mate=5),
        Score(cp=900),
        Score(cp=0),
        Score(cp=-900),
        Score(mate=-5),
        Score(mate=-1),
        Score(mate=0),  # already mated
    ]
    keys = [score_key(s) for s in best_to_worst]
    assert keys == sorted(keys, reverse=True)
    assert len(set(keys)) == len(keys)


@pytest.mark.parametrize(
    ("score", "flipped"),
    [
        (Score(cp=50), Score(cp=-50)),
        (Score(cp=0), Score(cp=0)),
        (Score(mate=3), Score(mate=-3)),
        (Score(mate=-2), Score(mate=2)),
    ],
)
def test_flip(score, flipped):
    assert flip(score) == flipped
