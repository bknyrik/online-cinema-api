from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LikeMovieDetailResponseSchema(BaseModel):
    id: int
    created_at: datetime
    movie_id: int
    profile_id: int


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
    profile_id: int


class CommentMovieListResponseSchema(BaseModel):
    comments: list[CommentMovieDetailResponseSchema]
    total_comments: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class CommentMovieDataRequestSchema(BaseModel):
    movie_id: int
    text: str


class CommentMovieUpdateRequestSchema(BaseModel):
    text: str = Field(strict=True, min_length=1)
