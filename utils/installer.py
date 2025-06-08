"""
Installation Engine for MacSnap Setup.

This module handles:
- Script execution with proper environment setup
- Dependency resolution and correct installation order
- Installation, validation, configuration, and uninstallation functions
- Batch processing for multiple items
- Error handling and recovery
- Type-specific installation handlers
"""

import os
import subprocess
import tempfile
from typing import Dict, List, Set, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .config_loader import ConfigItem
from .validators import ConfigValidator
from .logger import get_logger


class OperationResult(Enum):
    """Result status for operations."""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ALREADY_INSTALLED = "already_installed"


@dataclass
class ExecutionResult:
    """Result of a script execution."""
    operation: str
    item_id: str
    result: OperationResult
    return_code: int
    stdout: str
    stderr: str
    duration: float
    error_message: Optional[str] = None


class InstallationEngine:
    """Handles installation, configuration, and management of software items."""
    
    def __init__(self, verbose: bool = False):
        """
        Initialize the installation engine.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.results: List[ExecutionResult] = []
        self.validator = ConfigValidator()
        self.logger = get_logger(verbose=verbose)
        
        # Track installation state
        self.installed_items: Set[str] = set()
        self.failed_items: Set[str] = set()
        self.skipped_items: Set[str] = set()
    
    def check_install_status(self, item: ConfigItem) -> ExecutionResult:
        """
        Check if an item is already installed using its validate script.
        
        Args:
            item: Configuration item to check
            
        Returns:
            ExecutionResult with validation status
        """
        if not item.validate_script:
            # No validation script means we assume it's not installed
            return ExecutionResult(
                operation="validate",
                item_id=item.id,
                result=OperationResult.FAILED,
                return_code=1,
                stdout="",
                stderr="No validation script provided",
                duration=0.0
            )
        
        self.logger.debug(f"Checking installation status for {item.name}...")
        return self._execute_script(item, "validate", item.validate_script)
    
    def install_item(self, item: ConfigItem) -> ExecutionResult:
        """
        Install an item using its install script.
        
        Args:
            item: Configuration item to install
            
        Returns:
            ExecutionResult with installation status
        """
        if not item.install_script:
            return ExecutionResult(
                operation="install",
                item_id=item.id,
                result=OperationResult.FAILED,
                return_code=1,
                stdout="",
                stderr="No installation script provided",
                duration=0.0,
                error_message="Missing install script"
            )
        
        self.logger.step(f"Installing {item.name}...")
        result = self._execute_script(item, "install", item.install_script)
        
        if result.result == OperationResult.SUCCESS:
            self.installed_items.add(item.id)
        else:
            self.failed_items.add(item.id)
        
        return result
    
    def configure_item(self, item: ConfigItem) -> ExecutionResult:
        """
        Configure an item using its configure script.
        
        Args:
            item: Configuration item to configure
            
        Returns:
            ExecutionResult with configuration status
        """
        if not item.configure_script:
            return ExecutionResult(
                operation="configure",
                item_id=item.id,
                result=OperationResult.SKIPPED,
                return_code=0,
                stdout="",
                stderr="No configuration script provided",
                duration=0.0
            )
        
        self.logger.step(f"Configuring {item.name}...")
        return self._execute_script(item, "configure", item.configure_script)
    
    def uninstall_item(self, item: ConfigItem) -> ExecutionResult:
        """
        Uninstall an item using its uninstall script.
        
        Args:
            item: Configuration item to uninstall
            
        Returns:
            ExecutionResult with uninstallation status
        """
        if not item.uninstall_script:
            return ExecutionResult(
                operation="uninstall",
                item_id=item.id,
                result=OperationResult.SKIPPED,
                return_code=0,
                stdout="",
                stderr="No uninstallation script provided",
                duration=0.0
            )
        
        self.logger.step(f"Uninstalling {item.name}...")
        result = self._execute_script(item, "uninstall", item.uninstall_script)
        
        if result.result == OperationResult.SUCCESS:
            self.installed_items.discard(item.id)
        
        return result
    
    def batch_process(self, 
                     configurations: Dict[str, ConfigItem], 
                     selected_items: List[str],
                     operation: str = "install") -> List[ExecutionResult]:
        """
        Process multiple items in correct dependency order.
        
        Args:
            configurations: All available configurations
            selected_items: List of item IDs to process
            operation: Operation to perform ("install", "uninstall", "configure")
            
        Returns:
            List of ExecutionResults for all processed items
        """
        self.logger.info(f"Starting batch {operation} for {len(selected_items)} items...")
        
        # Validate configurations first
        errors, warnings = self.validator.validate_all(configurations)
        if errors:
            self.logger.error(f"Configuration errors found: {len(errors)}")
            for error in errors:
                self.logger.error(f"  - {error.item_id}.{error.field}: {error.message}")
            return []
        
        # Get dependency order
        try:
            dependency_order = self.validator.get_dependency_order(configurations)
        except ValueError as e:
            self.logger.error(f"Cannot determine dependency order: {e}")
            return []
        
        # Filter to only selected items and their dependencies
        items_to_process = self._resolve_dependencies(
            configurations, selected_items, dependency_order
        )
        
        self.logger.info(f"Processing {len(items_to_process)} items in dependency order...")
        
        results = []
        
        for item_id in items_to_process:
            if item_id not in configurations:
                continue
                
            item = configurations[item_id]
            
            # Check if dependencies are satisfied
            if not self._dependencies_satisfied(item, configurations):
                result = ExecutionResult(
                    operation=operation,
                    item_id=item_id,
                    result=OperationResult.SKIPPED,
                    return_code=0,
                    stdout="",
                    stderr="Dependencies not satisfied",
                    duration=0.0,
                    error_message="Skipped due to failed dependencies"
                )
                results.append(result)
                self.skipped_items.add(item_id)
                continue
            
            # Perform the operation
            try:
                if operation == "install":
                    result = self._handle_install_operation(item)
                elif operation == "uninstall":
                    result = self.uninstall_item(item)
                elif operation == "configure":
                    result = self.configure_item(item)
                else:
                    raise ValueError(f"Unknown operation: {operation}")
                
                results.append(result)
                self.results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing {item.name}: {e}")
                result = ExecutionResult(
                    operation=operation,
                    item_id=item_id,
                    result=OperationResult.FAILED,
                    return_code=1,
                    stdout="",
                    stderr=str(e),
                    duration=0.0,
                    error_message=str(e)
                )
                results.append(result)
                self.failed_items.add(item_id)
        
        self.logger.info(f"Batch {operation} completed. Results: {self._get_results_summary(results)}")
        return results
    
    def _handle_install_operation(self, item: ConfigItem) -> ExecutionResult:
        """
        Handle the full install operation: validate -> install -> configure.
        
        Args:
            item: Configuration item to install
            
        Returns:
            ExecutionResult for the overall operation
        """
        # Check if already installed
        validate_result = self.check_install_status(item)
        if validate_result.result == OperationResult.SUCCESS:
            self.logger.debug(f"{item.name} is already installed, skipping installation")
            return ExecutionResult(
                operation="install",
                item_id=item.id,
                result=OperationResult.ALREADY_INSTALLED,
                return_code=0,
                stdout=validate_result.stdout,
                stderr="Already installed",
                duration=validate_result.duration
            )
        
        # Install the item
        install_result = self.install_item(item)
        if install_result.result != OperationResult.SUCCESS:
            return install_result
        
        # Configure if configuration script exists
        if item.configure_script:
            configure_result = self.configure_item(item)
            # Return configure result if it failed, otherwise return install result
            if configure_result.result != OperationResult.SUCCESS:
                return configure_result
        
        return install_result
    
    def _resolve_dependencies(self, 
                            configurations: Dict[str, ConfigItem],
                            selected_items: List[str],
                            dependency_order: List[str]) -> List[str]:
        """
        Resolve dependencies for selected items.
        
        Args:
            configurations: All configurations
            selected_items: Items selected by user
            dependency_order: Global dependency order
            
        Returns:
            List of item IDs to process including dependencies
        """
        items_needed = set(selected_items)
        
        # Add all dependencies recursively
        def add_dependencies(item_id: str):
            if item_id in configurations:
                item = configurations[item_id]
                for dep_id in item.dependencies:
                    if dep_id not in items_needed:
                        items_needed.add(dep_id)
                        add_dependencies(dep_id)
        
        for item_id in selected_items:
            add_dependencies(item_id)
        
        # Return in dependency order
        return [item_id for item_id in dependency_order if item_id in items_needed]
    
    def _dependencies_satisfied(self, 
                               item: ConfigItem, 
                               configurations: Dict[str, ConfigItem]) -> bool:
        """
        Check if all dependencies for an item are satisfied.
        
        Args:
            item: Item to check
            configurations: All configurations
            
        Returns:
            True if all dependencies are satisfied
        """
        for dep_id in item.dependencies:
            if dep_id in self.failed_items or dep_id in self.skipped_items:
                return False
        return True
    
    def _execute_script(self, 
                       item: ConfigItem, 
                       operation: str, 
                       script_content: str) -> ExecutionResult:
        """
        Execute a script with proper environment setup.
        
        Args:
            item: Configuration item
            operation: Operation name (install, validate, configure, uninstall)
            script_content: Script content to execute
            
        Returns:
            ExecutionResult with execution details
        """
        import time
        start_time = time.time()
        
        try:
            # Prepare environment
            env = self._prepare_environment(item)
            
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write("#!/bin/bash\n")
                f.write("set -e\n")  # Exit on error
                f.write(script_content)
                script_path = f.name
            
            try:
                # Make script executable
                os.chmod(script_path, 0o755)
                
                # Execute script
                result = subprocess.run(
                    ['/bin/bash', script_path],
                    env=env,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                duration = time.time() - start_time
                
                # Log script output using our logger
                self.logger.log_script_output(
                    f"{item.id}.{operation}",
                    stdout=result.stdout,
                    stderr=result.stderr,
                    return_code=result.returncode
                )
                
                # Determine result status
                if result.returncode == 0:
                    operation_result = OperationResult.SUCCESS
                else:
                    operation_result = OperationResult.FAILED
                
                return ExecutionResult(
                    operation=operation,
                    item_id=item.id,
                    result=operation_result,
                    return_code=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    duration=duration
                )
                
            finally:
                # Clean up temporary script
                try:
                    os.unlink(script_path)
                except OSError:
                    pass
                    
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ExecutionResult(
                operation=operation,
                item_id=item.id,
                result=OperationResult.FAILED,
                return_code=124,  # Timeout exit code
                stdout="",
                stderr="Script execution timed out after 5 minutes",
                duration=duration,
                error_message="Execution timeout"
            )
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                operation=operation,
                item_id=item.id,
                result=OperationResult.FAILED,
                return_code=1,
                stdout="",
                stderr=str(e),
                duration=duration,
                error_message=str(e)
            )
    
    def _prepare_environment(self, item: ConfigItem) -> Dict[str, str]:
        """
        Prepare environment variables for script execution.
        
        Args:
            item: Configuration item
            
        Returns:
            Environment variables dictionary
        """
        env = os.environ.copy()
        
        # Add MacSnap-specific variables
        env['ITEM_CONFIG_DIR'] = item.config_dir
        env['ITEM_ID'] = item.id
        env['ITEM_NAME'] = item.name
        env['ITEM_TYPE'] = item.type
        env['ITEM_CATEGORY'] = item.category
        
        # Add PATH to ensure tools like brew are available
        if '/opt/homebrew/bin' not in env.get('PATH', ''):
            env['PATH'] = f"/opt/homebrew/bin:/usr/local/bin:{env.get('PATH', '')}"
        
        return env
    
    def _log(self, message: str) -> None:
        """Log a message (deprecated - use self.logger instead)."""
        self.logger.debug(f"[InstallationEngine] {message}")
    
    def _get_results_summary(self, results: List[ExecutionResult]) -> str:
        """Get a summary of operation results."""
        summary = {}
        for result in results:
            summary[result.result.value] = summary.get(result.result.value, 0) + 1
        
        parts = []
        for status, count in summary.items():
            parts.append(f"{count} {status}")
        
        return ", ".join(parts)
    
    def get_installation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all installation operations.
        
        Returns:
            Dictionary with installation statistics
        """
        return {
            "total_operations": len(self.results),
            "installed_items": len(self.installed_items),
            "failed_items": len(self.failed_items),
            "skipped_items": len(self.skipped_items),
            "results_by_operation": self._group_results_by_operation(),
            "results_by_status": self._group_results_by_status(),
            "total_duration": sum(r.duration for r in self.results),
            "failed_item_ids": list(self.failed_items),
            "skipped_item_ids": list(self.skipped_items)
        }
    
    def _group_results_by_operation(self) -> Dict[str, int]:
        """Group results by operation type."""
        groups = {}
        for result in self.results:
            groups[result.operation] = groups.get(result.operation, 0) + 1
        return groups
    
    def _group_results_by_status(self) -> Dict[str, int]:
        """Group results by status."""
        groups = {}
        for result in self.results:
            groups[result.result.value] = groups.get(result.result.value, 0) + 1
        return groups
    
    def clear_results(self) -> None:
        """Clear all results and state."""
        self.results.clear()
        self.installed_items.clear()
        self.failed_items.clear()
        self.skipped_items.clear()


# Convenience functions
def install_items(configurations: Dict[str, ConfigItem], 
                 item_ids: List[str], 
                 verbose: bool = False) -> List[ExecutionResult]:
    """
    Convenience function to install multiple items.
    
    Args:
        configurations: All available configurations
        item_ids: Items to install
        verbose: Enable verbose logging
        
    Returns:
        List of execution results
    """
    engine = InstallationEngine(verbose=verbose)
    return engine.batch_process(configurations, item_ids, "install")


def check_installation_status(configurations: Dict[str, ConfigItem], 
                            item_ids: List[str],
                            verbose: bool = False) -> List[ExecutionResult]:
    """
    Check installation status for multiple items.
    
    Args:
        configurations: All available configurations
        item_ids: Items to check
        verbose: Enable verbose logging
        
    Returns:
        List of execution results
    """
    engine = InstallationEngine(verbose=verbose)
    results = []
    
    for item_id in item_ids:
        if item_id in configurations:
            result = engine.check_install_status(configurations[item_id])
            results.append(result)
    
    return results 