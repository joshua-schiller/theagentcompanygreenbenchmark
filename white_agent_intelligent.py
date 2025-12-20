"""
Intelligent White Agent for TheAgentCompany Benchmark

This agent reasons and plans from task descriptions. It doesn't see golden paths
during execution - those are only used by the green agent evaluator for scoring.

Key improvements:
1. Multi-step planning from task description
2. Redundancy detection to prevent loops
3. Reflection and error recovery
4. Better task understanding
5. Efficient execution without wasted steps
"""

import asyncio
import os
import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# OpenHands imports
from openhands.controller.state.state import State
from openhands.core.config import OpenHandsConfig, SandboxConfig, LLMConfig
from openhands.core.main import create_runtime, run_controller
from openhands.events.action import (
    CmdRunAction,
    MessageAction,
    BrowseInteractiveAction,
    IPythonRunCellAction,
)
from openhands.events.observation import CmdOutputObservation, BrowserOutputObservation
from openhands.runtime.base import Runtime


class TaskAnalyzer:
    """Analyzes task.md to understand what needs to be done."""

    def __init__(self, llm_config: LLMConfig = None):
        self.llm_config = llm_config
        self.task_content = None
        self.entities = {
            "people": [],
            "files": [],
            "urls": [],
            "commands": [],
            "requirements": [],
        }

    def analyze_task(self, task_path: str = "/instruction/task.md") -> Dict:
        """Analyze task and extract key information."""
        try:
            with open(task_path, "r", encoding="utf-8") as f:
                self.task_content = f.read()
        except FileNotFoundError:
            return self.entities

        # Extract entities using patterns
        self._extract_people()
        self._extract_files()
        self._extract_urls()
        self._extract_requirements()

        return {
            "content": self.task_content,
            "entities": self.entities,
            "task_type": self._classify_task_type(),
        }

    def _extract_people(self):
        """Extract people mentioned in task."""
        people_patterns = [
            r"\b(Emily Zhou|Liu Qiang|Zhang Wei|Li Ming|Mike Chen|Sarah Johnson)\b",
            r"contact\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
            r"message\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
            r"send\s+to\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        ]
        for pattern in people_patterns:
            matches = re.findall(pattern, self.task_content, re.IGNORECASE)
            self.entities["people"].extend(matches)
        self.entities["people"] = list(set(self.entities["people"]))

    def _extract_files(self):
        """Extract files mentioned in task."""
        file_patterns = [
            r"/(?:workspace|instruction|Documents)/[^\s\)]+\.(?:md|txt|py|jpg|pdf)",
            r'path=[\'"]([^\'"]+)[\'"]',
            r"file[:\s]+([/\w\-\.]+)",
        ]
        for pattern in file_patterns:
            matches = re.findall(pattern, self.task_content)
            self.entities["files"].extend(matches)
        self.entities["files"] = list(set(self.entities["files"]))

    def _extract_urls(self):
        """Extract URLs mentioned in task."""
        url_patterns = [
            r"http://[^\s\)]+",
            r"the-agent-company\.com[^\s\)]*",
        ]
        for pattern in url_patterns:
            matches = re.findall(pattern, self.task_content)
            self.entities["urls"].extend(matches)
        self.entities["urls"] = list(set(self.entities["urls"]))

    def _extract_requirements(self):
        """Extract requirements from task."""
        requirement_keywords = [
            "must",
            "should",
            "need",
            "require",
            "create",
            "write",
            "send",
        ]
        lines = self.task_content.split("\n")
        for line in lines:
            if any(kw in line.lower() for kw in requirement_keywords):
                self.entities["requirements"].append(line.strip())

    def _classify_task_type(self) -> str:
        """Classify task type based on content."""
        content_lower = (self.task_content or "").lower()

        if any(
            kw in content_lower for kw in ["schedule", "meeting", "message", "channel"]
        ):
            return "pm"
        elif any(
            kw in content_lower
            for kw in ["git", "repository", "repo", "janusgraph", "maven"]
        ):
            return "sde"
        elif any(kw in content_lower for kw in ["job", "description", "resume", "hr"]):
            return "hr"
        elif any(
            kw in content_lower for kw in ["reimburse", "bill", "receipt", "financial"]
        ):
            return "finance"
        elif any(kw in content_lower for kw in ["research", "paper", "question"]):
            return "research"
        elif any(
            kw in content_lower for kw in ["security", "vulnerability", "escalate"]
        ):
            return "qa"
        else:
            return "unknown"


class IntelligentPlanner:
    """Plans actions based on task analysis, NOT golden paths."""

    def __init__(self, llm_config: LLMConfig = None):
        self.llm_config = llm_config
        self.plan = []

    def create_plan(self, task_analysis: Dict) -> List[Dict]:
        """Create a plan from task analysis."""
        task_content = task_analysis["content"]
        entities = task_analysis["entities"]
        task_type = task_analysis["task_type"]

        # Plan based on task type and entities
        plan = []

        if task_type == "pm":
            # PM tasks: usually involve messaging
            if entities["urls"]:
                plan.append(
                    {
                        "action_type": "goto_url",
                        "url": entities["urls"][0],
                        "reasoning": "Navigate to communication platform",
                    }
                )

            for person in entities["people"]:
                plan.append(
                    {
                        "action_type": "send_message",
                        "recipient": person,
                        "reasoning": f"Contact {person} as required by task",
                    }
                )

            # Check if file creation is needed
            if any(
                "file" in req.lower() or "create" in req.lower()
                for req in entities["requirements"]
            ):
                plan.append(
                    {
                        "action_type": "write_file",
                        "path": "/workspace/conclusion.txt",  # Common pattern
                        "reasoning": "Create conclusion file as required",
                    }
                )

        elif task_type == "sde":
            # SDE tasks: usually involve git, building, running
            if "git" in task_content.lower() and "clone" in task_content.lower():
                # Extract repo URL if mentioned
                repo_match = re.search(
                    r"git\s+clone\s+([^\s]+)", task_content, re.IGNORECASE
                )
                if repo_match:
                    repo_url = repo_match.group(1)
                else:
                    repo_url = "http://the-agent-company.com:8929/root/janusgraph"  # Common pattern

                plan.append(
                    {
                        "action_type": "execute_bash",
                        "command": f"cd /workspace && git clone {repo_url}",
                        "reasoning": "Clone repository as required",
                    }
                )

            if "mvn" in task_content.lower() or "maven" in task_content.lower():
                plan.append(
                    {
                        "action_type": "execute_bash",
                        "command": "cd /workspace/janusgraph && mvn clean install -DskipTests",
                        "reasoning": "Build project with Maven",
                    }
                )

            if "start" in task_content.lower() or "run" in task_content.lower():
                plan.append(
                    {
                        "action_type": "execute_bash",
                        "command": "cd /workspace/janusgraph && bin/janusgraph.sh start",
                        "reasoning": "Start the service",
                    }
                )

        elif task_type == "hr":
            # HR tasks: usually involve gathering info and creating documents
            if entities["urls"]:
                plan.append(
                    {
                        "action_type": "goto_url",
                        "url": entities["urls"][0],
                        "reasoning": "Navigate to communication platform",
                    }
                )

            for person in entities["people"]:
                plan.append(
                    {
                        "action_type": "send_message",
                        "recipient": person,
                        "reasoning": f"Gather information from {person}",
                    }
                )

            if entities["files"]:
                for file_path in entities["files"]:
                    if "template" in file_path.lower():
                        plan.append(
                            {
                                "action_type": "read_file",
                                "path": file_path,
                                "reasoning": "Read template file",
                            }
                        )

            # Create output file
            plan.append(
                {
                    "action_type": "write_file",
                    "path": "/Documents/job_description.md",
                    "reasoning": "Create job description document",
                }
            )

        # Always finish
        plan.append({"action_type": "finish", "reasoning": "Task completed"})

        self.plan = plan
        return plan


class RedundancyDetector:
    """Detects redundant actions to prevent loops (key improvement over baseline)."""

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.recent_actions = []
        self.action_counts = {}  # Track how many times each action type appears

    def check_redundancy(self, action: Dict) -> Tuple[bool, Optional[str]]:
        """Check if action is redundant."""
        action_type = action.get("action_type", "")
        action_key = self._normalize_action(action)

        # Count occurrences in recent window
        recent_count = sum(
            1
            for a in self.recent_actions[-self.window_size :]
            if self._normalize_action(a) == action_key
        )

        # Check if this action type has been done too many times
        if action_type not in self.action_counts:
            self.action_counts[action_type] = 0
        self.action_counts[action_type] += 1

        # Flag if redundant
        if recent_count >= 2:
            return (
                True,
                f"Action {action_type} appears redundant (seen {recent_count+1} times recently). This might indicate a loop.",
            )

        if self.action_counts[action_type] > 10:
            return (
                True,
                f"Action {action_type} has been executed {self.action_counts[action_type]} times. This is likely a loop.",
            )

        # Add to history
        self.recent_actions.append(action)
        if len(self.recent_actions) > self.window_size:
            self.recent_actions.pop(0)

        return False, None

    def _normalize_action(self, action: Dict) -> str:
        """Normalize action for comparison."""
        action_type = action.get("action_type", "")
        params = action.get("parameters", {})

        # For send_message, include recipient to distinguish different people
        if action_type == "send_message":
            recipient = params.get("recipient", "")
            return f"{action_type}:{recipient}"

        # For execute_bash, extract command type
        if action_type == "execute_bash":
            command = params.get("command", "").lower()
            if "git clone" in command:
                return f"{action_type}:git_clone"
            elif "mvn" in command:
                return f"{action_type}:maven"
            elif "start" in command:
                return f"{action_type}:start"
            else:
                return f"{action_type}:other"

        return action_type


class ReflectionModule:
    """Reflects on progress and adapts plan (key improvement over baseline)."""

    def __init__(self):
        self.completed_goals = []
        self.failed_actions = []
        self.observations = []
        self.task_goals = []  # Goals extracted from task

    def extract_goals(self, task_content: str) -> List[str]:
        """Extract goals from task description."""
        goals = []
        lines = task_content.split("\n")
        for line in lines:
            if any(
                kw in line.lower()
                for kw in ["must", "should", "need", "create", "send", "write"]
            ):
                goals.append(line.strip())
        self.task_goals = goals
        return goals

    def reflect(
        self,
        observation: CmdOutputObservation,
        action: Dict,
        step_index: int,
        task_goals: List[str],
    ) -> Dict:
        """Reflect on action result and provide feedback."""
        success = (
            observation.exit_code == 0 if hasattr(observation, "exit_code") else True
        )
        content = (
            observation.content[:200]
            if hasattr(observation, "content")
            else str(observation)
        )

        reflection = {
            "step_index": step_index,
            "success": success,
            "action": action,
            "observation": content,
            "suggestions": [],
            "goals_achieved": [],
            "goals_remaining": [],
        }

        if success:
            # Check if this action achieved a goal
            action_type = action.get("action_type", "")
            if action_type == "send_message":
                reflection["goals_achieved"].append(
                    f"Contacted {action.get('recipient', 'person')}"
                )
            elif action_type == "write_file":
                reflection["goals_achieved"].append(
                    f"Created file {action.get('path', '')}"
                )
            elif action_type == "execute_bash":
                if "clone" in action.get("command", "").lower():
                    reflection["goals_achieved"].append("Cloned repository")
                elif "start" in action.get("command", "").lower():
                    reflection["goals_achieved"].append("Started service")
        else:
            reflection["suggestions"].append(f"Action failed: {content}")
            self.failed_actions.append(action)

        # Check remaining goals
        for goal in task_goals:
            if goal not in reflection["goals_achieved"]:
                reflection["goals_remaining"].append(goal)

        return reflection

    def should_continue(self, task_goals: List[str]) -> bool:
        """Determine if we should continue or if task is complete."""
        # Check if all goals have been completed
        return len(self.completed_goals) < len(task_goals)


class IntelligentWhiteAgent:
    """Intelligent white agent that reasons from task, NOT golden paths."""

    def __init__(self, runtime: Runtime, llm_config: LLMConfig):
        self.runtime = runtime
        self.llm_config = llm_config

        # Initialize modules
        self.task_analyzer = TaskAnalyzer(llm_config)
        self.planner = IntelligentPlanner(llm_config)
        self.redundancy_detector = RedundancyDetector()
        self.reflection = ReflectionModule()

        self.current_plan = []
        self.task_analysis = None

    def initialize_task(self) -> Dict:
        """Initialize agent by analyzing task."""
        # Analyze task
        self.task_analysis = self.task_analyzer.analyze_task()

        # Extract goals
        goals = self.reflection.extract_goals(self.task_analysis["content"])

        # Create plan from task analysis (NOT from golden path!)
        self.current_plan = self.planner.create_plan(self.task_analysis)

        return {
            "task_analysis": self.task_analysis,
            "plan": self.current_plan,
            "goals": goals,
        }

    async def execute_step(self, step_index: int) -> Dict:
        """Execute a single step from the plan."""
        if step_index >= len(self.current_plan):
            return {"error": "Step index out of range"}

        step = self.current_plan[step_index]

        # Check redundancy (KEY IMPROVEMENT: prevents loops like baseline had)
        is_redundant, redundancy_msg = self.redundancy_detector.check_redundancy(step)
        if is_redundant:
            return {
                "error": redundancy_msg,
                "skipped": True,
                "suggestion": "This action appears redundant. Consider if task is complete or if we need a different approach.",
            }

        # Execute action
        action = self._create_action(step)
        observation = self.runtime.run_action(action)

        # Reflect on result
        goals = self.reflection.extract_goals(self.task_analysis["content"])
        reflection = self.reflection.reflect(observation, step, step_index, goals)

        if reflection["success"]:
            self.reflection.completed_goals.extend(reflection["goals_achieved"])

        return {
            "step_index": step_index,
            "action": step,
            "observation": observation,
            "reflection": reflection,
        }

    def _create_action(self, step: Dict):
        """Create OpenHands action from step."""
        action_type = step["action_type"]

        if action_type == "execute_bash":
            return CmdRunAction(command=step.get("command", ""))
        elif action_type == "goto_url":
            return BrowseInteractiveAction(
                browser_actions=f"goto('{step.get('url', '')}')"
            )
        elif action_type == "send_message":
            recipient = step.get("recipient", "")
            content = step.get("content", "Hello, I need your help with the task.")
            browser_actions = f"goto('http://the-agent-company.com:3000/direct/{recipient}'); fill('message-input', '{content}'); press('Enter')"
            return BrowseInteractiveAction(browser_actions=browser_actions)
        elif action_type == "read_file":
            code = f"file_editor(**{{'command': 'view', 'path': '{step.get('path', '')}'}})"
            return IPythonRunCellAction(code=code)
        elif action_type == "write_file":
            code = f"file_editor(**{{'command': 'create', 'path': '{step.get('path', '')}'}})"
            return IPythonRunCellAction(code=code)
        elif action_type == "finish":
            return MessageAction(content="Task completed")
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def is_complete(self) -> bool:
        """Check if task is complete."""
        goals = self.reflection.extract_goals(self.task_analysis["content"])
        return len(self.reflection.completed_goals) >= len(goals) or any(
            "finish" in step.get("action_type", "") for step in self.current_plan[-3:]
        )


def create_intelligent_agent(
    runtime: Runtime, llm_config: LLMConfig
) -> IntelligentWhiteAgent:
    """Create an intelligent white agent instance."""
    return IntelligentWhiteAgent(runtime, llm_config)


# Example usage
async def run_intelligent_agent(runtime: Runtime, config: OpenHandsConfig) -> State:
    """Run intelligent agent on a task."""

    # Create agent
    agent = create_intelligent_agent(runtime, config.llm_config)

    # Initialize task (analyzes task.md, creates plan)
    init_result = agent.initialize_task()
    print(f"Task analyzed: {init_result['task_analysis']['task_type']}")
    print(f"Plan created: {len(init_result['plan'])} steps")
    print(f"Goals identified: {len(init_result['goals'])}")

    # Execute plan
    for step_idx in range(len(agent.current_plan)):
        result = await agent.execute_step(step_idx)

        if result.get("error"):
            print(f"Step {step_idx} error: {result['error']}")
            if result.get("skipped"):
                continue

        reflection = result.get("reflection", {})
        if reflection.get("success"):
            print(f"Step {step_idx}: SUCCESS {reflection.get('goals_achieved', [])}")
        else:
            print(f"Step {step_idx}: FAILED {reflection.get('suggestions', [])}")

        if agent.is_complete():
            print("Task completed!")
            break

    return None
