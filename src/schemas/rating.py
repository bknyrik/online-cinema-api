from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MovieLikeDetailResponseSchema(BaseModel):
    id: int
    created_at: datetime
    movie_id: int
    profile_id: int


class MovieLikeListResponseSchema(BaseModel):
    likes: list[MovieLikeDetailResponseSchema]
    total_likes: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class MovieLikeDataRequestSchema(BaseModel):
    movie_id: int

    model_config = ConfigDict(strict=True)


class CommentMovieDetailResponseSchema(BaseModel):
    id: int
    created_at: datetime
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


class CommentReplyDetailResponseSchema(BaseModel):
    id: int
    created_at: datetime
    comment_id: int
    profile_id: int
    text: str


class CommentReplyListResponseSchema(BaseModel):
    replies: list[CommentReplyDetailResponseSchema]
    total_replies: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class CommentReplyCreateRequestSchema(BaseModel):
    comment_id: int
    text: str

    model_config = ConfigDict(strict=True)


class CommentReplyUpdateRequestSchema(BaseModel):
    text: str

    model_config = ConfigDict(strict=True)
