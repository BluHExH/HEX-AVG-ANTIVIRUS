"""
HEX-AVG Multithreading Module
Handles concurrent file scanning with thread management
"""

import concurrent.futures
import threading
from queue import Queue
from typing import Callable, Any, List, Dict, Optional
from pathlib import Path
from config import HEXAVGConfig


class ThreadManager:
    """Manages multithreaded operations for file scanning"""
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        timeout: Optional[float] = None
    ):
        """
        Initialize thread manager
        
        Args:
            max_workers: Maximum number of worker threads (default: from config)
            timeout: Timeout for thread operations in seconds
        """
        self.max_workers = max_workers or HEXAVGConfig.DEFAULT_THREADS
        self.timeout = timeout or HEXAVGConfig.MAX_SCAN_DURATION
        
        # Validate thread count
        self.max_workers = max(
            HEXAVGConfig.MIN_THREADS,
            min(self.max_workers, HEXAVGConfig.MAX_THREADS)
        )
        
        # Thread-safe queues
        self.task_queue = Queue()
        self.result_queue = Queue()
        
        # Statistics
        self.stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'active_threads': 0
        }
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        # Executor
        self.executor = None
        self.futures = []
    
    def submit_task(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> concurrent.futures.Future:
        """
        Submit a task to the thread pool
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
        
        Returns:
            Future object representing the task
        """
        if self.executor is None:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            )
        
        with self.lock:
            self.stats['total_tasks'] += 1
        
        future = self.executor.submit(func, *args, **kwargs)
        self.futures.append(future)
        
        return future
    
    def map_tasks(
        self,
        func: Callable,
        items: List[Any],
        show_progress: bool = False
    ) -> List[Any]:
        """
        Map a function over a list of items concurrently
        
        Args:
            func: Function to apply to each item
            items: List of items to process
            show_progress: Whether to show progress (requires callback)
        
        Returns:
            List of results
        """
        if self.executor is None:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            )
        
        results = []
        completed = 0
        total = len(items)
        
        with self.lock:
            self.stats['total_tasks'] = total
        
        # Submit all tasks
        future_to_item = {
            self.executor.submit(func, item): item
            for item in items
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(
            future_to_item,
            timeout=self.timeout
        ):
            item = future_to_item[future]
            
            try:
                result = future.result()
                results.append(result)
                
                with self.lock:
                    self.stats['completed_tasks'] += 1
                
                if show_progress:
                    completed += 1
                    print(f"\rProgress: {completed}/{total} ({completed/total*100:.1f}%)", end='')
            
            except Exception as e:
                with self.lock:
                    self.stats['failed_tasks'] += 1
                
                print(f"\nError processing {item}: {str(e)}")
                results.append(None)
        
        if show_progress:
            print()  # New line after progress
        
        return results
    
    def batch_process(
        self,
        func: Callable,
        items: List[Any],
        batch_size: int = 100,
        callback: Optional[Callable] = None
    ) -> List[Any]:
        """
        Process items in batches
        
        Args:
            func: Function to apply to each item
            items: List of items to process
            batch_size: Number of items per batch
            callback: Optional callback function for progress updates
        
        Returns:
            List of results
        """
        results = []
        total_items = len(items)
        processed = 0
        
        # Process items in batches
        for i in range(0, total_items, batch_size):
            batch = items[i:i + batch_size]
            
            # Process batch concurrently
            batch_results = self.map_tasks(func, batch)
            results.extend(batch_results)
            
            processed += len(batch)
            
            # Call callback if provided
            if callback:
                callback(processed, total_items)
        
        return results
    
    def scan_files(
        self,
        file_paths: List[Path],
        scan_func: Callable[[Path], Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Scan multiple files concurrently
        
        Args:
            file_paths: List of file paths to scan
            scan_func: Function to scan each file
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of scan results
        """
        results = []
        total_files = len(file_paths)
        scanned = 0
        
        if self.executor is None:
            self.executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            )
        
        with self.lock:
            self.stats['total_tasks'] = total_files
        
        # Submit all scan tasks
        future_to_path = {
            self.executor.submit(scan_func, path): path
            for path in file_paths
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(
            future_to_path,
            timeout=self.timeout
        ):
            file_path = future_to_path[future]
            
            try:
                result = future.result()
                results.append(result)
                
                with self.lock:
                    self.stats['completed_tasks'] += 1
                
                scanned += 1
                
                # Call progress callback
                if progress_callback:
                    progress_callback(scanned, total_files, file_path)
            
            except Exception as e:
                with self.lock:
                    self.stats['failed_tasks'] += 1
                
                # Create error result
                results.append({
                    'file_path': str(file_path),
                    'error': str(e),
                    'status': 'error'
                })
        
        return results
    
    def wait_for_completion(self) -> None:
        """Wait for all submitted tasks to complete"""
        if self.futures:
            concurrent.futures.wait(self.futures, timeout=self.timeout)
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the thread pool
        
        Args:
            wait: Whether to wait for tasks to complete
        """
        if self.executor:
            self.executor.shutdown(wait=wait)
            self.executor = None
        
        self.futures = []
    
    def get_statistics(self) -> Dict[str, int]:
        """Get thread manager statistics"""
        with self.lock:
            return self.stats.copy()
    
    def reset_statistics(self) -> None:
        """Reset statistics"""
        with self.lock:
            self.stats = {
                'total_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'active_threads': 0
            }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown(wait=True)
        return False


class ProgressCallback:
    """Simple progress callback for multithreading"""
    
    def __init__(self, description: str = "Processing"):
        """
        Initialize progress callback
        
        Args:
            description: Description of the operation
        """
        self.description = description
        self.completed = 0
        self.total = 0
        self.lock = threading.Lock()
    
    def __call__(self, completed: int, total: int, current_item: Any = None):
        """
        Update progress
        
        Args:
            completed: Number of items completed
            total: Total number of items
            current_item: Current item being processed (optional)
        """
        with self.lock:
            self.completed = completed
            self.total = total
        
        percentage = (completed / total * 100) if total > 0 else 0
        print(
            f"\r{self.description}: {completed}/{total} "
            f"({percentage:.1f}%)",
            end=''
        )
        
        if completed == total:
            print()  # New line when complete