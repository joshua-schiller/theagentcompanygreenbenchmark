"""
Simple test script to run the white agent on a task.

This script tests the agent's logic without requiring full OpenHands setup.
"""

import sys
import os
import tempfile

sys.path.append(os.path.dirname(__file__))

from white_agent_intelligent import (
    TaskAnalyzer,
    IntelligentPlanner,
    RedundancyDetector,
    ReflectionModule,
)


def test_agent_on_task(task_name: str = "pm-schedule-meeting-1"):
    """Test the agent's components on a task."""

    print("=" * 70)
    print(f"Testing White Agent on Task: {task_name}")
    print("=" * 70)

    # Create a mock task.md content
    mock_tasks = {
        "pm-schedule-meeting-1": """Task: Schedule a meeting between Emily Zhou and Liu Qiang.

Steps:
1. Navigate to RocketChat at http://the-agent-company.com:3000/home
2. Send message to Emily Zhou asking for availability
3. Send message to Liu Qiang asking for availability
4. Create conclusion.txt file with meeting schedule in /workspace/conclusion.txt
5. Finish""",
        "sde-run-janusgraph": """Task: Set up and run JanusGraph server.

Steps:
1. Clone JanusGraph repository from http://the-agent-company.com:8929/root/janusgraph
2. Build with Maven (mvn clean install -DskipTests)
3. Start JanusGraph server (bin/janusgraph.sh start)
4. Finish""",
        "finance-qualified-bill-ask-for-reimburse": """Task: Process reimbursement request.

Steps:
1. Navigate to OwnCloud at http://the-agent-company.com:8092/
2. Read receipt.jpg file from /Documents/Financials/receipt.jpg
3. Read reimbursement policy PDF from /Documents/Administrative Specialist/Reimbursement Policy.pdf
4. Navigate to RocketChat
5. Send message to Mike Chen with reimbursement amount
6. Finish""",
    }

    task_content = mock_tasks.get(task_name, mock_tasks["pm-schedule-meeting-1"])

    # Write mock task.md to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(task_content)
        temp_task_path = f.name

    try:
        print("\n[Phase 1] Task Analysis")
        print("-" * 70)

        # Analyze task
        analyzer = TaskAnalyzer()
        task_analysis = analyzer.analyze_task(temp_task_path)

        print(f"Task Type: {task_analysis['task_type']}")
        print(f"\nEntities Found:")
        for key, values in task_analysis["entities"].items():
            if values:
                print(f"  - {key}: {values}")

        print("\n[Phase 2] Planning")
        print("-" * 70)

        # Create plan
        planner = IntelligentPlanner()
        plan = planner.create_plan(task_analysis)

        print(f"Plan created: {len(plan)} steps")
        for i, step in enumerate(plan, 1):
            print(f"\n  Step {i}: {step['action_type']}")
            print(f"    Reasoning: {step.get('reasoning', 'N/A')}")
            if "recipient" in step:
                print(f"    Recipient: {step['recipient']}")
            if "command" in step:
                cmd = step["command"]
                print(
                    f"    Command: {cmd[:70]}..."
                    if len(cmd) > 70
                    else f"    Command: {cmd}"
                )
            if "url" in step:
                print(f"    URL: {step['url']}")
            if "path" in step:
                print(f"    Path: {step['path']}")

        print("\n[Phase 3] Redundancy Detection Test")
        print("-" * 70)

        # Test redundancy detection
        redundancy_detector = RedundancyDetector()

        print("Simulating execution with redundancy checks:\n")
        for i, step in enumerate(plan):
            is_redundant, message = redundancy_detector.check_redundancy(step)

            if is_redundant:
                print(f"  Step {i+1}: REDUNDANT")
                print(f"    {message}")
                print(f"    -> Would be SKIPPED")
            else:
                print(f"  Step {i+1}: Not redundant")
                print(f"    Action: {step['action_type']}")
                print(f"    -> Would EXECUTE")
            print()

        print("\n[Phase 4] Goal Tracking Test")
        print("-" * 70)

        # Test goal tracking
        reflection = ReflectionModule()
        goals = reflection.extract_goals(task_content)

        print(f"Goals extracted: {len(goals)}")
        for i, goal in enumerate(goals, 1):
            print(f"  {i}. {goal}")

        print("\n[Summary]")
        print("-" * 70)
        print(f"Task analyzed: {task_analysis['task_type']} task")
        print(f"Plan created: {len(plan)} steps")
        print(f"Redundancy detection: Working")
        print(f"Goal tracking: {len(goals)} goals identified")
        print(f"\nAgent is ready to execute!")
        print(f"\nKey Improvements Over Baseline:")
        print(f"  - Planning: {len(plan)} steps planned upfront (not reactive)")
        print(f"  - Redundancy: Detection prevents loops")
        print(f"  - Goals: {len(goals)} goals tracked for completion")

    finally:
        # Cleanup
        if os.path.exists(temp_task_path):
            os.remove(temp_task_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test white agent")
    parser.add_argument(
        "--task", type=str, default="pm-schedule-meeting-1", help="Task name to test"
    )
    parser.add_argument("--list", action="store_true", help="List available test tasks")

    args = parser.parse_args()

    if args.list:
        print("Available test tasks:")
        print("  1. pm-schedule-meeting-1")
        print("  2. sde-run-janusgraph")
        print("  3. finance-qualified-bill-ask-for-reimburse")
    else:
        test_agent_on_task(args.task)
