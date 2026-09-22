from pydantic import BaseModel


class LikeMovieListItemSchema(BaseModel):
    id: int
    movie_id: int
