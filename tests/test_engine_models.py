import pytest
from pydantic import ValidationError

from tempo.engine.models import Line, Score


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
