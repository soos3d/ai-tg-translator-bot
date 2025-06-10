"""Cache service module for efficient memory management."""
import time
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

class CacheService:
    """Service for managing in-memory caches with size limits and expiration."""
    
    def __init__(self, max_size=1000, expiration_seconds=3600):
        """
        Initialize the cache service.
        
        Args:
            max_size (int): Maximum number of items to keep in cache
            expiration_seconds (int): Time in seconds after which items expire
        """
        self.max_size = max_size
        self.expiration_seconds = expiration_seconds
        self._cache = OrderedDict()  # Using OrderedDict for LRU functionality
        self._expiry = {}  # Store expiration timestamps
        logger.info(f"Cache initialized with max size: {max_size}, expiration: {expiration_seconds}s")
    
    def get(self, key):
        """
        Get an item from the cache.
        
        Args:
            key: The key to look up
            
        Returns:
            The cached value or None if not found or expired
        """
        # Check if key exists and not expired
        if key in self._cache:
            if time.time() < self._expiry.get(key, 0):
                # Move to end to mark as recently used
                value = self._cache.pop(key)
                self._cache[key] = value
                return value
            else:
                # Expired, remove it
                self._remove(key)
                logger.debug(f"Cache item expired: {key}")
                return None
        return None
    
    def set(self, key, value):
        """
        Store an item in the cache.
        
        Args:
            key: The key to store
            value: The value to store
            
        Returns:
            bool: True if successful
        """
        # Remove if it already exists
        self._remove(key)
        
        # Check if we need to make room
        if len(self._cache) >= self.max_size:
            # Remove oldest item (first item in OrderedDict)
            oldest = next(iter(self._cache))
            self._remove(oldest)
            logger.debug(f"Cache full, removed oldest item: {oldest}")
        
        # Add new item
        self._cache[key] = value
        self._expiry[key] = time.time() + self.expiration_seconds
        logger.debug(f"Added item to cache: {key}")
        return True
    
    def _remove(self, key):
        """Remove an item from the cache."""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
    
    def cleanup(self):
        """Remove all expired items from the cache."""
        current_time = time.time()
        expired_keys = [k for k, exp_time in self._expiry.items() if current_time > exp_time]
        for key in expired_keys:
            self._remove(key)
        
        count = len(expired_keys)
        if count > 0:
            logger.info(f"Cache cleanup removed {count} expired items")
        return count
    
    def clear(self):
        """Clear the entire cache."""
        self._cache.clear()
        self._expiry.clear()
        logger.info("Cache cleared")
    
    def size(self):
        """Return the current cache size."""
        return len(self._cache)
