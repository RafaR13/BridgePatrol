from db.repository.bridge_tables.mayan import *

from normalization.mappers.mayan.mapper import *
from .runner import normalize

def normalize_mayan():
    jobs = [ """ TODO: ADD """ ]
    normalize(bridge="mayan", jobs=jobs)