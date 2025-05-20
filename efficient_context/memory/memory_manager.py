"""
Memory management utilities for efficient-context.
"""

import logging
import gc
import os
import psutil
from typing import Optional, Dict, Any
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages memory usage for efficient context handling.
    
    This class provides utilities to monitor and optimize memory usage
    when working with large language models and context on CPU.
    """
    
    def __init__(
        self,
        target_usage_percent: float = 80.0,
        aggressive_cleanup: bool = False,
        memory_monitor_interval: Optional[float] = None,
    ):
        """
        Initialize the MemoryManager.
        
        Args:
            target_usage_percent: Target memory usage as percentage of available memory
            aggressive_cleanup: Whether to perform aggressive garbage collection
            memory_monitor_interval: Interval for memory monitoring in seconds (None to disable)
        """
        self.target_usage_percent = target_usage_percent
        self.aggressive_cleanup = aggressive_cleanup
        self.memory_monitor_interval = memory_monitor_interval
        self.monitor_active = False
        
        logger.info(
            "MemoryManager initialized with target usage: %.1f%%", 
            target_usage_percent
        )
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage statistics.
        
        Returns:
            stats: Dictionary of memory usage statistics
        """
        # Get process memory info
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        
        # Get system memory info
        system_memory = psutil.virtual_memory()
        
        # Calculate usage percentages
        process_percent = (process_memory.rss / system_memory.total) * 100
        system_percent = system_memory.percent
        
        return {
            "process_rss_bytes": process_memory.rss,
            "process_vms_bytes": process_memory.vms,
            "process_percent": process_percent,
            "system_available_bytes": system_memory.available,
            "system_total_bytes": system_memory.total,
            "system_used_percent": system_percent,
        }
    
    def log_memory_usage(self) -> None:
        """Log memory usage statistics."""
        stats = self.get_memory_usage()
        
        logger.info(
            "Memory usage: Process: %.1f%% (%.1f MB), System: %.1f%% (%.1f GB available)",
            stats["process_percent"],
            stats["process_rss_bytes"] / (1024 * 1024),
            stats["system_used_percent"],
            stats["system_available_bytes"] / (1024 * 1024 * 1024)
        )
    
    def cleanup_memory(self) -> None:
        """Perform memory cleanup."""
        # Run garbage collection
        collected = gc.collect()
        
        if self.aggressive_cleanup:
            # Run an additional, more aggressive pass
            collected += gc.collect()
        
        logger.debug("Memory cleanup: Collected %d objects", collected)
    
    def _check_memory_threshold(self) -> bool:
        """
        Check if memory usage exceeds the target threshold.
        
        Returns:
            exceeded: Whether the threshold is exceeded
        """
        stats = self.get_memory_usage()
        return stats["system_used_percent"] > self.target_usage_percent
    
    @contextmanager
    def optimize_memory(self):
        """
        Context manager for optimizing memory during operations.
        
        Example:
            ```
            with memory_manager.optimize_memory():
                # Run memory-intensive operations
            ```
        """
        # Log initial memory state if in debug mode
        if logger.isEnabledFor(logging.DEBUG):
            self.log_memory_usage()
        
        try:
            # Yield control back to the caller
            yield
        finally:
            # Check if we need to clean up memory
            if self._check_memory_threshold():
                logger.info("Memory threshold exceeded, performing cleanup")
                self.cleanup_memory()
                
                # Log final memory state if in debug mode
                if logger.isEnabledFor(logging.DEBUG):
                    self.log_memory_usage()
