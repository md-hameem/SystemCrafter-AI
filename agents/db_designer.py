"""
SystemCrafter AI - Database Designer Agent
Creates normalized DB schemas, ER diagrams, and migration scripts.
"""
import json
from typing import Any

from agents.base import AgentConfig, BaseAgent
from orchestrator.core import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a database architect. Create a complete database schema with migrations and diagrams.

Output ONLY valid JSON matching this schema:
{
  "er_mermaid": "Mermaid ER diagram code",
  "sql_migration": "Complete SQL migration script for PostgreSQL",
  "tables": [
    {
      "name": "table_name",
      "description": "What this table stores",
      "columns": [
        {
          "name": "column_name",
          "type": "UUID|TEXT|INTEGER|FLOAT|BOOLEAN|TIMESTAMP|JSONB",
          "constraints": ["PRIMARY KEY", "NOT NULL", "UNIQUE", "DEFAULT value"],
          "references": "other_table(column) or null"
        }
      ],
      "indexes": [
        {
          "name": "idx_name",
          "columns": ["col1", "col2"],
          "unique": false
        }
      ]
    }
  ],
  "indexing_advice": [
    "Advice on what indexes to create and why"
  ],
  "scaling_advice": [
    "Advice on partitioning, sharding, read replicas"
  ]
}

DATABASE DESIGN REQUIREMENTS:
- Use PostgreSQL syntax
- Use UUID for primary keys (gen_random_uuid())
- Include created_at and updated_at timestamps on all tables
- Define proper foreign key relationships with ON DELETE/ON UPDATE
- Create indexes for frequently queried columns
- Use appropriate data types (TEXT over VARCHAR for variable strings)
- Add NOT NULL constraints where appropriate
- Include comments/descriptions for tables
- Consider normalization but keep practical for the use case

SQL MIGRATION SHOULD INCLUDE:
- CREATE TABLE statements with all columns and constraints
- CREATE INDEX statements
- Foreign key constraints
- Default values
- Comments

MERMAID ER DIAGRAM:
- Use erDiagram syntax
- Show all entities and relationships
- Include key fields"""


class DBDesignerAgent(BaseAgent):
    """
    Agent that designs database schemas and generates migrations.
    """
    
    def __init__(self) -> None:
        config = AgentConfig(
            name="Database Designer",
            description="Designs database schemas and generates SQL migrations",
            temperature=0.1,  # Low temperature for consistent schema design
            max_tokens=8192,
        )
        super().__init__(config)
    
    @property
    def system_prompt(self) -> str:
        return SYSTEM_PROMPT
    
    def build_user_prompt(self, input_data: dict) -> str:
        """Build prompt from entities."""
        entities = input_data.get("entities", [])
        preferences = input_data.get("preferences", {})
        
        prompt = f"Entities to model:\n{json.dumps(entities, indent=2)}"
        
        if preferences:
            prompt += f"\n\nDatabase Preferences:\n{json.dumps(preferences, indent=2)}"
        
        return prompt
    
    def validate_input(self, input_data: dict) -> bool:
        """Validate that entities are provided."""
        if "entities" not in input_data:
            logger.error("Missing required field: entities")
            return False
        return True
    
    def validate_output(self, output: dict) -> bool:
        """Validate output has required fields."""
        required_fields = ["sql_migration", "er_mermaid"]
        for field in required_fields:
            if field not in output:
                logger.error(f"Missing required output field: {field}")
                return False
        return True
    
    def parse_response(self, response: str) -> dict:
        """Parse JSON response from LLM."""
        try:
            return self._safe_json_parse(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {e}")
