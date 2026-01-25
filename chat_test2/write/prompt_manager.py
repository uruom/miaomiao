"""Prompt Configuration Manager - Loads prompts from configuration files on demand"""

import json
import os
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """Prompt template configuration"""
    name: str
    template: str
    description: str = ""
    version: str = "1.0"
    variables: List[str] = None
    system_prompt: str = ""

    def __post_init__(self):
        if self.variables is None:
            self.variables = self._extract_variables()

    def _extract_variables(self) -> List[str]:
        """Extract variable names from template"""
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, self.template)
        return list(set(variables))

    def format(self, **kwargs) -> str:
        """Format template with provided data"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            formatted = self.template
            for var in self.variables:
                if var not in kwargs:
                    formatted = formatted.replace(f"{{{var}}}", "")
            return formatted
        except Exception as e:
            logger.error(f"Template formatting failed: {e}")
            return self.template


class PromptConfigManager:
    """Prompt configuration manager that loads prompts from files on demand"""

    def __init__(self, config_dir: str = "prompt_configs"):
        self.config_dir = config_dir
        self._templates_cache: Dict[str, PromptTemplate] = {}
        self._loaded_files: set = set()

        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)

    def _load_template_from_file(self, template_name: str) -> Optional[PromptTemplate]:
        """Load a single template from file"""
        file_path = os.path.join(self.config_dir, f"{template_name}.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"Template file not found: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            template = PromptTemplate(**data)
            self._templates_cache[template_name] = template
            self._loaded_files.add(file_path)
            logger.info(f"Loaded template: {template_name}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            return None

    def _load_all_templates(self):
        """Load all templates from config directory"""
        if not os.path.exists(self.config_dir):
            logger.warning(f"Config directory not found: {self.config_dir}")
            return
        
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                template_name = filename[:-5]  # Remove .json extension
                if template_name not in self._templates_cache:
                    self._load_template_from_file(template_name)

    def get_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Get template by name, loading it if not already cached"""
        if template_name in self._templates_cache:
            return self._templates_cache[template_name]
        
        # Try to load from file
        template = self._load_template_from_file(template_name)
        if template:
            return template
        
        logger.error(f"Template not found: {template_name}")
        return None

    def get_prompt(self, template_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Get formatted prompt for template"""
        template = self.get_template(template_name)
        if not template:
            return None
        
        return template.format(**data)

    def list_available_templates(self) -> List[str]:
        """List all available template names"""
        if not os.path.exists(self.config_dir):
            return []
        
        templates = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                templates.append(filename[:-5])
        
        return templates

    def add_template(self, template: PromptTemplate):
        """Add new template and save to file"""
        self._templates_cache[template.name] = template
        self._save_template(template)

    def update_template(self, template_name: str, **kwargs):
        """Update existing template"""
        template = self.get_template(template_name)
        if not template:
            logger.error(f"Template not found for update: {template_name}")
            return
        
        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        self._save_template(template)

    def _save_template(self, template: PromptTemplate):
        """Save template to file"""
        try:
            file_path = os.path.join(self.config_dir, f"{template.name}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(template), f, indent=2, ensure_ascii=False)
            logger.info(f"Template saved: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save template: {e}")

    def reload_templates(self):
        """Reload all templates from files"""
        self._templates_cache.clear()
        self._loaded_files.clear()
        self._load_all_templates()


def create_default_templates():
    """Create default prompt template files"""
    config_dir = "prompt_configs"
    os.makedirs(config_dir, exist_ok=True)
    
    default_templates = {
        "outline_generation": {
            "name": "outline_generation",
            "description": "Story outline generation",
            "template": "Please generate a detailed novel outline for the following story concept:\n\nStory concept: {concept}\n\nRequirements:\n1. Divide the story into 1-2 main parts with major climax points\n2. Each part contains 1-2 volumes with climax points\n3. Provide titles and descriptions for each volume\n4. Estimate chapter count for each volume\n5. List main characters and scenes\n\nReturn in JSON format.\n\nAdditional requirements: {additional_requirements}",
            "version": "1.0",
            "variables": ["concept", "additional_requirements"],
            "system_prompt": ""
        },
        "detail_generation": {
            "name": "detail_generation",
            "description": "Detailed outline generation",
            "template": "Please generate a detailed outline for the following chapter:\n\n{context_info}\n\nVolume Information:\nTitle: {title}\nSummary: {summary}\nCharacters: {characters}\nLocations: {locations}\nEstimated words: {words}\n\nGenerate detailed outline with scenes, transitions, and emotional development.",
            "version": "1.0",
            "variables": ["context_info", "title", "summary", "characters", "locations", "words"],
            "system_prompt": ""
        },
        "frame_generation": {
            "name": "frame_generation",
            "description": "Fixed frame generation",
            "template": "Please generate 6-8 chapter frames for the following scene:\n\n{context_info}\n\nScene Information:\nTitle: {scene_title}\nDescription: {scene_description}\nCharacters: {characters}\nLocation: {location}\nKey events: {events}\nEmotional tone: {tone}\n\nEach frame should represent a climactic moment with complete state description.",
            "version": "1.0",
            "variables": ["context_info", "scene_title", "scene_description", "characters", "location", "events", "tone"],
            "system_prompt": ""
        },
        "writing_expansion": {
            "name": "writing_expansion",
            "description": "Fixed frame expansion writing",
            "template": "Please expand the fixed frame into a complete literary paragraph:\n\n{context_info}\n\nFrame Information:\nTime: {timestamp}\nScene: {scene_id}\nCurrent action: {current_action}\nCharacters: {characters}\nLocation: {location}\nEnvironment: {environment}\nObjects: {objects}\nDialogue: {dialogue}\nThoughts: {thoughts}\nSensory: {sensory_details}\n\nUse {style} style for description. Control word count to 300-800 words.",
            "version": "1.0",
            "variables": ["context_info", "timestamp", "scene_id", "current_action", "characters", "location", "environment", "objects", "dialogue", "thoughts", "sensory_details", "style"],
            "system_prompt": ""
        },
        "character_creation": {
            "name": "character_creation",
            "description": "Character creation",
            "template": "Please create a detailed character:\n\nBasic Information:\nName: {name}\nAge: {age}\nGender: {gender}\nOccupation: {occupation}\n\nInclude appearance, personality, background, skills, weaknesses, and relationships.",
            "version": "1.0",
            "variables": ["name", "age", "gender", "occupation"],
            "system_prompt": ""
        }
    }
    
    for template_name, template_data in default_templates.items():
        file_path = os.path.join(config_dir, f"{template_name}.json")
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2, ensure_ascii=False)
                print(f"Created default template: {template_name}")
            except Exception as e:
                print(f"Failed to create template {template_name}: {e}")


def test_prompt_manager():
    """Test the prompt configuration manager"""
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Create default templates if they don't exist
    create_default_templates()
    
    manager = PromptConfigManager()
    
    # List available templates
    print("Available templates:")
    for template_name in manager.list_available_templates():
        print(f"  - {template_name}")
    
    # Test getting a prompt
    print("\nTesting outline generation prompt:")
    data = {
        "concept": "A story about AI awakening",
        "additional_requirements": "Include philosophical themes"
    }
    
    prompt = manager.get_prompt("outline_generation", data)
    if prompt:
        print(f"Prompt length: {len(prompt)}")
        print(f"Prompt preview:\n{prompt[:200]}...")
    
    print("\nPrompt manager test completed")


if __name__ == "__main__":
    test_prompt_manager()