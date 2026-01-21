# Test script to verify the agentic backend
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        from app.mcp.registry import mcp_registry
        from app.agents.todo_agent import TodoAgent
        from app.db.session import engine
        from app.models import user, task, conversation
        print("[OK] All modules imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

def test_mcp_tools():
    """Test that MCP tools are registered"""
    try:
        # Import the tasks module to ensure tools are registered
        from app.mcp import tasks
        from app.mcp.registry import mcp_registry

        expected_tools = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]
        registered_tools = list(mcp_registry.get_all_tool_definitions().keys())

        for tool in expected_tools:
            if tool not in registered_tools:
                print(f"[ERROR] Tool {tool} not registered")
                return False

        print(f"[OK] All MCP tools registered: {registered_tools}")
        return True
    except Exception as e:
        print(f"[ERROR] MCP tools test failed: {e}")
        return False

def test_agent_creation():
    """Test that agent can be created (without calling OpenAI)"""
    try:
        # Import the tasks module to ensure tools are registered
        from app.mcp import tasks
        # Mock the OpenAI API key to avoid actual API calls
        os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"

        from app.agents.todo_agent import TodoAgent
        agent = TodoAgent(api_key="sk-test-key-for-testing")

        # Check that tools are prepared
        tools = agent._prepare_tools_for_agent()
        if len(tools) == 0:
            print("[ERROR] Agent has no tools prepared")
            return False

        print(f"[OK] Agent created successfully with {len(tools)} tools")
        return True
    except Exception as e:
        print(f"[ERROR] Agent creation test failed: {e}")
        return False

def run_tests():
    """Run all tests"""
    print("Running tests for Agentic Todo AI Backend...\n")

    tests = [
        test_imports,
        test_mcp_tools,
        test_agent_creation
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return True
    else:
        print("\n[FAILURE] Some tests failed!")
        return False

if __name__ == "__main__":
    run_tests()