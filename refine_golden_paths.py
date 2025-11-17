"""
Used for refining golden paths.

This script compares canonical golden path definitions against actual
agent trajectories and gives suggestions for updating the
golden paths.  Can be used in two modes:

1. Given a single trajectory JSON file, it will parse the actions,
   align them to the canonical golden path for the specified task,
   and produce a suggested refined path.
2. When multiple trajectories are available, you can run the script
   repeatedly and aggregate the suggestions.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from parser import parse_trajectory
from golden_paths import GOLDEN_PATHS

DEFAULT_DESCRIPTIONS_PATH = Path("golden_paths_descriptions.md")

@dataclass
class MatchResult:
    canonical: str
    matched: Optional[str]
    similarity: float

def load_description_file(path: Path) -> Dict[str, List[str]]:
    """
    Parse the description file and extract canonical action lists
    for every task.
    """
    if not path.exists():
        return {}

    tasks: Dict[str, List[str]] = {}
    current_task: Optional[str] = None
    current_actions: List[str] = []

    with path.open("r") as fh:
        for line in fh:
            clean_line = line.strip()
            if not clean_line:
                continue

            if clean_line.startswith("Task "):
                if current_task and current_actions:
                    tasks[current_task] = current_actions
                current_task = clean_line.split(":", 1)[1].strip()
                current_actions = []
                continue

            if clean_line.startswith("- ") and current_task:
                action = clean_line[2:].strip()
                current_actions.append(action)

        if current_task and current_actions:
            tasks[current_task] = current_actions

    return tasks

def normalize_action(action: str) -> str:
    """
    Normalize an action string for fuzzy comparison.
    Cleans the string.
    """
    action = action.strip().lower()
    action = re.sub(r"'[^']*'", "''", action)
    action = re.sub(r'"[^"]*"', '""', action)
    action = re.sub(r"\s+", " ", action)
    return action

def action_similarity(action_1: str, action_2: str) -> float:
    return SequenceMatcher(None, normalize_action(action_1), normalize_action(action_2)).ratio()

def align_actions(
    canonical_actions: Sequence[str],
    parsed_actions: Sequence[str],
    min_similarity: float = 0.45,
) -> tuple[List[MatchResult], set[int]]:
    """
    Align canonical actions to parsed actions using greedy matching with
    SequenceMatcher similarity.
    """
    matches: List[MatchResult] = []
    used_indices: set[int] = set()

    for canonical in canonical_actions:
        best_idx = None
        best_score = 0.0

        for idx, parsed in enumerate(parsed_actions):
            if idx in used_indices:
                continue
            score = action_similarity(canonical, parsed)
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is not None and best_score >= min_similarity:
            used_indices.add(best_idx)
            matches.append(
                MatchResult(
                    canonical=canonical,
                    matched=parsed_actions[best_idx],
                    similarity=best_score,
                )
            )
        else:
            matches.append(MatchResult(canonical=canonical, matched=None, similarity=0.0))

    return matches, used_indices

def refine_golden_path(
    task_name: str,
    parsed_actions: Sequence[str],
    canonical_actions: Sequence[str],
    min_similarity: float = 0.45,
) -> Dict[str, object]:
    matches, matched_indices = align_actions(
        canonical_actions, parsed_actions, min_similarity
    )
    suggested_path = [m.matched or m.canonical for m in matches]
    unmatched_parsed = [
        action for idx, action in enumerate(parsed_actions) if idx not in matched_indices
    ]

    return {
        "task_name": task_name,
        "suggested_golden_path": suggested_path,
        "matches": [
            {
                "canonical": match.canonical,
                "matched": match.matched,
                "similarity": match.similarity,
            }
            for match in matches
        ],
        "unmatched_parsed_actions": unmatched_parsed,
        "parsed_action_count": len(parsed_actions),
    }

def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Refine golden paths using actual agent trajectories."
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Task name",
    )
    parser.add_argument(
        "--trajectory",
        required=True,
        help="Path to trajectory JSON file produced by TheAgentCompany benchmark.",
    )
    parser.add_argument(
        "--descriptions",
        default=str(DEFAULT_DESCRIPTIONS_PATH),
        help="Path to golden path descriptions .md file.",
    )
    parser.add_argument(
        "--min-similarity",
        type=float,
        default=0.45,
        help="Minimum similarity required to align actions.",
    )
    parser.add_argument(
        "--save-json",
        help="Optional path to save refinement output JSON.",
    )
    parser.add_argument(
        "--print-parsed",
        action="store_true",
        help="Print parsed actions before refinement.",
    )
    return parser


def main() -> None:
    cli = build_cli()
    args = cli.parse_args()

    task_name = args.task.strip()
    trajectory_path = Path(args.trajectory)

    if not trajectory_path.exists():
        cli.error(f"Trajectory file not found: {trajectory_path}")

    parsed_actions = parse_trajectory(str(trajectory_path))
    if args.print_parsed:
        print("\nParsed actions:")
        print(json.dumps(parsed_actions, indent=2))

    descriptions = load_description_file(Path(args.descriptions))
    canonical_actions = descriptions.get(task_name) or GOLDEN_PATHS.get(task_name)

    if not canonical_actions:
        cli.error(
            f"No canonical actions for task '{task_name}'. "
        )

    refinement = refine_golden_path(
        task_name=task_name,
        parsed_actions=parsed_actions,
        canonical_actions=canonical_actions,
        min_similarity=args.min_similarity,
    )

    print("\n***Refinement Summary***")
    print(f"Task: {task_name}")
    print(f"Trajectory: {trajectory_path}")
    print(f"Parsed actions: {refinement['parsed_action_count']}")
    print("Suggested Golden Path:")
    for idx, action in enumerate(refinement["suggested_golden_path"], start=1):
        print(f"  {idx}. {action}")

    print("\nMatches:")
    for match in refinement["matches"]:
        status = "MATCH" if match["matched"] else "NO MATCH"
        print(
            f"  {status:<8} | canonical: {match['canonical']} "
            f"| matched: {match['matched']} | similarity: {match['similarity']:.3f}"
        )

    if refinement["unmatched_parsed_actions"]:
        print("\nUnmatched parsed actions (potential extras/noise):")
        for action in refinement["unmatched_parsed_actions"]:
            print(f"  - {action}")

    if args.save_json:
        output_path = Path(args.save_json)
        output_path.write_text(json.dumps(refinement, indent=2))
        print(f"\nSaved refinement output to {output_path}")


if __name__ == "__main__":
    main()

