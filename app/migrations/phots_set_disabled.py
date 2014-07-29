"""
Makes sure all the phots have a disabled attribute on them.
"""
from models.rethink.phot.photModel import Phot

models = [Phot]

def migration(document):
    if not "disabled" in document:
        document.disabled = False
