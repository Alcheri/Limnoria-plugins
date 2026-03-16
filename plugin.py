###
# Copyright (c) 2025, Barry Suridge
# All rights reserved.
#
#
###
import requests
import json
from urllib.parse import quote

# XXX: Install the following packages before running the script:
try:
    from bs4 import BeautifulSoup
except ImportError as ie:
    raise ImportError(f"Cannot import module: {ie}")

import supybot.log as log
from supybot import callbacks
from supybot.commands import *
from supybot.i18n import PluginInternationalization


_ = PluginInternationalization("IMDb")

# Set headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/91.0.4472.124 Safari/537.36"
}


def search_imdb_title(movie_name):
    """Return top IMDb suggestion entry for a title search."""
    if not movie_name or not movie_name.strip():
        return None

    query = movie_name.strip()
    first_char = next((ch.lower() for ch in query if ch.isalnum()), "x")
    encoded_query = quote(query)
    suggestion_url = (
        f"https://v3.sg.media-imdb.com/suggestion/{first_char}/{encoded_query}.json"
    )

    log.info(f"Fetching IMDb suggestions for {query}")
    try:
        response = requests.get(suggestion_url, headers=headers, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as e:
        log.error(f"IMDb suggestion request failed: {e}")
        return None
    except ValueError as e:
        log.error(f"IMDb suggestion JSON parse failed: {e}")
        return None

    results = payload.get("d", [])
    if not results:
        return None

    # Prefer title IDs, and prioritize movie/series-like matches.
    tt_results = [item for item in results if str(item.get("id", "")).startswith("tt")]
    if not tt_results:
        return None

    preferred_types = {"movie", "feature", "tvSeries", "tvMiniSeries", "tvMovie"}
    for item in tt_results:
        if item.get("qid") in preferred_types or item.get("q") in preferred_types:
            return item

    return tt_results[0]


def _details_from_suggestion(suggestion_item):
    title = suggestion_item.get("l", "Unknown Title")
    year = suggestion_item.get("y", "Unknown Year")
    cast = suggestion_item.get("s", "Unknown Actors")
    kind = suggestion_item.get("q") or suggestion_item.get("qid") or "Unknown Type"

    return {
        "Title": title,
        "Year": str(year),
        "Plot": "Plot unavailable (IMDb blocked detailed page lookup).",
        "Genre": kind,
        "Main Actors": cast,
    }


def get_movie_details_by_id(imdb_id, fallback_details=None):
    if fallback_details is None:
        fallback_details = {
            "Title": "Unknown Title",
            "Year": "Unknown Year",
            "Plot": "Unknown Plot",
            "Genre": "Unknown Genre",
            "Main Actors": "Unknown Actors",
        }

    movie_url = f"https://www.imdb.com/title/{imdb_id}/"
    try:
        response = requests.get(movie_url, headers=headers, timeout=10)
    except requests.RequestException as e:
        log.warning(f"IMDb title request failed for {imdb_id}: {e}")
        return fallback_details

    if response.status_code != 200:
        log.warning(f"IMDb title page blocked/unavailable ({response.status_code})")
        return fallback_details

    soup = BeautifulSoup(response.text, "html.parser")

    # Find JSON-LD data
    json_ld = soup.find("script", type="application/ld+json")
    if not json_ld:
        log.warning("IMDb JSON-LD data not found; using fallback details.")
        return fallback_details

    # Parse JSON-LD data
    try:
        data = json.loads(json_ld.string)
    except (TypeError, json.JSONDecodeError) as e:
        log.warning(f"IMDb JSON-LD parse failed: {e}")
        return fallback_details

    # Extract movie details
    title = data.get("name", fallback_details.get("Title", "Unknown Title"))
    year = data.get("datePublished", fallback_details.get("Year", "Unknown Year"))
    if year != "Unknown Year":
        year = year.split("-")[0]  # Extract just the year
    plot = data.get("description", fallback_details.get("Plot", "Unknown Plot"))

    genre_value = data.get("genre")
    if isinstance(genre_value, list):
        genres = ", ".join(genre_value)
    elif isinstance(genre_value, str):
        genres = genre_value
    else:
        genres = fallback_details.get("Genre", "Unknown Genre")

    actor_list = data.get("actor", [])
    actors = ", ".join([actor.get("name", "") for actor in actor_list[:5] if actor])
    if not actors:
        actors = fallback_details.get("Main Actors", "Unknown Actors")

    return {
        "Title": title,
        "Year": str(year),
        "Plot": plot,
        "Genre": genres,
        "Main Actors": actors,
    }


class IMDb(callbacks.Plugin):
    """
    A simple plugin to fetch movie details from the Internet Movie Database (IMDb)
    """

    threaded = True

    def __init__(self, irc):
        self.__parent = super(IMDb, self)
        self.__parent.__init__(irc)

    @wrap(["text"])
    def imdb(self, irc, msg, args, movie_name):
        """<movie_name>

        Fetch details of the given movie from IMDb.
        """
        if not self.registryValue("enabled", msg.channel, irc.network):
            return

        suggestion = search_imdb_title(movie_name)
        if suggestion:
            imdb_id = suggestion.get("id")
            if not imdb_id:
                irc.error(
                    "Movie found, but IMDb did not provide a valid title ID.",
                    prefixNick=False,
                )
                return
            fallback_details = _details_from_suggestion(suggestion)
            details = get_movie_details_by_id(
                imdb_id, fallback_details=fallback_details
            )
            irc.reply("Top Match Details:", prefixNick=False)
            for key, value in details.items():
                irc.reply(f"{key}: {value}", prefixNick=False)
        else:
            irc.error(
                "Movie not found on IMDb! Ensure correct spelling or try a different title.",
                prefixNick=False,
            )


Class = IMDb


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
