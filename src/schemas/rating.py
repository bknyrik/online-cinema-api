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


class MovieCommentDetailResponseSchema(BaseModel):
    id: int
    created_at: datetime
    movie_id: int
    text: str
    profile_id: int


class MovieCommentListResponseSchema(BaseModel):
    comments: list[MovieCommentDetailResponseSchema]
    total_comments: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class MovieCommentCreateRequestSchema(BaseModel):
    movie_id: int
    text: str


class MovieCommentUpdateRequestSchema(BaseModel):
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
    text: str = Field(min_length=1)

    model_config = ConfigDict(strict=True)


class CommentReplyUpdateRequestSchema(BaseModel):
    text: str = Field(min_length=1)

    model_config = ConfigDict(strict=True)


class CommentLikeDetailResponseSchema(BaseModel):
    id: int
    created_at: datetime
    comment_id: int
    profile_id: int


class CommentLikeListResponseSchema(BaseModel):
    likes: list[CommentLikeDetailResponseSchema]
    total_likes: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class CommentLikeCreateRequestSchema(BaseModel):
    comment_id: int


class MovieRateDetailResponseSchema(BaseModel):
    id: int
    created_at: datetime
    movie_id: int
    profile_id: int
    scale: int


class MovieRateListResponseSchema(BaseModel):
    rates: list[MovieRateDetailResponseSchema]
    total_rates: int
    total_pages: int
    prev: str | None
    next: str | None

    model_config = ConfigDict(from_attributes=True)


class MovieRateCreateRequestSchema(BaseModel):
    movie_id: int
    scale: int = Field(min_length=1, max_length=10)

    model_config = ConfigDict(strict=True)


class MovieUpdateRequestSchema(BaseModel):
    scale: int = Field(min_length=1, max_length=10)

    model_config = ConfigDict(strict=True)
