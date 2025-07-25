import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from enum import Enum
import time

class LogLevel(Enum):
    """Enumeration for log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ColorCodes:
    """ANSI color codes for terminal output"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"

class ProgressIndicator:
    """Simple progress indicator for long-running operations"""
    
    def __init__(self, message: str = "Processing", logger: Optional['MacSnapLogger'] = None):
        self.message = message
        self.logger = logger
        self.is_running = False
        self.start_time = None
        
    def start(self):
        """Start the progress indicator"""
        self.is_running = True
        self.start_time = time.time()
        if self.logger:
            self.logger.info(f"{self.message}...")
    
    def stop(self, success: bool = True, final_message: Optional[str] = None):
        """Stop the progress indicator"""
        if not self.is_running:
            return
            
        self.is_running = False
        duration = time.time() - self.start_time if self.start_time else 0
        
        if final_message:
            message = final_message
        else:
            status = "completed" if success else "failed"
            message = f"{self.message} {status}"
            
        if self.logger:
            if success:
                self.logger.success(f"{message} (took {duration:.2f}s)")
            else:
                self.logger.error(f"{message} (took {duration:.2f}s)")

class MacSnapLogger:
    """
    Comprehensive logging system for MacSnap Setup
    
    Features:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - File logging to ~/Library/Logs/MacSnap/setup.log
    - Colored console output
    - Verbose mode support
    - Progress indicators
    - Script output capture
    """
    
    def __init__(self, verbose: bool = False, log_file: Optional[str] = None):
        """
        Initialize the MacSnap logger
        
        Args:
            verbose: Enable verbose (DEBUG) logging
            log_file: Custom log file path (defaults to ~/Library/Logs/MacSnap/setup.log)
        """
        self.verbose = verbose
        self.start_time = datetime.now()
        
        # Set up log file path
        if log_file:
            self.log_file = Path(log_file)
        else:
            log_dir = Path.home() / "Library" / "Logs" / "MacSnap"
            log_dir.mkdir(parents=True, exist_ok=True)
            self.log_file = log_dir / "setup.log"
        
        # Set up Python logging
        self._setup_logging()
        
        # Track console output formatting
        self.supports_color = self._supports_color()
        
        # Log session start
        self.info("="*60)
        self.info(f"MacSnap Setup session started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.info(f"Verbose mode: {'enabled' if verbose else 'disabled'}")
        self.info(f"Log file: {self.log_file}")
        self.info("="*60)
    
    def _setup_logging(self):
        """Set up Python logging configuration"""
        # Create logger
        self.logger = logging.getLogger('macsnap')
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # File handler - always logs everything
        file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler - respects verbose setting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def _supports_color(self) -> bool:
        """Check if the terminal supports ANSI color codes"""
        return (
            hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
            os.environ.get('TERM') != 'dumb' and
            'COLORTERM' in os.environ or 'ANSI_COLORS_DISABLED' not in os.environ
        )
    
    def _colorize(self, text: str, color: str) -> str:
        """Apply color to text if terminal supports it"""
        if self.supports_color:
            return f"{color}{text}{ColorCodes.RESET}"
        return text
    
    def _format_message(self, level: LogLevel, message: str, prefix: str = "") -> str:
        """Format a log message with appropriate colors and prefixes"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Level-specific formatting
        if level == LogLevel.DEBUG:
            level_str = self._colorize("DEBUG", ColorCodes.GRAY)
            message_color = ColorCodes.GRAY
        elif level == LogLevel.INFO:
            level_str = self._colorize("INFO ", ColorCodes.BLUE)
            message_color = ""
        elif level == LogLevel.WARNING:
            level_str = self._colorize("WARN ", ColorCodes.YELLOW)
            message_color = ColorCodes.YELLOW
        elif level == LogLevel.ERROR:
            level_str = self._colorize("ERROR", ColorCodes.RED)
            message_color = ColorCodes.RED
        elif level == LogLevel.CRITICAL:
            level_str = self._colorize("CRIT ", ColorCodes.BG_RED + ColorCodes.WHITE)
            message_color = ColorCodes.RED
        else:
            level_str = "INFO "
            message_color = ""
        
        # Format timestamp
        time_str = self._colorize(f"[{timestamp}]", ColorCodes.DIM)
        
        # Apply message color
        colored_message = self._colorize(message, message_color) if message_color else message
        
        # Combine with prefix if provided
        full_message = f"{prefix}{colored_message}" if prefix else colored_message
        
        return f"{time_str} {level_str} {full_message}"
    
    def debug(self, message: str):
        """Log a debug message (only shown in verbose mode)"""
        if self.verbose:
            formatted = self._format_message(LogLevel.DEBUG, message)
            print(formatted)
        
        # Always log to file
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log an info message"""
        formatted = self._format_message(LogLevel.INFO, message)
        print(formatted)
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log a warning message"""
        formatted = self._format_message(LogLevel.WARNING, message)
        print(formatted)
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log an error message"""
        formatted = self._format_message(LogLevel.ERROR, message)
        print(formatted)
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log a critical message"""
        formatted = self._format_message(LogLevel.CRITICAL, message)
        print(formatted)
        self.logger.critical(message)
    
    def success(self, message: str):
        """Log a success message (special case of info with green color)"""
        success_symbol = self._colorize("✅", ColorCodes.GREEN)
        colored_message = self._colorize(message, ColorCodes.GREEN)
        formatted = self._format_message(LogLevel.INFO, f"{success_symbol} {colored_message}")
        print(formatted)
        self.logger.info(f"SUCCESS: {message}")
    
    def failure(self, message: str):
        """Log a failure message (special case of error with red color)"""
        failure_symbol = self._colorize("❌", ColorCodes.RED)
        colored_message = self._colorize(message, ColorCodes.RED)
        formatted = self._format_message(LogLevel.ERROR, f"{failure_symbol} {colored_message}")
        print(formatted)
        self.logger.error(f"FAILURE: {message}")
    
    def step(self, message: str):
        """Log a step in a process"""
        step_symbol = self._colorize("🔄", ColorCodes.CYAN)
        formatted = self._format_message(LogLevel.INFO, f"{step_symbol} {message}")
        print(formatted)
        self.logger.info(f"STEP: {message}")
    
    def separator(self, char: str = "-", length: int = 50):
        """Print a separator line"""
        separator = char * length
        formatted = self._format_message(LogLevel.INFO, separator)
        print(formatted)
        self.logger.info(separator)
    
    def log_script_output(self, script_name: str, stdout: str = "", stderr: str = "", return_code: int = 0):
        """
        Log the output from a script execution
        
        Args:
            script_name: Name of the script that was executed
            stdout: Standard output from the script
            stderr: Standard error from the script
            return_code: Return code from the script execution
        """
        self.debug(f"Script '{script_name}' executed with return code: {return_code}")
        
        if stdout and stdout.strip():
            self.debug(f"Script '{script_name}' STDOUT:")
            for line in stdout.strip().split('\n'):
                self.debug(f"  {line}")
        
        if stderr and stderr.strip():
            if return_code == 0:
                self.debug(f"Script '{script_name}' STDERR (non-fatal):")
                for line in stderr.strip().split('\n'):
                    self.debug(f"  {line}")
            else:
                self.error(f"Script '{script_name}' STDERR:")
                for line in stderr.strip().split('\n'):
                    self.error(f"  {line}")
    
    def create_progress_indicator(self, message: str) -> ProgressIndicator:
        """Create a progress indicator for long-running operations"""
        return ProgressIndicator(message, self)
    
    def log_summary(self, total_items: int, successful: int, failed: int, skipped: int):
        """Log a summary of operations"""
        duration = datetime.now() - self.start_time
        
        self.separator("=", 60)
        self.info("OPERATION SUMMARY")
        self.separator("=", 60)
        
        self.info(f"Total items processed: {total_items}")
        self.success(f"Successful operations: {successful}")
        if failed > 0:
            self.failure(f"Failed operations: {failed}")
        else:
            self.info(f"Failed operations: {failed}")
        self.info(f"Skipped operations: {skipped}")
        
        self.separator()
        self.info(f"Total duration: {duration.total_seconds():.2f} seconds")
        self.info(f"Log file: {self.log_file}")
        self.separator("=", 60)
    
    def close(self):
        """Close the logger and clean up resources"""
        session_end = datetime.now()
        duration = session_end - self.start_time
        
        self.info("="*60)
        self.info(f"MacSnap Setup session ended at {session_end.strftime('%Y-%m-%d %H:%M:%S')}")
        self.info(f"Session duration: {duration.total_seconds():.2f} seconds")
        self.info("="*60)
        
        # Close all handlers
        for handler in self.logger.handlers:
            handler.close()
        self.logger.handlers.clear()


# Global logger instance (initialized when needed)
_global_logger: Optional[MacSnapLogger] = None

def get_logger(verbose: bool = False) -> MacSnapLogger:
    """Get or create the global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = MacSnapLogger(verbose=verbose)
    return _global_logger

def set_verbose_mode(verbose: bool):
    """Enable or disable verbose mode for the global logger"""
    global _global_logger
    if _global_logger is not None:
        _global_logger.verbose = verbose
        _global_logger._setup_logging()

def close_logger():
    """Close and cleanup the global logger"""
    global _global_logger
    if _global_logger is not None:
        _global_logger.close()
        _global_logger = None 