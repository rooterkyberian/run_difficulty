#!python3
import pathlib
import random
import re
import time
from datetime import timedelta
from urllib.parse import urljoin

import typer
from bs4 import BeautifulSoup
from requests_cache import CachedSession

session = CachedSession(
    ".requests_cache",
    use_cache_dir=True,
    expire_after=timedelta(days=100),
)

output_path = pathlib.Path(__file__).parent / "fetched" / "b4sport"


def download_runs(query: str):
    output_path.mkdir(parents=True, exist_ok=True)
    typer.echo(f"Searching for: {query}")
    next_url = f"https://wyniki.b4sport.pl/timerResults/search?q={query}"
    while next_url:
        typer.echo(f"Fetching {next_url}")
        respond = session.get(next_url)

        soup = BeautifulSoup(respond.text, "html.parser")
        for run_link in soup.find_all("a", href=True, title="Pokaż"):
            typer.echo(f"\tfetching run under {run_link['href']}")
            id_ = re.match(r".+?(?P<id>\d+).html$", run_link["href"]).group("id")
            _download_run(id_)

        for link in soup.find_all("a", href=True, text="Następna>"):
            if not next_url.endswith(link["href"]):
                next_url = urljoin(next_url, link["href"])
                break
        else:
            next_url = None


def _download_run(id_: str):
    output_file_path = output_path / f"{id_}.csv"
    if output_file_path.exists():
        return
    csv_url = f"https://wyniki.b4sport.pl/timerResults/printResults/location_nr/-1/id/{id_}/format/csv"
    resp = session.get(csv_url)
    output_file_path.write_text(resp.content.decode("iso8859-2"))
    if not resp.from_cache:
        time.sleep(1 + random.random() * 3)


if __name__ == "__main__":
    typer.run(download_runs)
