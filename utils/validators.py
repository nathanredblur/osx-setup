"""
Configuration Validator for MacSnap Setup.

This module handles:
- YAML schema validation (required fields, structure)
- Type validation (valid installation types)
- Script validation (required scripts based on item type)
- Dependency validation and circular dependency detection
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass
from .config_loader import ConfigItem


@dataclass
class ValidationError:
    """Represents a validation error with context."""
    item_id: str
    field: str
    error_type: str
    message: str
    severity: str = "error"  # "error", "warning", "info"


class ConfigValidator:
    """Validates configuration items and their relationships."""
    
    # Valid installation types
    VALID_TYPES = {
        'brew',
        'brew_cask', 
        'mas',
        'direct_download_dmg',
        'direct_download_pkg',
        'proto_tool',
        'system_config',
        'launch_agent',
        'shell_script'
    }
    
    # Required fields for all configurations
    REQUIRED_FIELDS = {'id', 'name', 'type', 'category'}
    
    # Optional fields
    OPTIONAL_FIELDS = {
        'description', 'selected_by_default', 'dependencies',
        'install', 'validate', 'configure', 'uninstall'
    }
    
    # Script requirements by type
    SCRIPT_REQUIREMENTS = {
        'brew': {'install': True, 'validate': False, 'configure': False, 'uninstall': False},
        'brew_cask': {'install': True, 'validate': False, 'configure': False, 'uninstall': False},
        'mas': {'install': True, 'validate': False, 'configure': False, 'uninstall': False},
        'direct_download_dmg': {'install': True, 'validate': True, 'configure': False, 'uninstall': False},
        'direct_download_pkg': {'install': True, 'validate': True, 'configure': False, 'uninstall': False},
        'proto_tool': {'install': True, 'validate': False, 'configure': False, 'uninstall': False},
        'system_config': {'install': False, 'validate': False, 'configure': True, 'uninstall': False},
        'launch_agent': {'install': True, 'validate': True, 'configure': False, 'uninstall': True},
        'shell_script': {'install': True, 'validate': False, 'configure': False, 'uninstall': False}
    }
    
    def __init__(self):
        """Initialize the validator."""
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate_all(self, configurations: Dict[str, ConfigItem]) -> Tuple[List[ValidationError], List[ValidationError]]:
        """
        Validate all configurations comprehensively.
        
        Args:
            configurations: Dictionary of configuration items
            
        Returns:
            Tuple of (errors, warnings)
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Validate individual items
        for item_id, item in configurations.items():
            self._validate_single_item(item)
        
        # Validate dependencies
        self._validate_dependencies(configurations)
        
        # Check for circular dependencies
        self._detect_circular_dependencies(configurations)
        
        return self.errors, self.warnings
    
    def _validate_single_item(self, item: ConfigItem) -> None:
        """
        Validate a single configuration item.
        
        Args:
            item: Configuration item to validate
        """
        # Schema validation
        self._validate_schema(item)
        
        # Type validation
        self._validate_type(item)
        
        # Script validation
        self._validate_scripts(item)
        
        # Field format validation
        self._validate_field_formats(item)
    
    def _validate_schema(self, item: ConfigItem) -> None:
        """
        Validate basic schema requirements.
        
        Args:
            item: Configuration item to validate
        """
        # Check required fields are not empty
        if not item.id or not item.id.strip():
            self._add_error(item.id or "unknown", "id", "missing", "ID field is required and cannot be empty")
        
        if not item.name or not item.name.strip():
            self._add_error(item.id, "name", "missing", "Name field is required and cannot be empty")
        
        if not item.type or not item.type.strip():
            self._add_error(item.id, "type", "missing", "Type field is required and cannot be empty")
        
        if not item.category or not item.category.strip():
            self._add_error(item.id, "category", "missing", "Category field is required and cannot be empty")
    
    def _validate_type(self, item: ConfigItem) -> None:
        """
        Validate the type field contains a valid installation type.
        
        Args:
            item: Configuration item to validate
        """
        if item.type and item.type not in self.VALID_TYPES:
            self._add_error(
                item.id, 
                "type", 
                "invalid_value",
                f"Invalid type '{item.type}'. Valid types are: {', '.join(sorted(self.VALID_TYPES))}"
            )
    
    def _validate_scripts(self, item: ConfigItem) -> None:
        """
        Validate script requirements based on item type.
        
        Args:
            item: Configuration item to validate
        """
        if item.type not in self.SCRIPT_REQUIREMENTS:
            return
        
        requirements = self.SCRIPT_REQUIREMENTS[item.type]
        
        # Check required scripts
        for script_type, required in requirements.items():
            script_content = getattr(item, f"{script_type}_script", None)
            
            if required and (not script_content or not script_content.strip()):
                self._add_error(
                    item.id,
                    f"{script_type}_script",
                    "missing_required",
                    f"Type '{item.type}' requires a '{script_type}' script"
                )
            elif script_content and script_content.strip() and not required:
                self._add_warning(
                    item.id,
                    f"{script_type}_script",
                    "unnecessary",
                    f"Type '{item.type}' typically doesn't need a '{script_type}' script"
                )
    
    def _validate_field_formats(self, item: ConfigItem) -> None:
        """
        Validate field formats and values.
        
        Args:
            item: Configuration item to validate
        """
        # Validate ID format (should be alphanumeric with underscores/hyphens)
        if item.id and not self._is_valid_id(item.id):
            self._add_error(
                item.id,
                "id",
                "invalid_format",
                "ID should contain only letters, numbers, underscores, and hyphens"
            )
        
        # Validate dependencies format
        if item.dependencies:
            for dep_id in item.dependencies:
                if not dep_id or not dep_id.strip():
                    self._add_error(
                        item.id,
                        "dependencies",
                        "invalid_format",
                        "Dependencies cannot contain empty values"
                    )
                elif not self._is_valid_id(dep_id):
                    self._add_error(
                        item.id,
                        "dependencies",
                        "invalid_format",
                        f"Dependency ID '{dep_id}' has invalid format"
                    )
        
        # Validate category format
        if item.category and not self._is_valid_category(item.category):
            self._add_warning(
                item.id,
                "category",
                "format_suggestion",
                "Category should use title case (e.g., 'Development Tools')"
            )
    
    def _validate_dependencies(self, configurations: Dict[str, ConfigItem]) -> None:
        """
        Validate that all dependencies reference existing items.
        
        Args:
            configurations: All configuration items
        """
        for item_id, item in configurations.items():
            for dep_id in item.dependencies:
                if dep_id not in configurations:
                    self._add_error(
                        item_id,
                        "dependencies",
                        "missing_reference",
                        f"Dependency '{dep_id}' does not exist"
                    )
    
    def _detect_circular_dependencies(self, configurations: Dict[str, ConfigItem]) -> None:
        """
        Detect circular dependencies in the configuration graph.
        
        Args:
            configurations: All configuration items
        """
        # Use DFS to detect cycles
        visited = set()
        rec_stack = set()
        
        def has_cycle(item_id: str, path: List[str]) -> bool:
            if item_id in rec_stack:
                # Found a cycle - find the cycle in the path
                cycle_start = path.index(item_id)
                cycle = path[cycle_start:] + [item_id]
                self._add_error(
                    item_id,
                    "dependencies",
                    "circular_dependency",
                    f"Circular dependency detected: {' -> '.join(cycle)}"
                )
                return True
            
            if item_id in visited:
                return False
            
            visited.add(item_id)
            rec_stack.add(item_id)
            
            item = configurations.get(item_id)
            if item:
                for dep_id in item.dependencies:
                    if dep_id in configurations:  # Only check valid dependencies
                        if has_cycle(dep_id, path + [item_id]):
                            return True
            
            rec_stack.remove(item_id)
            return False
        
        # Check each item for cycles
        for item_id in configurations:
            if item_id not in visited:
                has_cycle(item_id, [])
    
    def _is_valid_id(self, item_id: str) -> bool:
        """
        Check if an ID has valid format.
        
        Args:
            item_id: ID to validate
            
        Returns:
            True if valid format
        """
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', item_id))
    
    def _is_valid_category(self, category: str) -> bool:
        """
        Check if a category follows recommended format.
        
        Args:
            category: Category to validate
            
        Returns:
            True if follows title case format
        """
        # Check if it's title case
        return category == category.title() and not category.isupper() and not category.islower()
    
    def _add_error(self, item_id: str, field: str, error_type: str, message: str) -> None:
        """Add a validation error."""
        self.errors.append(ValidationError(item_id, field, error_type, message, "error"))
    
    def _add_warning(self, item_id: str, field: str, error_type: str, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(ValidationError(item_id, field, error_type, message, "warning"))
    
    def get_dependency_order(self, configurations: Dict[str, ConfigItem]) -> List[str]:
        """
        Get the correct installation order based on dependencies.
        
        Args:
            configurations: All configuration items
            
        Returns:
            List of item IDs in dependency order
            
        Raises:
            ValueError: If circular dependencies exist
        """
        # First validate dependencies
        errors, _ = self.validate_all(configurations)
        circular_errors = [e for e in errors if e.error_type == "circular_dependency"]
        
        if circular_errors:
            raise ValueError(f"Cannot determine order due to circular dependencies: {circular_errors[0].message}")
        
        # Topological sort
        visited = set()
        temp_mark = set()
        result = []
        
        def visit(item_id: str):
            if item_id in temp_mark:
                return  # Skip if already processing (shouldn't happen after circular check)
            if item_id in visited:
                return
            
            temp_mark.add(item_id)
            
            item = configurations.get(item_id)
            if item:
                for dep_id in item.dependencies:
                    if dep_id in configurations:
                        visit(dep_id)
            
            temp_mark.remove(item_id)
            visited.add(item_id)
            result.append(item_id)
        
        # Visit all nodes
        for item_id in configurations:
            if item_id not in visited:
                visit(item_id)
        
        return result
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of validation results.
        
        Returns:
            Dictionary with validation summary
        """
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors_by_type": self._group_by_type(self.errors),
            "warnings_by_type": self._group_by_type(self.warnings),
            "errors_by_item": self._group_by_item(self.errors),
            "warnings_by_item": self._group_by_item(self.warnings),
            "is_valid": len(self.errors) == 0
        }
    
    def _group_by_type(self, issues: List[ValidationError]) -> Dict[str, int]:
        """Group validation issues by error type."""
        groups = {}
        for issue in issues:
            groups[issue.error_type] = groups.get(issue.error_type, 0) + 1
        return groups
    
    def _group_by_item(self, issues: List[ValidationError]) -> Dict[str, int]:
        """Group validation issues by item ID."""
        groups = {}
        for issue in issues:
            groups[issue.item_id] = groups.get(issue.item_id, 0) + 1
        return groups


# Convenience function for quick validation
def validate_configs(configurations: Dict[str, ConfigItem]) -> Tuple[List[ValidationError], List[ValidationError]]:
    """
    Quick function to validate configurations.
    
    Args:
        configurations: Dictionary of configuration items
        
    Returns:
        Tuple of (errors, warnings)
    """
    validator = ConfigValidator()
    return validator.validate_all(configurations) 