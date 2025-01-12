import logging
from typing import Annotated
from cachetools import LRUCache
from fastapi import Depends, HTTPException
from icechunk import IcechunkError, Repository

from pixel_chunk.state import create_storage

repo_cache = LRUCache(5)


def get_repo(id: str) -> Repository:
    # First check the cache
    repo = repo_cache.get(id, None)
    if repo:
        logging.debug(f"Repo for project {id} found in cache!")
        return repo

    # Otherwise open it and cache it
    try:
        logging.debug(f"Loading repo for project {id}...")
        storage = create_storage(id)
        repo = Repository.open(storage)
        repo_cache[id] = repo
        return repo
    except IcechunkError as e:
        logging.error(f"Failed to open repo for project {id}: {e}")
        raise HTTPException(status_code=404, detail="Project not found")


RepoDep = Annotated[Repository, Depends(get_repo)]
