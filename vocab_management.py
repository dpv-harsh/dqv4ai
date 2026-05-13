#!/usr/bin/env python3
#author: Harshvardhan J. Pandit

'''Data and configurations for vocabulary management'''

import csv
import hashlib
import logging
import re
import unicodedata

from rdflib import BNode, Literal, Namespace
import slugify

logging.basicConfig(
    level=logging.DEBUG, format='%(levelname)s - %(funcName)s :: %(lineno)d - %(message)s')
DEBUG = logging.debug
INFO = logging.info

# == data ==

# DPV Version
DPV_VERSION = "2.4-dev"
DPV_PREVIOUS_VERSION = "2.3"
DPV_PUBLISH_DATE = "2026-07-31"
# Document status: should be one of CG-DRAFT or CG-FINAL
DOCUMENT_STATUS = "CG-DRAFT"

# === serializations ===

# Serialisations are `key:value` where `key` is the file extension
# and `value` is the format passed to rdflib to serialise triples

if DOCUMENT_STATUS == "CG-DRAFT":
    # in draft mode, we only generate turtle files, and no OWL files
    RDF_SERIALIZATIONS = {'ttl': 'turtle'}
    OWL_SERIALIZATIONS = {}
elif DOCUMENT_STATUS == "CG-FINAL":
    # in final model, we generate all serialisations and OWL files
    RDF_SERIALIZATIONS = {
        'rdf': 'xml', 
        'ttl': 'turtle', 
        'n3': 'n3',
        'jsonld': 'json-ld'
    }
    OWL_SERIALIZATIONS = RDF_SERIALIZATIONS
else:
    raise ValueError(f"Unknown {DOCUMENT_STATUS=}")

IANA_TYPES = {
    'html': {
        'title': 'HTML',
        'format': 'https://www.iana.org/assignments/media-types/text/html',
        'standard': 'https://www.w3.org/TR/html/',
    },
    'rdf': {
        'title': 'RDF/XML',
        'format': 'https://www.iana.org/assignments/media-types/application/rdf+xml',
        'standard': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    },
    'ttl': {
        'title': 'Turtle',
        'format': 'https://www.iana.org/assignments/media-types/text/turtle',
        'standard': 'https://www.w3.org/TR/turtle/',
    },
    'n3': {
        'title': 'N3',
        'format': 'https://www.iana.org/assignments/media-types/text/n3',
        'standard': 'https://www.w3.org/TeamSubmission/n3/',
    },
    'jsonld': {
        'title': 'JSON-LD',
        'format': 'https://www.iana.org/assignments/media-types/application/ld+json',
        'standard': 'https://www.w3.org/TR/json-ld11/',
    },
    'owl': {
        'title': 'OWL',
        'format': 'https://www.iana.org/assignments/media-types/application/rdf+xml',
        'standard': 'http://www.w3.org/2002/07/owl#',
    },
}


## === term-statuses ===
VOCAB_TERM_ACCEPT = ('accepted', 'changed', 'modified', 'sunset')
VOCAB_TERM_REJECT = ('deprecated', 'removed')

## === term-ignored

IGNORED_TERMS = ('rdf:type', 'rdfs:Class', 'rdf:Property', 'skos:Concept')

# === namespaces ===
NAMESPACE_CSV = (
    'vocab_csv/Namespaces.csv',
    'vocab_csv/Namespaces_Other.csv',
    )
NAMESPACES = {}
for csvfile in NAMESPACE_CSV:
    # DEBUG(f'Extracting namespaces from {csvfile}')
    with open(csvfile, 'r') as fd:
        csvreader = csv.reader(fd)
        next(csvreader)
        for row in csvreader:
            prefix, iri = row[0], row[1]
            variable = prefix.upper().replace('-', '_')
            namespace = Namespace(iri)
            globals()[variable] = namespace
            NAMESPACES[prefix] = namespace
            if iri.startswith('https://w3id.org/dpv'):
                NAMESPACES[f'{prefix}-owl'] = Namespace(iri.replace('#', '/owl#'))
            # DEBUG(f'{prefix} namespace with IRI {iri}')

from rdflib import Graph
NS = Graph()
NS.ns = { k:v for k,v in NAMESPACES.items() }

# === Import/Export for RDF and HTML ===

# Root folder to import RDF files from
IMPORT_PATH = f'docs'
# Root folder to export HTML files to
EXPORT_PATH = f'docs'
# Root folder where Jinja2 templates are stored
TEMPLATE_PATH = '.'
# RDF to be stored in folder
EXPORT_RDF_PATH = f'docs'

# === csv-files ===
IMPORT_CSV_PATH = './vocab_csv'
CSVFILES = {
    'iso-25059': {
        'core': {
            'taxonomy': f'{IMPORT_CSV_PATH}/DIS_25059.csv',
        }
    },
    'eu-aiact': {
        'core': {
            'taxonomy': f'{IMPORT_CSV_PATH}/eu_aiact.csv',
        }
    },
}

# === translations ===
IMPORT_TRANSLATIONS = {
    # 'de': {
    #     'lang': 'German',
    #     'prod': f'{IMPORT_CSV_PATH}/DE_prod.csv',
    #     'verify': f'{IMPORT_CSV_PATH}/DE_verify.csv',
    # },
    # 'fr': {
    #     'lang': 'French',
    #     'prod': f'{IMPORT_CSV_PATH}/FR_prod.csv',
    #     'verify': f'{IMPORT_CSV_PATH}/FR_verify.csv',
    # },
    # 'it': {
    #     'lang': 'Italian',
    #     'prod': f'{IMPORT_CSV_PATH}/IT_prod.csv',
    #     'verify': f'{IMPORT_CSV_PATH}/IT_verify.csv',
    # },
    # 'es': {
    #     'lang': 'Spanish',
    #     'prod': f'{IMPORT_CSV_PATH}/ES_prod.csv',
    #     'verify': f'{IMPORT_CSV_PATH}/ES_verify.csv',
    # },
}
# This file will save the missing translations.
# The initial list is populated in [[200.py]] and then the data is 
# collected and overwritten in [[300.py]]
TRANSLATIONS_MISSING_FILE = f"{IMPORT_CSV_PATH}/translations_missing.json"

# === rdf-vocabs ===
# How to do this?
# load all vocabulary files - create a global dict
RDF_VOCABS = {
    'iso-25059': {
        'vocab': f'docs/iso-25059/iso-25059.ttl',
        'template': 'template_aiqv_iso_25059.jinja2',
        'export': 'docs/iso-25059',
        'modules': {
            'core': 'docs/iso-25059/modules/core.ttl',
        },
        'module-template': {
        },
        'metadata': {
            "dct:title": "AIQV ISO-25059",
            "dct:description": "AIQV",
            "dct:created": "2026-05-12",
            "dct:modified": "2026-05-12",
            "dct:creator": "Anonymous",
            "schema:version": "0.1",
            "profile:isProfileOf": "",
            "bibo:status": "published",
        },
    },
    'eu-aiact': {
        'vocab': f'docs/eu-aiact/eu-aiact.ttl',
        'template': 'template_aiqv_eu_aiact.jinja2',
        'export': 'docs/eu-aiact',
        'modules': {
            'core': 'docs/eu-aiact/modules/core.ttl',
        },
        'module-template': {
        },
        'metadata': {
            "dct:title": "AIQV",
            "dct:description": "AIQV",
            "dct:created": "2026-05-12",
            "dct:modified": "2026-05-12",
            "dct:creator": "Anonymous",
            "schema:version": "0.1",
            "profile:isProfileOf": "",
            "bibo:status": "published",
        },
    },
}

# === exports ===
RDF_STRUCTURE = {
    'aiqv': {
        'main': f'{EXPORT_RDF_PATH}',
        'modules': f'{EXPORT_RDF_PATH}',
    },
    'iso-25059': {
        'main': f'{EXPORT_RDF_PATH}/iso-25059',
        'modules': f'{EXPORT_RDF_PATH}/iso-25059/modules',
    },
    'eu-aiact': {
        'main': f'{EXPORT_RDF_PATH}/eu-aiact',
        'modules': f'{EXPORT_RDF_PATH}/eu-aiact/modules',
    },
}

# Collated concepts
RDF_COLLATIONS = (
)

# === SPARQL Query Hooks ===
RDF_EXPORT_HOOK = {
}

# === examples ===
EXAMPLES = {}

# == functions ==

# === prefix-iri ===
def prefix_from_iri(iri):
    for prefix, ns in NAMESPACES.items():
        if iri.startswith(ns):
            term = iri.replace(ns, '')
            return f'{prefix}:{term}'
    return None

# === contributors ==
import json
with open(f'./contributors.json', 'r') as fd:
    contributors = json.load(fd)


def generate_author_affiliation(author):
    '''takes author name, returns affiliation'''
    author = str(author)
    if author in contributors:
        return contributors[author]['affiliation']
    return ''


def generate_author_orcid(author):
    '''takes author name, returns affiliation'''
    author = str(author)
    if author in contributors:
        if 'ORCID' in contributors[author]:
            return contributors[author]['ORCID']
    return ''


def generate_author_website(author):
    '''takes author name, returns affiliation'''
    author = str(author)
    if author in contributors:
        if 'website' in contributors[author]:
            return contributors[author]['website']
    return ''


def generate_authors_affiliations(authors):
    '''takes author name, returns affiliation'''
    authors = [contributors[author] for author in contributors]
    return authors


def _person_slugify():
    '''person is a string, slugify means make it IRI compatible'
    - e.g. 'Harshvardhan J. Pandit' should be 'HarshvardhanJPandit'
    - for creating IRIs, we create a BNode and return it
    - to maintain consistency, we use the same BNode, and maintain
    a register/dict of people handled so far
    - PREFIX = 'person-'  # to distinguish what this is
    '''
    people = {}
    def _helper(person_name):
        person_name = person_name.strip()
        nonlocal people
        person = slugify.slugify(f"person-{person_name}")
        if person in people:
            return people[person]
        org_name = generate_author_affiliation(person_name)
        if not org_name:
            raise Exception(f"{person_name} org is empty!")
        org = slugify.slugify(f"org-{org_name}")

        bnode_person = BNode(person)
        bnode_org = BNode(org)

        triples = []
        triples.append((bnode_person, RDF.type, FOAF.Person))
        triples.append((bnode_person, RDF.type, DCT.Agent))
        triples.append((bnode_person, FOAF.name, Literal(person_name)))
        if generate_author_orcid(person_name):
            triples.append((bnode_person, SCORO.hasORCID, Literal(generate_author_orcid(person_name))))
        if generate_author_website(person_name):
            triples.append((bnode_person, FOAF.homepage, Literal(generate_author_website(person_name))))
        triples.append((bnode_org, RDF.type, FOAF.Organization))
        triples.append((bnode_org, FOAF.name, Literal(org_name)))
        triples.append((bnode_person, ORG.memberOf, bnode_org))
        people[person] = {
            'person': bnode_person,
            'org': bnode_org,
            'triples': triples,
        }
        return people[person]
    return _helper

PERSON_DICT = _person_slugify()
