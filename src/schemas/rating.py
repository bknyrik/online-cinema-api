from pydantic import BaseModel, ConfigDict


class LikeMovieDetailResponseSchema(BaseModel):
    id: int
    movie_id: int


class LikeMovieListResponseSchema(BaseModel):
    likes: list[LikeMovieDetailResponseSchema]
    total_likes: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class LikeMovieDataRequestSchema(BaseModel):
    movie_id: int


class CommentMovieDetailResponseSchema(BaseModel):
    id: int
    movie_id: int
    text: str


class CommentMovieDataRequestSchema(BaseModel):
    movie_id: int
    text: str
