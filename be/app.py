from typing import Annotated, List
import autogen

# Azure OpenAI Configuration
config_list = [
    {
        "model": "gpt-4-32k",
        "api_key": "f1719a4af60d45ada4097b9570a2c5d0",
        "azure_endpoint": "https://cast-southcentral-nprd-apim.azure-api.net/AITCSG",
        "api_type": "azure",
        "api_version": "2023-07-01-preview"
    }
]

# Define LLM Configuration using Azure
llm_config = {
    "config_list": config_list,
    "temperature": 0.7,
    "max_tokens": 1000
}

# Create proper AutoGen agents without Docker dependency
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",  # Set to "ALWAYS" if you want to provide input at each step
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
    code_execution_config={"last_n_messages": 1, "work_dir": "workdir", "use_docker": False},  # Disable Docker
    system_message="You are a helpful user proxy agent."
)

code_analyzer = autogen.AssistantAgent(
    name="CodeAnalyzer",
    llm_config=llm_config,
    system_message="You are a code analyzer that examines code to identify functions, classes, and dependencies."
)

test_generator = autogen.AssistantAgent(
    name="TestGenerator",
    llm_config=llm_config,
    system_message="You are a test generator that creates unit and integration tests for code components."
)

test_executor = autogen.AssistantAgent(
    name="TestExecutor",
    llm_config=llm_config,
    system_message="You are a test executor that runs tests and reports on failures and successes."
)

ci_integration = autogen.AssistantAgent(
    name="CIIntegration",
    llm_config=llm_config,
    system_message="You are a CI integration agent that reports test results to CI/CD systems and comments on PRs."
)

# Function: Extract Code Components
def extract_code_components(codebase: str) -> str:
    """Analyzes the codebase and extracts functions, classes, and dependencies."""
    return "Extracted functions: foo(), bar(); Missing tests: foo() lacks edge cases."

# Function: Generate Tests
def generate_tests(code_analysis: str) -> str:
    """Generates unit and integration tests based on the extracted code."""
    return "Generated test cases: test_foo_edge_case, test_bar_normal_case."

# Function: Run Tests
def run_tests(test_files: List[str]) -> str:
    """Executes the generated test cases and reports failures."""
    return "Test results: 2 failures, 5 passes. Failures in test_foo_edge_case."

# Function: CI Reporting
def ci_report(test_results: str) -> str:
    """Reports test results to CI/CD and comments on PRs."""
    return "Posted results to PR: 2 test failures detected. Suggested fixes included."

# Register functions with proper AutoGen agents
user_proxy.register_function(
    function_map={
        "extract_code_components": extract_code_components,
    }
)

code_analyzer.register_function(
    function_map={
        "generate_tests": generate_tests,
    }
)

test_generator.register_function(
    function_map={
        "run_tests": run_tests,
    }
)

test_executor.register_function(
    function_map={
        "ci_report": ci_report,
    }
)

# Group Chat Setup
groupchat = autogen.GroupChat(
    agents=[user_proxy, code_analyzer, test_generator, test_executor, ci_integration],
    messages=[]
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config
)

# Trigger Automated Testing
user_proxy.initiate_chat(
    manager,
    message="Analyze the codebase, generate missing tests, execute them, and report results to CI."
)