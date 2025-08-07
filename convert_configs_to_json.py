#!/usr/bin/env python3
"""
Script to convert all YAML configuration files to separate JSON files.
This script uses the existing ConfigLoader utility to generate 5 JSON files:
1. metadata.json - General information and statistics
2. categories.json - List of categories with id, name and count (excluding special configs)
3. programs.json - List of all programs/applications (excluding _*.yml files)
4. special-configs.json - Special configurations from _*.yml files only
5. tags.json - All unique tags from programs with usage counts (excluding special configs)

Output directory: web/src/assets/data/ (recreated on each run)
Files starting with _*.yml are treated as special configs and excluded from main listings.
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the tui directory to the Python path to import utilities
sys.path.append(str(Path(__file__).parent / "tui"))

from utils.config_loader import ConfigLoader
from constants import get_configs_path

def generate_metadata(loader: ConfigLoader) -> Dict[str, Any]:
    """Generate metadata JSON structure."""
    stats = loader.get_stats()
    return {
        "generated_at": datetime.now().isoformat(),
        "description": "MacSnap configuration database - converted from YAML files",
        "version": "1.0.0",
        "total_configs": stats['total_items'],
        "total_categories": stats['total_categories'],
        "selected_by_default": stats['selected_by_default'],
        "items_by_type": stats['items_by_type'],
        "items_by_category": stats['items_by_category'],
        "categories": stats['categories']
    }

def generate_categories(loader: ConfigLoader) -> Dict[str, Any]:
    """Generate categories JSON structure with id, name and count (excluding special configs)."""
    categories = []
    
    for category in loader.get_categories():
        # Skip the "Special" category
        if category == "Special":
            continue
            
        # Generate a simple id from the category name (lowercase, replace spaces with hyphens)
        category_id = category.lower().replace(' ', '-').replace('&', 'and')
        items = loader.get_items_by_category(category)
        categories.append({
            "id": category_id,
            "name": category,
            "count": len(items)
        })
    
    return {
        "metadata": {
            "total_categories": len(categories),
            "generated_at": datetime.now().isoformat()
        },
        "categories": categories
    }

def generate_programs(loader: ConfigLoader) -> Dict[str, Any]:
    """Generate programs JSON structure (excluding special _*.yml files)."""
    programs = {}
    
    for item_id, item in loader.configurations.items():
        # Skip special configurations (those with category "Special" from _*.yml files)
        if item.category == "Special":
            continue
            
        programs[item_id] = {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "type": item.type,
            "category": item.category,
            "selected_by_default": item.selected_by_default,
            "requires_license": item.requires_license,
            "tags": item.tags,
            "url": item.url,
            "notes": item.notes,
            "dependencies": item.dependencies,
            "install_script": item.install_script,
            "validate_script": item.validate_script,
            "configure_script": item.configure_script,
            "uninstall_script": item.uninstall_script
        }
    
    return {
        "metadata": {
            "total_programs": len(programs),
            "generated_at": datetime.now().isoformat(),
            "description": "MacSnap programs and applications database"
        },
        "programs": programs
    }

def generate_special_configs(loader: ConfigLoader) -> Dict[str, Any]:
    """Generate special configurations JSON structure (from _*.yml files)."""
    special_configs = {}
    
    for item_id, item in loader.configurations.items():
        # Only include special configurations (those with category "Special" from _*.yml files)
        if item.category != "Special":
            continue
            
        special_configs[item_id] = {
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "type": item.type,
            "category": item.category,
            "tags": item.tags,
            "notes": item.notes,
            "dependencies": item.dependencies,
            "install_script": item.install_script,
            "validate_script": item.validate_script,
            "configure_script": item.configure_script,
            "uninstall_script": item.uninstall_script,
            "file_path": item.file_path
        }
    
    return {
        "metadata": {
            "total_special_configs": len(special_configs),
            "generated_at": datetime.now().isoformat(),
            "description": "MacSnap special configurations from _*.yml files"
        },
        "special_configs": special_configs
    }

def generate_tags(loader: ConfigLoader) -> Dict[str, Any]:
    """Generate tags JSON structure with all unique tags from programs (excluding special configs)."""
    tags_set = set()
    tag_counts = {}
    
    # Collect all tags from configurations (excluding special ones)
    for item in loader.configurations.values():
        # Skip special configurations
        if item.category == "Special":
            continue
            
        if item.tags:
            for tag in item.tags:
                tags_set.add(tag)
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Create sorted list of tags with counts
    tags_list = []
    for tag in sorted(tags_set):
        tags_list.append({
            "name": tag,
            "count": tag_counts[tag]
        })
    
    return {
        "metadata": {
            "total_tags": len(tags_list),
            "generated_at": datetime.now().isoformat(),
            "description": "All tags used across MacSnap programs"
        },
        "tags": tags_list
    }

def write_json_file(data: Dict[str, Any], file_path: Path, description: str) -> None:
    """Write data to a JSON file with error handling."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        file_size = file_path.stat().st_size
        print(f"✅ {description}")
        print(f"   📄 File: {file_path.name}")
        print(f"   📊 Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error writing {description}: {e}")

def main():
    """Main function to convert YAML configs to separate JSON files."""
    print("🔄 Converting YAML configurations to separate JSON files...")
    
    # Define paths
    script_dir = Path(__file__).parent
    web_data_dir = script_dir / "web" / "src" / "assets" / "data"
    
    # Remove and recreate the data directory to start fresh
    if web_data_dir.exists():
        print(f"🗑️  Removing existing data directory: {web_data_dir}")
        shutil.rmtree(web_data_dir)
    
    print(f"📁 Creating data directory: {web_data_dir}")
    web_data_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load configurations using the existing ConfigLoader
        print("📁 Loading configurations...")
        configs_path = get_configs_path()
        loader = ConfigLoader(str(configs_path))
        loader.load_configurations()
        
        print(f"✅ Loaded {len(loader.configurations)} configurations")
        print(f"📂 Found {len(loader.get_categories())} categories")
        
        # Generate and write each JSON file
        print("\n🔄 Generating JSON files...")
        
        # 1. Metadata
        metadata = generate_metadata(loader)
        write_json_file(metadata, web_data_dir / "metadata.json", "Generated metadata.json")
        
        # 2. Categories
        categories = generate_categories(loader)
        write_json_file(categories, web_data_dir / "categories.json", "Generated categories.json")
        
        # 3. Programs
        programs = generate_programs(loader)
        write_json_file(programs, web_data_dir / "programs.json", "Generated programs.json")
        
        # 4. Special Configurations (from _*.yml files)
        special_configs = generate_special_configs(loader)
        write_json_file(special_configs, web_data_dir / "special-configs.json", "Generated special-configs.json")
        
        # 5. Tags
        tags = generate_tags(loader)
        write_json_file(tags, web_data_dir / "tags.json", "Generated tags.json")
        
        # Summary
        print(f"\n🎉 Successfully generated 5 JSON files!")
        print(f"📊 Summary:")
        print(f"   • Total configurations: {metadata['total_configs']}")
        print(f"   • Programs: {programs['metadata']['total_programs']}")
        print(f"   • Special configs: {special_configs['metadata']['total_special_configs']}")
        print(f"   • Categories: {len(categories['categories'])}")
        print(f"   • Tags: {tags['metadata']['total_tags']}")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
