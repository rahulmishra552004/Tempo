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
