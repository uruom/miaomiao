"""Prompt Configuration Manager - Unified management of all module prompt templates"""

import json
import os
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import logging

# Import system prompt configuration

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """Prompt template"""
    name: str
    template: str
    description: str = ""
    version: str = "1.0"
    variables: List[str] = None
    system_prompt: str = ""

    def __post_init__(self):
        if self.variables is None:
            # Automatically extract variables
            self.variables = self._extract_variables()

    def _extract_variables(self) -> List[str]:
        """Extract variable names from template"""
        pattern = r'\{(\w+)\}'
        variables = re.findall(pattern, self.template)
        return list(set(variables))  # Remove duplicates

    def format(self, **kwargs) -> str:
        """Format template"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing template variable: {e}")
            # Try to replace missing variables with empty strings
            formatted = self.template
            for var in self.variables:
                if var not in kwargs:
                    formatted = formatted.replace(f"{{{var}}}", "")
            return formatted
        except Exception as e:
            logger.error(f"Template formatting failed: {e}")
            return self.template


class PromptManager:
    """Prompt Manager - Loads prompts from configuration files on demand"""

    def __init__(self, config_dir: str = "prompt_configs"):
        self.config_dir = config_dir
        self.templates: Dict[str, PromptTemplate] = {}

        # Load user configurations
        self._load_user_configs()

    def _load_user_configs(self):
        """Load user-configured templates"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
            logger.info(f"Created config directory: {self.config_dir}")
            return

        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.config_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    if isinstance(data, dict):
                        template = PromptTemplate(**data)
                        self.templates[template.name] = template
                    elif isinstance(data, list):
                        for item in data:
                            template = PromptTemplate(**item)
                            self.templates[template.name] = template

                    logger.info(f"Loaded user template: {filename}")
                except Exception as e:
                    logger.error(f"Failed to load template file {filename}: {e}")

    def get_prompt(self, template_name: str, data: Dict[str, Any]) -> Optional[str]:
        """Get formatted prompt"""
        template = self.templates.get(template_name)
        if not template:
            logger.error(f"Template does not exist: {template_name}")
            return None

        return template.format(**data)

    def get_system_prompt(self, template_name: str) -> Optional[str]:
        """Get system prompt"""
        template = self.templates.get(template_name)
        if not template:
            logger.error(f"Template does not exist: {template_name}")
            return None

        return template.system_prompt

    def add_template(self, template: PromptTemplate):
        """Add new template"""
        self.templates[template.name] = template
        logger.info(f"Added template: {template.name}")

    def remove_template(self, template_name: str):
        """Remove template"""
        if template_name in self.templates:
            del self.templates[template_name]
            logger.info(f"Removed template: {template_name}")
        else:
            logger.warning(f"Template does not exist: {template_name}")

    def list_templates(self) -> List[str]:
        """List all available templates"""
        return list(self.templates.keys())

    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """Get template information"""
        template = self.templates.get(template_name)
        if not template:
            return None

        return asdict(template)

    def save_template_to_file(self, template_name: str, filename: str = None):
        """Save template to file"""
        template = self.templates.get(template_name)
        if not template:
            logger.error(f"Template does not exist: {template_name}")
            return False

        if filename is None:
            filename = f"{template_name}.json"

        filepath = os.path.join(self.config_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(template), f, ensure_ascii=False, indent=2)
            logger.info(f"Template saved to: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False

    def load_template(self, template_name: str) -> Optional[PromptTemplate]:
        """Load a specific template on demand"""
        if template_name in self.templates:
            return self.templates[template_name]

        # Try to load from file
        filepath = os.path.join(self.config_dir, f"{template_name}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                template = PromptTemplate(**data)
                self.templates[template_name] = template
                logger.info(f"Loaded template on demand: {template_name}")
                return template
            except Exception as e:
                logger.error(f"Failed to load template {template_name}: {e}")
        
        return None


# Create global manager instance
prompt_manager = PromptManager()


def test_prompt_manager():
     """Test prompt manager"""
     manager = PromptManager()

     # Test template list
     templates = manager.list_templates()
     print(f"Available templates: {templates}")

     # Test getting template information
     for template_name in templates:
         info = manager.get_template_info(template_name)
         if info:
             print(f"\nTemplate: {template_name}")
             print(f"Description: {info.get('description', 'None')}")
             print(f"Variables: {info.get('variables', [])}")
             print(f"Version: {info.get('version', '1.0')}")

     # Test on-demand loading
     if "outline_generation" not in templates:
         template = manager.load_template("outline_generation")
         if template:
             print(f"\nSuccessfully loaded template on demand: {template.name}")

     # Test formatting
     if "outline_generation" in manager.list_templates():
         test_data = {
             "concept": "A story about artificial intelligence awakening",
             "additional_requirements": "Include discussion of technological ethics"
         }
         prompt = manager.get_prompt("outline_generation", test_data)
         if prompt:
             print("\nFormatted prompt:")
             print(prompt[:200] + "...")


if __name__ == "__main__":
     test_prompt_manager()