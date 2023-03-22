"""Hello YouTube API ."""
import argparse
import hashlib
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Iterable

import httplib2
#from googleapiclient.discovery import build
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from oauth2client.tools import ClientRedirectServer

from tools import get_argument_parser, setup, upload_batches


from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import pandas as pd


df = pd.read_excel(r'~/Dropbox/quantum/data/All_data_1.xlsx', sheet_name = 'List_data')
videoid_list = df['VideoID'].tolist()
title_list = df['Title'].tolist()
speaker_list = df['Speaker'].tolist()
place_list = df['Place'].tolist()
Year_list = df['Year'].tolist()
Nr_list = df['Number'].tolist()

SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']
PLATFORM = "Youtube"
FIELDS = dict(
    author='keyword',
    omroep='keyword',
    platform='keyword',
    samenvatting='text',
    categories='tag',
    tags='tag',
    dislike="long",
    like_count="long",
    fav_count="long",
    reply_count="long",
    view_count="long",
    channel="keyword"
)


class YoutubeScraper:
    def __init__(self, client_secret: str):
        storage = file.Storage(Path.cwd() / 'youtube.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            # Write credentials to temporary file, rewind, and start auth flow
            with tempfile.NamedTemporaryFile(suffix=".json", mode="w") as f:
                f.write(client_secret)
                f.seek(0)
                flow = client.flow_from_clientsecrets(f.name, scope=SCOPES, message="Invalid credentials")
                flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args([])
                credentials = tools.run_flow(flow, storage, flags)
        http = credentials.authorize(http=httplib2.Http())
        self.service = build('youtube', 'v3', http=http)

    def _get_video_list(self, api="search", **kargs):
        """File-cached call to youtube API"""
        kargs_dump = json.dumps({k: kargs[k] for k in sorted(kargs)})
        key = hashlib.sha224(kargs_dump.encode("utf-8")).hexdigest()
        fn = Path.cwd() / ".api-cache" / f"{api}_{key}.json"
        if not fn.parent.exists():
            fn.parent.mkdir()
        if fn.exists():
            return json.load(fn.open())
        else:
            results = getattr(self.service, api)().list(**kargs).execute()
            json.dump(results, fn.open('w'))
            return results

    def video_list_pages(self, part='id,snippet', maxResults=50, **options) -> Iterable[List[str]]:
        while True:
            results = self._get_video_list(api='search', part=part, order='date', maxResults=maxResults, **options)
            ids = (item['id']['videoId'] for item in results['items'] if item["id"]["kind"] == "youtube#video")
            yield ids
            if "nextPageToken" not in results:
                break
            options["pageToken"] = results["nextPageToken"]

    def get_documents(self, **options):
        for page in self.video_list_pages(part='id,snippet', **options):
            videos = self._get_video_list(api='videos', part="snippet,statistics", id=",".join(page), maxResults=50)
            for video in videos['items']:
                yield _amcat_document(video)


def _parse_date(date: str) -> datetime:
    return datetime.strptime(date.replace(".000Z", "").replace("Z", ""), "%Y-%m-%dT%H:%M:%S")


def _amcat_document(video):
    return dict(
        url=f"https://www.youtube.com/watch?v={video['id']}",
        title=video['snippet']['title'],
        text=video['snippet']['description'] or "-",
        date=_parse_date(video['snippet']['publishedAt']),
        channel=video['snippet']['channelTitle'],
        view_count=video['statistics']['viewCount'],
        like_count=video['statistics'].get('likeCount', 0),
        dislike_count=video['statistics'].get('dislikeCount', 0),
        fav_count=video['statistics'].get('favoriteCount', 0),
        reply_count=video['statistics'].get('commentCount', 0),
    )


if __name__ == '__main__':
    parser = get_argument_parser()
    parser.add_argument("--to-date", help="Start scraping from this date", type=datetime.fromisoformat)
    args, config, config_omroep, conn = setup(parser, FIELDS)
    scraper = YoutubeScraper(config['google']['client_secret'])

    if 'youtube_channel' in config_omroep:
        channel = config_omroep['youtube_channel']
    elif 'youtube_username' in config_omroep:
        r = scraper.service.channels().list(part="contentDetails", forUsername=config_omroep['username']).execute()
        channel = r['items'][0]['id']
    else:
        raise Exception(f"Omroep {args.omroep} has no youtube_channel or youtube_username")

    opts = dict(channelId=channel)
    if args.from_date:
        opts['publishedAfter'] = f"{args.from_date.isoformat()}Z"
    if args.to_date:
        opts['publishedBefore'] = f"{args.to_date.isoformat()}Z"
    docs = scraper.get_documents(**opts)
    upload_batches(conn, config_omroep['index'], docs, platform=PLATFORM, omroep=config_omroep['omroep'])
