"""
Example: Run white agent on a single task

This script demonstrates how to run the enhanced white agent on a single task.
"""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from white_agent_starter import create_enhanced_agent, run_enhanced_agent
from openhands.core.config import OpenHandsConfig, SandboxConfig, LLMConfig
from openhands.core.main import create_runtime
from openhands.utils.async_utils import call_async_from_sync


async def main():
    """Run agent on a single task."""
    
    # Configuration
    task_name = "pm-schedule-meeting-1"  # Change this to test different tasks
    task_image = f"ghcr.io/theagentcompany/{task_name}:1.0.0"
    
    # LLM Configuration
    llm_config = LLMConfig(
        api_key=os.getenv("OPENAI_API_KEY", "your-api-key"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        model=os.getenv("LLM_MODEL", "gpt-4")
    )
    
    # OpenHands Configuration
    config = OpenHandsConfig(
        run_as_openhands=False,
        max_budget_per_task=4,
        max_iterations=100,
        save_trajectory_path=f"./traj_{task_name}.json",
        sandbox=SandboxConfig(
            base_container_image=task_image,
            enable_auto_lint=True,
            use_host_network=True,
            timeout=300,
        ),
    )
    config.set_llm_config(llm_config)
    
    # Create runtime
    print(f"Creating runtime for task: {task_name}")
    runtime = create_runtime(config)
    await call_async_from_sync(runtime.connect)
    
    # Run agent
    print(f"Running agent on task: {task_name}")
    state = await run_enhanced_agent(runtime, task_name, config)
    
    print(f"Task completed! Trajectory saved to: traj_{task_name}.json")
    
    # Cleanup
    await call_async_from_sync(runtime.close)


if __name__ == "__main__":
    print("=" * 60)
    print("White Agent - Single Task Example")
    print("=" * 60)
    print("\nThis example runs the enhanced white agent on a single task.")
    print("Make sure you have:")
    print("1. TheAgentCompany servers running")
    print("2. OPENAI_API_KEY environment variable set")
    print("3. Task image available")
    print("\n")
    
    asyncio.run(main())



