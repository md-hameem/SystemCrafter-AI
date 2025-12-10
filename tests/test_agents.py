"""
Tests for Agent modules
"""
import pytest
from unittest.mock import AsyncMock, patch

from agents.requirement_interpreter import RequirementInterpreterAgent
from agents.system_architect import SystemArchitectAgent


@pytest.mark.asyncio
async def test_requirement_interpreter_validate_input():
    """Test input validation for requirement interpreter."""
    agent = RequirementInterpreterAgent()
    
    # Valid input
    assert agent.validate_input({"raw_text": "Build a todo app"}) is True
    
    # Missing raw_text
    assert agent.validate_input({}) is False
    
    # Empty raw_text
    assert agent.validate_input({"raw_text": ""}) is False
    assert agent.validate_input({"raw_text": "   "}) is False


@pytest.mark.asyncio
async def test_requirement_interpreter_validate_output():
    """Test output validation for requirement interpreter."""
    agent = RequirementInterpreterAgent()
    
    # Valid output
    valid_output = {
        "title": "Todo App",
        "summary": "A simple todo application",
        "features": [{"id": "F1", "name": "Create Todo"}],
    }
    assert agent.validate_output(valid_output) is True
    
    # Missing title
    assert agent.validate_output({"features": []}) is False
    
    # Missing features
    assert agent.validate_output({"title": "Test"}) is False
    
    # Features not a list
    assert agent.validate_output({"title": "Test", "features": "invalid"}) is False


@pytest.mark.asyncio
async def test_system_architect_validate_input():
    """Test input validation for system architect."""
    agent = SystemArchitectAgent()
    
    # Valid input
    assert agent.validate_input({"project_spec": {"title": "Test"}}) is True
    
    # Missing project_spec
    assert agent.validate_input({}) is False


@pytest.mark.asyncio
async def test_system_architect_validate_output():
    """Test output validation for system architect."""
    agent = SystemArchitectAgent()
    
    # Valid output
    valid_output = {
        "selected_architecture": {"name": "Monolith"},
        "diagram_mermaid": "graph TD...",
    }
    assert agent.validate_output(valid_output) is True
    
    # Missing selected_architecture
    assert agent.validate_output({"diagram_mermaid": "..."}) is False
    
    # Missing diagram_mermaid
    assert agent.validate_output({"selected_architecture": {}}) is False
