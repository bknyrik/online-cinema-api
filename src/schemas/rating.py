from pydantic import BaseModel, ConfigDict


class LikeMovieListItemSchema(BaseModel):
    id: int
    movie_id: int


class LikeMovieListResponseSchema(BaseModel):
    likes: list[LikeMovieListItemSchema]

    model_config = ConfigDict(from_attributes=True)


class LikeMovieDataRequestSchema(BaseModel):
    movie_id: int
