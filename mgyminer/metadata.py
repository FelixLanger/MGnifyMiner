import asyncio
import logging
import sys
import xml.etree.ElementTree as ET
from datetime import timedelta
from typing import List

import mysql.connector
import pandas as pd
from aiohttp_client_cache import CachedSession, SQLiteBackend

from mgyminer.config import load_config
from mgyminer.utils import mgyp_to_id, proteinID_to_mgyp

logging.basicConfig(
    format="%(asctime)s.%(msecs)03d %(levelname)s:%(name)s: %(message)s",
    level=logging.DEBUG,
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("areq")
logging.getLogger("chardet.charsetprober").disabled = True

assebmly_api = "https://www.ebi.ac.uk/metagenomics/api/v1/assemblies/{id}?format=json"
ena_sample_api = "https://www.ebi.ac.uk/ena/browser/api/xml/{id}"


cfg = load_config()


def find_origin_assemblies(mgyps: List) -> dict:
    # Create Database connection
    proteindb = mysql.connector.connect(**cfg["mysql"])
    cursor = proteindb.cursor()

    # Remove dublicates from input list & convert to plain IDs
    mgyps = list(dict.fromkeys(mgyps))
    ids = [(mgyp_to_id(mgyp),) for mgyp in mgyps]

    # Database queries to build table with assemblies
    table = "temp1"
    create_tmp_table = (
        f"CREATE TEMPORARY TABLE IF NOT EXISTS {table} (`id` bigint(20)"
        f" unsigned NOT NULL,  PRIMARY KEY (`id`));"
    )
    cursor.execute(create_tmp_table)
    populate_statement = f"INSERT INTO {table} (id) VALUES (%s)"
    cursor.executemany(populate_statement, ids)
    join_statement = (
        f"SELECT {table}.id, assembly.accession FROM {table} "
        f"LEFT JOIN protein_metadata ON {table}.id = protein_metadata.mgyp_id "
        f"LEFT JOIN assembly ON assembly_id = assembly.id"
    )
    cursor.execute(join_statement)
    sqlresponse = cursor.fetchall()

    # create proteinacc : assembly accs mapping
    assemblies = {}
    for t in sqlresponse:
        protein, assembly = t
        protein = proteinID_to_mgyp(protein)
        if protein in assemblies:
            assemblies[protein].append(assembly)
        else:
            assemblies[protein] = [assembly]

    return assemblies


async def fetch_api(session, url, format=None):
    try:
        logger.debug(f"Requesting data for {url}")
        response = await session.get(url)
        logger.debug(f"Got response {response.status} for URL: {url}")
        if response.ok:
            if format == "json":
                return await response.json()
            else:
                return await response.text()
        else:
            # TODO retry depending on response code
            return None
    except Exception as err:
        logger.warning(f"An error has occured: {err}")


def get_sample_accession(assembly_metadata):
    """Take assembly api response and parse out the corresponding sample accession"""
    if assembly_metadata:
        try:
            sample_accession = assembly_metadata["data"]["relationships"]["samples"][
                "data"
            ][0]["id"]
            return sample_accession
        # do nothing in the cases where there is an assembly entry in the api that is not pointing to a sample
        except IndexError:
            return None


def metadata_dict(meta_xml):
    metadata = {}
    root = ET.fromstring(meta_xml)
    for attribute in root.findall("./SAMPLE/SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE"):
        tag = None
        value = None
        unit = None
        for entry in attribute:
            if entry.tag == "TAG":
                tag = entry.text.lower()
            if entry.tag == "VALUE":
                value = entry.text
            if entry.tag == "UNITS":
                unit = entry.text
        if value:
            metadata[tag] = {"value": value, "unit": unit}
    return metadata


async def assembly_metadata(session, assembly):
    response = await fetch_api(session, assebmly_api.format(id=assembly), format="json")
    sample_accession = get_sample_accession(response)
    sample_meta = await fetch_api(session, ena_sample_api.format(id=sample_accession))
    return (assembly, sample_accession, sample_meta)


async def sample_metadata(assemblies):
    cache = SQLiteBackend(
        cache_name=cfg["metadata"]["location"],
        expire_after=timedelta(days=cfg["metadata"]["expire_after"]),
    )

    async with CachedSession(cache=cache) as session:
        sample_metadata = await asyncio.gather(
            *(assembly_metadata(session, assembly) for assembly in assemblies)
        )
        metadata = {}
        for assembly, sample_accession, sample_meta in sample_metadata:
            if sample_meta:
                metadata[assembly] = (sample_accession, metadata_dict(sample_meta))
        # metadata = {assembly:(sample_accession, metadata_dict(sample_meta)) for assembly ,
        # sample_accession, sample_meta in sample_metadata}
    return metadata


def add_metadata(df, interests, metadata, assemblies_mapping):
    """
    Add multiple columns with metadata to df
    :param df: input df
    :param metadata: list of metadata fields of interest
    :return: df
    """
    # Mapping for different spelling variants in ENA Metadata
    meta_mapping = {
        "temperature": ["temperature", "temp"],
        "alkalinity": ["alkalinity"],
        "biome": ["environment (biome)"],
        "depth": ["depth", "geographic location (depth)"],
        "location": [
            "geo_loc_name",
            "geographic location",
            "geographic location (country and/or sea)",
            "geographic location (country and/or sea, region)",
            "geographic location (country and/or sea,region)",
            "geographic location (region and locality)",
        ],
        "ph": ["ph"],
        "salinity": ["salinity", "sallinity psu", "sodium"],
        "lat": [
            "latitude start",
            "geographic location (latitude)",
            "lat_lon",
        ],
        "long": ["geographic location (longitude)", "longitude start", "lat_lon"],
    }

    table_data = []
    for protein in set(df.target_name):
        data = {field: [] for field in interests}
        data["target_name"] = protein
        # Fuer jedes protein suche ich mir die assemblies
        for assembly in assemblies_mapping[protein]:
            # fuer jedes interessante feld siche ich mir die daten aus dem assembly
            if assembly in metadata.keys():
                # TODO if assembly should be removed once private proteins are removed
                for field in interests:
                    hit = [
                        name
                        for name in meta_mapping[field]
                        if name in metadata[assembly][1].keys()
                    ]
                    if hit:
                        data[field].append(metadata[assembly][1][hit[0]]["value"])
        table_data.append(data)
    return pd.DataFrame(table_data)


def only_numeric(values):
    """
    convert all values in a list to floats and filter out invalid (non numeric entries)
    :param values:
    :return:
    """
    out = []
    for value in values:
        try:
            out.append(float(value))
        except ValueError:
            pass
    return out


def make_min_max(values):
    """make a span from a list of values"""
    if values:
        return (min(values), max(values))


def get_metadata(args):
    filename = args.input.stem
    file_dir = args.input.parents[0]
    df = pd.read_csv(args.input)
    accessions = list(df.target_name)
    assemblies_mapping = find_origin_assemblies(accessions)
    all_assemblies = [
        assembly
        for assemblies in assemblies_mapping.values()
        for assembly in assemblies
    ]
    metadata = asyncio.run(sample_metadata(all_assemblies))
    meta_df = add_metadata(
        df, ["location", "ph", "biome", "temperature"], metadata, assemblies_mapping
    )
    meta_df["temperature"] = meta_df["temperature"].apply(
        lambda x: make_min_max(only_numeric(x))
    )
    result = df.merge(
        meta_df, left_on="target_name", right_on="target_name", how="left"
    )
    result.to_csv(file_dir / f"{filename}_meta.csv", index=False)
