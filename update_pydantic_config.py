#!/usr/bin/env python3
"""
Script to update Pydantic V2 configuration from deprecated settings.
"""

import re

def update_pydantic_config():
    """Update Pydantic models to use V2 configuration."""

    models_file = "app/models.py"

    with open(models_file, 'r') as f:
        content = f.read()

    # Replace deprecated configuration
    updates = [
        (r'allow_population_by_field_name = True', 'populate_by_name = True'),
        (r'__get_validators__', '__get_pydantic_core_schema__'),
        (r'__get_pydantic_json_schema__', '__get_json_schema__'),
    ]

    for old, new in updates:
        content = re.sub(re.escape(old), new, content)

    # Update the PyObjectId class for Pydantic V2
    pydantic_v2_objectid = '''
class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_plain_validator_function(
            cls.validate,
            json_types_schema=core_schema.json_schema({"type": "string"}),
        )

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_json_schema__(cls, schema, handler):
        return {"type": "string"}
'''

    # Replace the old PyObjectId class
    content = re.sub(
        r'class PyObjectId\(ObjectId\):.*?@classmethod.*?def __get_pydantic_json_schema__.*?return \{"type": "string"\}',
        pydantic_v2_objectid.strip(),
        content,
        flags=re.DOTALL
    )

    with open(models_file, 'w') as f:
        f.write(content)

    print("✅ Updated Pydantic models for V2 compatibility")
    print("🔄 Changes made:")
    print("   - Replaced 'allow_population_by_field_name' with 'populate_by_name'")
    print("   - Updated PyObjectId class for Pydantic V2")
    print("🔄 Please restart the server for changes to take effect")

if __name__ == "__main__":
    update_pydantic_config()
