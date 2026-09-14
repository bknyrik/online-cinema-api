

class PaginationLimitOffsetMixin:

    @staticmethod
    def get_limit_offset(pagination_data: dict[str, int]) -> tuple[int, int]:
        return (
            pagination_data["per_page"],
            (pagination_data["page"] - 1) * pagination_data["per_page"]
        )
