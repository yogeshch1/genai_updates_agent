# src/fetchers/arxiv_fetcher.py
import argparse
import time
from pathlib import Path
import sys
import datetime
import feedparser

# make src/ importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from db.models import get_session, Item
from utils.logger import get_logger

logger = get_logger(__name__)

def parse_entry(entry):
    arxiv_id = entry.id.split('/abs/')[-1]
    title = getattr(entry, "title", "").replace("\n", " ").strip()
    authors = [a.name for a in getattr(entry, "authors", [])] if getattr(entry, "authors", None) else []
    abstract = getattr(entry, "summary", "")
    published = None
    if getattr(entry, "published_parsed", None):
        published = datetime.datetime(*entry.published_parsed[:6])
    categories = [t['term'] for t in getattr(entry, "tags", [])] if getattr(entry, "tags", None) else []
    link = getattr(entry, "link", "")
    raw = {
        "id": getattr(entry, "id", None),
        "title": title,
        "authors": authors,
        "summary": abstract,
        "link": link,
        "published": getattr(entry, "published", None)
    }
    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "published": published,
        "categories": categories,
        "url": link,
        "raw": raw
    }

def fetch_and_store(categories="cs.CL,cs.LG,stat.ML", max_results=50):
    qcats = "+OR+".join([f"cat:{c}" for c in categories.split(",")])
    url = f"http://export.arxiv.org/api/query?search_query={qcats}&start=0&max_results={max_results}&sortBy=lastUpdatedDate&sortOrder=descending"
    logger.info(f"Querying arXiv: {url}")
    feed = feedparser.parse(url)
    session = get_session()
    inserted = 0
    for entry in feed.entries:
        item = parse_entry(entry)
        # dedupe by source_id
        exists = session.query(Item).filter_by(source="arxiv", source_id=item["arxiv_id"]).first()
        if exists:
            # update raw/updated_at
            exists.raw = item["raw"]
            exists.updated_at = datetime.datetime.utcnow()
            session.add(exists)
            continue
        new_item = Item(
            source="arxiv",
            source_id=item["arxiv_id"],
            title=item["title"],
            authors=item["authors"],
            abstract=item["abstract"],
            url=item["url"],
            categories=item["categories"],
            published_date=item["published"],
            raw=item["raw"]
        )
        session.add(new_item)
        inserted += 1
    session.commit()
    session.close()
    logger.info(f"Inserted {inserted} new arXiv items")
    return inserted

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=3600, help="Daemon sleep interval (seconds)")
    parser.add_argument("--max_results", type=int, default=50)
    parser.add_argument("--categories", type=str, default="cs.CL,cs.LG,stat.ML")
    args = parser.parse_args()

    if args.once:
        fetch_and_store(categories=args.categories, max_results=args.max_results)
    else:
        logger.info("Starting arXiv fetcher daemon (Ctrl+C to exit)")
        while True:
            try:
                fetch_and_store(categories=args.categories, max_results=args.max_results)
            except Exception as e:
                logger.exception("Error while fetching arXiv")
            time.sleep(args.interval)

if __name__ == "__main__":
    main()