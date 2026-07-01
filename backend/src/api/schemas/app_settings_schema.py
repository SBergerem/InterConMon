from pydantic import BaseModel
from typing import Any


class AppSettingResponse(BaseModel):
    original_name: str
    display_name: str
    value: Any


class AppSettingCategoryResponse(BaseModel):
    category_name: str
    category_settings: list[AppSettingResponse | None]


class AppSettingListResponse(BaseModel):
    items: list[AppSettingCategoryResponse | None]
