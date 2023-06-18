import os
import datetime as dt
from typing import Final

import attrs
import httpx

from bot.utility.language import LanguageCode


API_URI: Final[str] = "https://api.themoviedb.org/3"
BASE_POSTER_URI: Final[str] = "http://image.tmdb.org/t/p/w780"

TMDB_API_KEY: Final[str] = os.getenv("TMDB_API_KEY")


@attrs.define
class MovieProperties:
    title: str = attrs.field()
    rating: float = attrs.field()
    popularity: float = attrs.field()
    release_date: dt.datetime = attrs.field()
    overview: str = attrs.field()
    poster_uri: str | None = attrs.field()


def search_movies(query: str, language_code: LanguageCode) -> list[MovieProperties]:
    response = httpx.get(
        API_URI + "/search/movie", params={"query": query, "language": language_code, "api_key": TMDB_API_KEY}
    )
    response_json = response.json()

    return [
        MovieProperties(
            title=movie_prop_dict["title"],
            release_date=movie_prop_dict["release_date"],
            rating=movie_prop_dict["vote_average"],
            popularity=movie_prop_dict["popularity"],
            overview=movie_prop_dict["overview"],
            poster_uri=(BASE_POSTER_URI + movie_prop_dict["poster_path"])
            if movie_prop_dict["poster_path"] is not None
            else None,
        )
        for movie_prop_dict in response_json["results"]
    ]
