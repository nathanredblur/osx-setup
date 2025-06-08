"""
Configuration Loader for MacSnap Setup.

This module handles:
- Recursive scanning of configs/ directory for .yml files
- YAML parsing and configuration object creation
- Category extraction for UI organization
- Environment variable setup for script execution
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass


@dataclass
class ConfigItem:
    """Represents a single configuration item from a YAML file."""
    id: str
    name: str
    description: str
    type: str
    category: str
    selected_by_default: bool = False
    dependencies: List[str] = None
    install_script: Optional[str] = None
    validate_script: Optional[str] = None
    configure_script: Optional[str] = None
    uninstall_script: Optional[str] = None
    file_path: str = ""
    config_dir: str = ""  # Directory containing the YAML file
    
    def __post_init__(self):
        """Initialize dependencies as empty list if None."""
        if self.dependencies is None:
            self.dependencies = []


class ConfigLoader:
    """Loads and manages configuration files from the configs/ directory."""
    
    def __init__(self, configs_dir: str = "configs"):
        """
        Initialize the ConfigLoader.
        
        Args:
            configs_dir: Path to the configs directory (relative or absolute)
        """
        self.configs_dir = Path(configs_dir).resolve()
        self.configurations: Dict[str, ConfigItem] = {}
        self.categories: Set[str] = set()
        
    def load_configurations(self) -> Dict[str, ConfigItem]:
        """
        Load all configuration files from the configs directory recursively.
        
        Returns:
            Dictionary mapping item IDs to ConfigItem objects
            
        Raises:
            FileNotFoundError: If configs directory doesn't exist
            yaml.YAMLError: If YAML files are malformed
        """
        if not self.configs_dir.exists():
            raise FileNotFoundError(f"Configs directory not found: {self.configs_dir}")
            
        # Clear existing data
        self.configurations.clear()
        self.categories.clear()
        
        # Recursively find all .yml files
        yml_files = list(self.configs_dir.rglob("*.yml"))
        
        print(f"Found {len(yml_files)} configuration files")
        
        for yml_file in yml_files:
            try:
                config_item = self._load_single_config(yml_file)
                if config_item:
                    # Check for duplicate IDs
                    if config_item.id in self.configurations:
                        print(f"Warning: Duplicate ID '{config_item.id}' found in {yml_file}")
                        print(f"  Previous: {self.configurations[config_item.id].file_path}")
                        continue
                        
                    self.configurations[config_item.id] = config_item
                    self.categories.add(config_item.category)
                    
            except Exception as e:
                print(f"Error loading {yml_file}: {e}")
                continue
                
        print(f"Loaded {len(self.configurations)} valid configurations")
        print(f"Found categories: {sorted(self.categories)}")
        
        return self.configurations
    
    def _load_single_config(self, yml_file: Path) -> Optional[ConfigItem]:
        """
        Load a single YAML configuration file.
        
        Args:
            yml_file: Path to the YAML file
            
        Returns:
            ConfigItem object or None if invalid
        """
        try:
            with open(yml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not data:
                print(f"Warning: Empty YAML file: {yml_file}")
                return None
                
            # Extract required fields
            try:
                config_item = ConfigItem(
                    id=data['id'],
                    name=data['name'],
                    type=data['type'],
                    category=data['category'],
                    description=data.get('description', ''),
                    selected_by_default=data.get('selected_by_default', False),
                    dependencies=data.get('dependencies', []),
                    file_path=str(yml_file),
                    config_dir=str(self.configs_dir)
                )
                
                # Extract script sections
                if 'install' in data and 'script' in data['install']:
                    config_item.install_script = data['install']['script']
                    
                if 'validate' in data and 'script' in data['validate']:
                    config_item.validate_script = data['validate']['script']
                    
                if 'configure' in data and 'script' in data['configure']:
                    config_item.configure_script = data['configure']['script']
                    
                if 'uninstall' in data and 'script' in data['uninstall']:
                    config_item.uninstall_script = data['uninstall']['script']
                
                return config_item
                
            except KeyError as e:
                print(f"Missing required field {e} in {yml_file}")
                return None
                
        except yaml.YAMLError as e:
            print(f"YAML parsing error in {yml_file}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error loading {yml_file}: {e}")
            return None
    
    def get_categories(self) -> List[str]:
        """
        Get all available categories sorted alphabetically.
        
        Returns:
            List of category names
        """
        return sorted(self.categories)
    
    def get_items_by_category(self, category: str) -> List[ConfigItem]:
        """
        Get all configuration items for a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of ConfigItem objects in the category, sorted by name
        """
        items = [
            item for item in self.configurations.values()
            if item.category == category
        ]
        return sorted(items, key=lambda x: x.name)
    
    def get_item_by_id(self, item_id: str) -> Optional[ConfigItem]:
        """
        Get a configuration item by its ID.
        
        Args:
            item_id: Item identifier
            
        Returns:
            ConfigItem object or None if not found
        """
        return self.configurations.get(item_id)
    
    def get_dependencies(self, item_id: str) -> List[str]:
        """
        Get the dependency list for a specific item.
        
        Args:
            item_id: Item identifier
            
        Returns:
            List of dependency IDs
        """
        item = self.get_item_by_id(item_id)
        return item.dependencies if item else []
    
    def get_selected_by_default(self) -> List[ConfigItem]:
        """
        Get all items that should be selected by default.
        
        Returns:
            List of ConfigItem objects marked as selected_by_default
        """
        return [
            item for item in self.configurations.values()
            if item.selected_by_default
        ]
    
    def prepare_script_environment(self, item: ConfigItem) -> Dict[str, str]:
        """
        Prepare environment variables for script execution.
        
        Args:
            item: Configuration item
            
        Returns:
            Dictionary of environment variables
        """
        env = os.environ.copy()
        env['ITEM_CONFIG_DIR'] = item.config_dir
        env['ITEM_ID'] = item.id
        env['ITEM_NAME'] = item.name
        env['ITEM_TYPE'] = item.type
        return env
    
    def validate_dependencies(self) -> List[str]:
        """
        Validate that all dependencies reference existing items.
        
        Returns:
            List of error messages for invalid dependencies
        """
        errors = []
        
        for item_id, item in self.configurations.items():
            for dep_id in item.dependencies:
                if dep_id not in self.configurations:
                    errors.append(
                        f"Item '{item_id}' has invalid dependency '{dep_id}'"
                    )
        
        return errors
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about loaded configurations.
        
        Returns:
            Dictionary with configuration statistics
        """
        stats = {
            'total_items': len(self.configurations),
            'total_categories': len(self.categories),
            'categories': list(self.categories),
            'selected_by_default': len(self.get_selected_by_default()),
            'items_by_type': {},
            'items_by_category': {}
        }
        
        # Count by type
        for item in self.configurations.values():
            item_type = item.type
            stats['items_by_type'][item_type] = stats['items_by_type'].get(item_type, 0) + 1
            
        # Count by category
        for category in self.categories:
            stats['items_by_category'][category] = len(self.get_items_by_category(category))
            
        return stats


# Convenience function for quick loading
def load_configs(configs_dir: str = "configs") -> ConfigLoader:
    """
    Quick function to load configurations.
    
    Args:
        configs_dir: Path to configs directory
        
    Returns:
        ConfigLoader instance with configurations loaded
    """
    loader = ConfigLoader(configs_dir)
    loader.load_configurations()
    return loader 