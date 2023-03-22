import argparse
import json
import logging
from argparse import Namespace
from datetime import datetime
from typing import Iterable, List, Tuple, Optional

import toml
from amcat4py import AmcatClient


def get_argument_parser():
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')
    parser = argparse.ArgumentParser()
    parser.add_argument("omroep", help="Name of omroep")
    parser.add_argument("--config", help="Configuration file", default="config.toml")
    parser.add_argument("--amcat", help="Amcat host to connect to (as defined in config)", default="default")
    parser.add_argument("--from-date", help="Stop parsing at this date", type=datetime.fromisoformat)
    return parser


def setup(parser: argparse.ArgumentParser, fields: Optional[dict] = None) -> Tuple[Namespace, dict, dict, AmcatClient]:
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')
    # When running locally, disable OAuthlib's HTTPs verification. When
    # running in production *do not* leave this option enabled.
    # os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    config = toml.load(args.config)
    config_omroep = config[args.omroep]
    conn = get_amcatclient(config, args.amcat)
    check_index(conn, config_omroep['index'], fields)
    return args, config, config_omroep, conn


def get_amcatclient(config, name='default'):
    amcat_config = config['amcat'][name]
    logging.info(f"Connecting to AmCAT {amcat_config['username']}@{amcat_config['host']}")
    return AmcatClient(amcat_config['host'])


def upload_batches(conn: AmcatClient, index: str, documents: Iterable[dict], platform: str, omroep: str,
                   chunk_size=100, extra_properties: dict = None):
    urls = get_existing_urls(conn, index, platform)
    for chunk in chunks(documents, chunk_size=chunk_size):
        new = [d for d in chunk if d['url'] not in urls]
        if not new:
            continue
        logging.info(f"Uploading {len(new)} new documents to {conn.host}/index/{index}")
        for doc in new:
            if extra_properties:
                doc.update(extra_properties)
            doc['platform'] = platform
            doc['omroep'] = omroep
            if not doc.get('title', '').strip():
                open("/tmp/test.json", "w").write(json.dumps(doc, default=amcat4apiclient.serialize))
                raise Exception("Document without title, saved to /tmp/test.json")
        conn.upload_documents(index, new)


def chunks(items: Iterable, chunk_size=100) -> Iterable[List]:
    buffer = []
    for item in items:
        buffer.append(item)
        if len(buffer) > chunk_size:
            yield buffer
            buffer = []
    if buffer:
        yield buffer


def check_index(conn: AmcatClient, index: str, fields: Optional[dict] = None):
    if not conn.check_index(index):
        conn.create_index(index)
    if fields:
        conn.set_fields(index, fields)


def get_existing_urls(conn: AmcatClient, index: str, platform: str):
    urls = {a['url'] for a in conn.query(index, filters=dict(platform=platform), fields=["url"])}
    logging.info(f"Found {len(urls)} urls in {conn.host}/index/{index} with platform={platform}")
    return urls
