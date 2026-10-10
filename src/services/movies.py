from copy import deepcopy

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.movies import MovieModel, CertificationModel
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
