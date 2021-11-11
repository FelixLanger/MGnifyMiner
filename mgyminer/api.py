import asyncio
import io
import logging
import sys
import xml.etree.ElementTree as ET
from datetime import timedelta

from aiohttp_client_cache import CachedSession, SQLiteBackend

with open("../playground/assembly_accessions.txt") as fin:
    assemblies = fin.read().splitlines()
    assemblies = [
        assembly
        for assembly in assemblies
        if assembly.startswith("ERZ") and len(assembly) < 11
    ]

# Logger setup
logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True

# Cache definition
cache = SQLiteBackend(
    cache_name="~/PycharmProjects/MGnifyMiner/playground/.cache/metadata_cache.db",
    expire_after=timedelta(days=100),
)

assebmly_api = "https://www.ebi.ac.uk/metagenomics/api/v1/assemblies/{id}?format=json"
ena_sample_api = "https://www.ebi.ac.uk/ena/browser/api/xml/{id}"


def get_sample_accession(assembly_metadata):
    """Take assembly api response and parse out the corresponding sample accession"""
    if assembly_metadata:
        sample_accession = assembly_metadata["data"]["relationships"]["samples"][
            "data"
        ][0]["id"]
        return sample_accession


async def fetch_api(session, url, format=None):
    try:
        logger.debug(f"Requesting data for {url}")
        response = await session.get(url)
        logger.debug(f"Got response {response.status} for URL: {url}")
    except Exception as err:
        logger.warning(f"An error has occured: {err}")
    if response.ok:
        if format == "json":
            return await response.json()
        else:
            return await response.text()
    else:
        # TODO retry depending on response code
        return None


async def fetch_assembly_metadata(session, assembly_accession):
    """Take assembly accession and get metadata from MGnify API"""
    url = f"https://www.ebi.ac.uk/metagenomics/api/v1/assemblies/{assembly_accession}?format=json"
    try:
        logger.info(f"Requesting data for {assembly_accession}")
        response = await session.get(url)
        logger.info(f"Got response {response.status} for URL: {url}")
        return await response.json()
    except Exception as err:
        logger.info(f"An error has occured: {err}")


async def fetch_sample_metadata(session, sample_accession):
    """Take sample accession and get sample metadata from ENA API"""
    url = f"https://www.ebi.ac.uk/ena/browser/api/xml/{sample_accession}"
    try:
        logger.info(f"Requesting data for {sample_accession}")
        response = await session.get(url)
        logger.info(f"Got response {response.status} for URL: {url}")
        return await response.text()
    except Exception as err:
        logger.info(f"An error has occured: {err}")


async def task(session, assembly):
    response = await fetch_api(session, assebmly_api.format(id=assembly), format="json")
    sample_accession = get_sample_accession(response)
    sample_meta = await fetch_api(session, ena_sample_api.format(id=sample_accession))
    return sample_meta


async def main():
    async with CachedSession() as session:
        sample_metadata = await asyncio.gather(
            *(task(session, assembly) for assembly in assemblies)
        )
        for i, sample in enumerate(sample_metadata):
            if sample:
                f = io.StringIO(sample)
                tree = ET.parse(f)
                root = tree.getroot()
                i = [rank for rank in root.iter("PRIMARY_ID")][0].text
                with open(f"../playground/sample_metadata/{i}.xml", "w") as fout:
                    fout.write(sample)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
