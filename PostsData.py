from dataclasses import dataclass
from datetime import datetime


@dataclass
class PostsData:
    description: str | None
    likes: int | None
    comments: int | None
    post_data: datetime | None
