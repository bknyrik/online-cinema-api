from copy import deepcopy

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.movies import (
    MovieModel,
    CertificationModel,
    GenreModel,
    StarModel,
    DirectorModel
)
from src.repositories import movies
from src.services import mixins


class MovieService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin,
    mixins.SearchItemsMixin,
    mixins.SortingItemsMixin,
    mixins.FilterItemsMixin
):

    def __init__(
        self,
        movie_repository: movies.MovieRepository,
        genre_repository: movies.GenreRepository,
        star_repository: movies.StarRepository,
        director_repository: movies.DirectorRepository,
        certification_repository: movies.CertificationRepository
    ) -> None:
        self.model_type = MovieModel
        self.movie_repository = movie_repository
        self.genre_repository = genre_repository
        self.star_repository = star_repository
        self.director_repository = director_repository
        self.certification_repository = certification_repository

    async def handle_movie_data_parent_objects(
        self,
        db: AsyncSession,
        data: dict
    ) -> dict:
        repositories = {
            "genres": self.genre_repository,
            "stars": self.star_repository,
            "directors": self.director_repository,
            "certification": self.certification_repository
        }
        data_copy = deepcopy(data)

        for key, value in data.items():
            match key:
                case "genres" | "stars" | "directors":
                    items = await repositories[key].aget_by_ids(
                        db=db,
                        ids=data_copy[key]
                    )

                    self.validate_items_by_ids_not_found(
                        items=items,
                        ids=data[key],
                        item_type=key.capitalize()
                    )
                    data_copy[key] = items
                case "certification":
                    certification = await repositories[key].aget_by_id(
                        db=db,
                        id_=data[key]
                    )
                    self.validate_item_by_id_not_found(
                        item=certification,
                        id_=data[key],
                        item_type=key.capitalize()
                    )
                    data_copy["certification_id"] = data_copy.pop(key)

        return data_copy


    async def get_movie_list(
        self,
        db: AsyncSession,
        pagination_data: dict,
        filter_data: dict,
        search_data: dict,
        sort_data: dict
    ) -> dict:
        try:
            filter_expressions = self.get_filter_expressions(filter_data)
            search_expressions = self.get_search_expressions(search_data)
            sort_columns = (
                self.get_sort_columns(sort_data)
                if any(value is not None for value in sort_data.values())
                else [self.model_type.id]
            )

            limit, offset = self.get_limit_offset(pagination_data)
            total_movies = await self.movie_repository.acount(
                db=db,
                expressions=filter_expressions + search_expressions
            )
            total_pages = self.get_total_pages(
                total_movies,
                pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_movies
            )

            movies_list = list(
                await self.movie_repository.aget_all(
                    db=db,
                    join_relationships=[
                        "genres",
                        "stars",
                        "directors",
                        "certification"
                    ],
                    offset=offset,
                    limit=limit,
                    expressions=filter_expressions + search_expressions,
                    order_by_columns=sort_columns
                ),
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with movies"
            )
        else:
            prev_page, next_page = (
                self.get_prev_next_urls_pages(
                    "/api/movies/",
                    page=pagination_data["page"],
                    total_pages=total_pages,
                    query_params={
                        **pagination_data,
                        **filter_data,
                        **search_data,
                        **sort_data
                    }
                )
            )
            return {
                "movies": movies_list,
                "total_movies": total_movies,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }

    async def get_detail_movie(self, db: AsyncSession, movie_id: int) -> MovieModel:
        try:
            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=movie_id,
                join_relationships=[
                    "genres",
                    "stars",
                    "directors",
                    "certification"
                ]
            )

            self.validate_item_by_id_not_found(
                item=movie,
                id_=movie_id,
                item_type="Movie"
            )

            return movie
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting movie"
            )

    async def create_movie(self, db: AsyncSession, data: dict) -> MovieModel:
        try:
            movie = await self.movie_repository.aget_by(
                db=db,
                expressions=[
                    self.model_type.name == data["name"],
                    self.model_type.year == data["year"],
                    self.model_type.time == data["time"]
                ]
            )

            self.validate_item_by_attrs_exists(
                item=movie,
                attrs={
                    key: value for key, value in data.items()
                    if key in ("name", "year", "time")
                },
                item_type="Movie"
            )

            data = await self.handle_movie_data_parent_objects(
                db=db,
                data=data
            )

            created_movie = await self.movie_repository.acreate(
                db=db,
                data=data
            )

            created_movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=created_movie.id,
                join_relationships=[
                    "genres",
                    "stars",
                    "directors",
                    "certification"
                ]
            )

            await db.commit()
            return created_movie
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while creating movie"
            )

    async def update_movie(
        self,
        db: AsyncSession,
        movie_id: int,
        data: dict
    ) -> MovieModel:
        try:
            movie = await self.movie_repository.aget_by_id(
                db=db,
                id_=movie_id,
                join_relationships=[
                    "certification",
                    "genres",
                    "stars",
                    "directors"
                ]
            )

            self.validate_item_by_id_not_found(
                item=movie,
                id_=movie_id,
                item_type="Movie"
            )

            if data.get("name") and data.get("year") and data.get("time"):
                another_movie = await self.movie_repository.aget_by(
                    db=db,
                    expressions=[
                        self.model_type.name == data["name"],
                        self.model_type.year == data["year"],
                        self.model_type.time == data["time"]
                    ]
                )

                self.validate_item_by_attrs_with_another_item_exists(
                    item=movie,
                    another_item=another_movie,
                    attrs={
                        key: value for key, value in data.items()
                        if key in ("name", "year", "time")
                    },
                    item_type="Movie"
                )

            data = await self.handle_movie_data_parent_objects(
                db=db,
                data=data
            )

            await self.movie_repository.aupdate(
                db=db,
                instance=movie,
                data=data
            )
            await db.commit()
            await db.refresh(movie)
            return movie
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating movie"
            )

    async def delete_movie(self, db: AsyncSession, movie_id: int) -> None:
        try:
            movie = await self.movie_repository.adelete_by_id(
                db=db,
                id_=movie_id
            )

            self.validate_item_by_id_not_found(
                item=movie,
                id_=movie_id,
                item_type="Movie"
            )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while movie deletion"
            )



class CertificationService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):

    def __init__(
        self,
        certification_repository: movies.CertificationRepository
    ) -> None:
        self.certification_repository = certification_repository

    async def get_certification_list(
        self,
        pagination_data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)
            total_certifications = await self.certification_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_certifications,
                per_page=pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_items=total_certifications,
                total_pages=total_pages
            )

            certifications = await self.certification_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/certifications/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )

            return {
                "certifications": certifications,
                "total_certifications": total_certifications,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "An error occurred while getting"
                    "list with certifications"
                )
            )

    async def get_certification_detail(
        self,
        db: AsyncSession,
        certification_id: int
    ) -> CertificationModel:
        try:
            certification = await self.certification_repository.aget_by_id(
                db=db,
                id_=certification_id
            )

            self.validate_item_by_id_not_found(
                item=certification,
                id_=certification_id,
                item_type="Certification"
            )

            return certification
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting the certification"
            )

    async def create_certification(
        self,
        db: AsyncSession,
        data: dict
    ) -> CertificationModel:
        try:
            certification = await self.certification_repository.aget_by(
                db=db,
                expressions=[CertificationModel.name == data["name"]]
            )

            self.validate_item_by_attrs_exists(
                item=certification,
                attrs=data,
                item_type="Certification"
            )

            certification = await self.certification_repository.acreate(
                db=db,
                data=data
            )

            await db.commit()
            return certification
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while certification creation"
            )

    async def update_certification(
        self,
        db: AsyncSession,
        certification_id: int,
        data: dict
    ) -> CertificationModel:
        try:
            certification = await self.certification_repository.aget_by_id(
                db=db,
                id_=certification_id
            )

            self.validate_item_by_id_not_found(
                item=certification,
                id_=certification_id,
                item_type="Certification"
            )

            another_certification = await self.certification_repository.aget_by(
                db=db,
                expressions=[CertificationModel.name == data["name"]]
            )

            self.validate_item_by_attrs_with_another_item_exists(
                item=certification,
                another_item=another_certification,
                attrs=data,
                item_type="Certification"
            )

            await self.certification_repository.aupdate(
                db=db,
                instance=certification,
                data=data
            )

            await db.commit()
            return certification
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while updating certification"
            )

    async def delete_certification(
        self,
        db: AsyncSession,
        certification_id: int
    ) -> None:
        try:
            certification = await self.certification_repository.adelete_by_id(
                db=db,
                id_=certification_id
            )

            self.validate_item_by_id_not_found(
                item=certification,
                id_=certification_id,
                item_type="Certification"
            )
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while certification deletion"
            )


class GenreService(
    mixins.ModelItemsMixin,
    mixins.PaginationLimitOffsetMixin
):

    def __init__(self, genre_repository: movies.GenreRepository) -> None:
        self.genre_repository = genre_repository

    async def get_genre_list(
        self,
        pagination_data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            total_genres = await self.genre_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_genres,
                per_page=pagination_data["per_page"]
            )
            limit, offset = self.get_limit_offset(pagination_data)

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_genres
            )

            genres = list(
                await self.genre_repository.aget_all(
                    db=db,
                    offset=offset,
                    limit=limit,
                    order_by_columns=[GenreModel.id]
                )
            )
            count_movies = await self.genre_repository.acount_movies(db)
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with genres"
            )
        else:
            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/genres/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )
            genres = [
                {"id": genre.id, "name": genre.name, "movies": count}
                for genre, count in zip(genres, count_movies)
            ]
            return {
                "genres": genres,
                "total_genres": total_genres,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }

    async def get_genre_detail(
        self,
        db: AsyncSession,
        genre_id: int
    ) -> GenreModel:
        try:
            genre = await self.genre_repository.aget_by_id(
                db=db,
                id_=genre_id,
                join_relationships=["movies"]
            )

            self.validate_item_by_id_not_found(genre, genre_id, "Genre")

            return genre
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting the genre"
            )

    async def create_genre(
        self,
        db: AsyncSession,
        data: dict,
    ) -> GenreModel:
        try:
            genre = await self.genre_repository.aget_by(
                db=db,
                expressions=[GenreModel.name == data["name"]]
            )

            self.validate_item_by_attrs_exists(
                item=genre,
                attrs=data,
                item_type="Genre"
            )

            created_genre = await self.genre_repository.acreate(
                db=db,
                data=data
            )
            await db.commit()
            return created_genre
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while genre creation"
            )

    async def update_genre(
        self,
        db: AsyncSession,
        genre_id: int,
        data: dict
    ) -> GenreModel:
        try:
            genre = await self.genre_repository.aget_by_id(
                db=db,
                id_=genre_id
            )

            self.validate_item_by_id_not_found(genre, genre_id, "Genre")

            another_genre = await self.genre_repository.aget_by(
                db=db,
                expressions=[GenreModel.name == data["name"]]
            )

            self.validate_item_by_attrs_with_another_item_exists(
                item=genre,
                another_item=another_genre,
                attrs=data,
                item_type="Genre"
            )

            await self.genre_repository.aupdate(db, genre, data)
            await db.commit()
            return genre
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERnAL_SERVER_ERROR,
                detail="An error occurred while genre updating"
            )

    async def delete_genre(
        self,
        db: AsyncSession,
        genre_id: int
    ) -> None:
        try:
            genre = await self.genre_repository.adelete_by_id(
                db=db,
                id_=genre_id
            )

            self.validate_item_by_id_not_found(genre, genre_id, "Genre")

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while genre deletion"
            )


class StarService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):

    def __init__(self, star_repository: movies.StarRepository) -> None:
        self.star_repository = star_repository

    async def get_star_list(
        self,
        pagination_data: dict,
        db: AsyncSession
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)
            total_stars = await self.star_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_stars,
                per_page=pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_stars
            )

            stars = await self.star_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset,
                order_by_columns=[StarModel.id]
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/stars/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )

            return {
                "stars": stars,
                "total_stars": total_stars,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with stars"
            )

    async def get_star_detail(
        self,
        db: AsyncSession,
        star_id: int
    ) -> StarModel:
        try:
            star = await self.star_repository.aget_by_id(
                db=db,
                id_=star_id
            )

            self.validate_item_by_id_not_found(star, star_id, "Star")

            return star
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting the star"
            )

    async def create_star(
        self,
        db: AsyncSession,
        data: dict
    ) -> StarModel:
        try:
            star = await self.star_repository.aget_by(
                db=db,
                expressions=[StarModel.name == data["name"]]
            )

            self.validate_item_by_attrs_exists(
                item=star,
                attrs=data,
                item_type="Star"
            )

            star = await self.star_repository.acreate(
                db=db,
                data=data
            )

            await db.commit()
            return star
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while star creation"
            )

    async def update_star(
        self,
        db: AsyncSession,
        data: dict,
        star_id: int
    ) -> StarModel:
        try:
            star = await self.star_repository.aget_by_id(
                db=db,
                id_=star_id
            )

            self.validate_item_by_id_not_found(
                item=star,
                id_=star_id,
                item_type="Star"
            )

            another_star = await self.star_repository.aget_by(
                db=db,
                expressions=[StarModel.name == data["name"]]
            )

            self.validate_item_by_attrs_with_another_item_exists(
                item=star,
                another_item=another_star,
                attrs=data,
                item_type="Star"
            )

            await self.star_repository.aupdate(db, star, data)
            await db.commit()
            return star
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while star updating"
            )

    async def delete_star(
        self,
        db: AsyncSession,
        star_id: int
    ) -> None:
        try:
            star = await self.star_repository.adelete_by_id(
                db=db,
                id_=star_id
            )

            self.validate_item_by_id_not_found(star, star_id, "Star")

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while star deletion"
            )


class DirectorService(
    mixins.PaginationLimitOffsetMixin,
    mixins.ModelItemsMixin
):
    def __init__(self, director_repository: movies.DirectorRepository) -> None:
        self.director_repository = director_repository

    async def get_director_list(
        self,
        pagination_data: dict,
        db: AsyncSession,
    ) -> dict:
        try:
            limit, offset = self.get_limit_offset(pagination_data)
            total_directors = await self.director_repository.acount(db)
            total_pages = self.get_total_pages(
                total_items=total_directors,
                per_page=pagination_data["per_page"]
            )

            self.validate_page_not_found(
                page=pagination_data["page"],
                total_pages=total_pages,
                total_items=total_directors
            )

            directors = await self.director_repository.aget_all(
                db=db,
                limit=limit,
                offset=offset,
                order_by_columns=[DirectorModel.id]
            )

            prev_page, next_page = self.get_prev_next_urls_pages(
                "/api/directors/",
                page=pagination_data["page"],
                total_pages=total_pages,
                query_params=pagination_data
            )

            return {
                "directors": directors,
                "total_directors": total_directors,
                "total_pages": total_pages,
                "prev": prev_page,
                "next": next_page
            }
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting list with directors"
            )

    async def get_director_detail(
        self,
        db: AsyncSession,
        director_id: int
    ) -> DirectorModel:
        try:
            director = await self.director_repository.aget_by_id(
                db=db,
                id_=director_id
            )

            self.validate_item_by_id_not_found(
                item=director,
                id_=director_id,
                item_type="Director"
            )

            return director
        except SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while getting the director"
            )

    async def create_director(
        self,
        db: AsyncSession,
        data: dict
    ) -> DirectorModel:
        try:
            director = await self.director_repository.aget_by(
                db=db,
                expressions=[DirectorModel.name == data["name"]]
            )

            self.validate_item_by_attrs_exists(
                item=director,
                attrs=data,
                item_type="Director"
            )

            director = await self.director_repository.acreate(
                db=db,
                data=data
            )
            await db.commit()
            return director
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while director creation"
            )

    async def update_director(
        self,
        db: AsyncSession,
        data: dict,
        director_id: int
    ) -> DirectorModel:
        try:
            director = await self.director_repository.aget_by_id(
                db=db,
                id_=director_id
            )

            self.validate_item_by_id_not_found(
                item=director,
                id_=director_id,
                item_type="Director"
            )

            another_director = await self.director_repository.aget_by(
                db=db,
                expressions=[DirectorModel.name == data["name"]]
            )

            self.validate_item_by_attrs_with_another_item_exists(
                item=director,
                another_item=another_director,
                attrs=data,
                item_type="Director"
            )

            await self.director_repository.aupdate(db, director, data)
            await db.commit()
            return director
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while director updating"
            )

    async def delete_director(
        self,
        director_id: int,
        db: AsyncSession,
    ) -> None:
        try:
            director = await self.director_repository.adelete_by_id(
                db=db,
                id_=director_id
            )

            self.validate_item_by_id_not_found(
                item=director,
                id_=director_id,
                item_type="Director"
            )

            await db.commit()
        except SQLAlchemyError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while director deletion"
            )
