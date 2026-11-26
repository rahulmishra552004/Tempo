from pydantic import BaseModel, ConfigDict, Field, model_validator


class Score(BaseModel):
    model_config = ConfigDict(frozen=True)

    mate: int | None = None
    cp: int | None = None

    @model_validator(mode="after")
    def _exactly_one(self) -> "Score":
        if (self.mate is None) == (self.cp is None):
            raise ValueError("set exactly one of cp or mate")
        return self


class Line(BaseModel):
    model_config = ConfigDict(frozen=True)

    score: Score
    moves: list[str] = Field(min_length=1)


def score_key(score: Score) -> int:
    if score.cp is not None:
        return score.cp
    if score.mate > 0:
        return 100000 - score.mate
    else:
        return -100000 - score.mate


def flip(score: Score) -> Score:
    if score.mate is None:
        return Score(cp=-score.cp)
    else:
        return Score(mate=-score.mate)
