"""
Scoring functions for comparing agent trajectories to golden paths.

Provides path similarity, redundancy detection, efficiency
scoring, and report generation.
"""

from typing import List, Dict
from difflib import SequenceMatcher
import re

def normalize_action(action: str) -> str:
    """
    Normalize an action string for comparison.
    Remove content like URLs, file paths, message content, etc.
    """
    action_type_match = re.match(r'^(\w+)\(', action)
    if not action_type_match:
        return action
    
    action_type = action_type_match.group(1)
    
    if action_type == 'execute_bash':
        return action_type
    elif action_type == 'send_message':
        recipient_match = re.search(r"recipient='([^']+)'", action)
        if recipient_match:
            return f"{action_type}(recipient='{recipient_match.group(1)}')"
        return action_type
    elif action_type == 'goto_url':
        url_match = re.search(r"url='([^']+)'", action)
        if url_match:
            url = url_match.group(1)
            domain_match = re.search(r'://([^/]+)(/.*)?', url)
            if domain_match:
                domain = domain_match.group(1)
                path = domain_match.group(2) or ''
                if '/channel/' in path:
                    return f"{action_type}(channel)"
                elif '/direct/' in path:
                    return f"{action_type}(direct)"
                elif '/directory/' in path:
                    return f"{action_type}(directory)"
                return f"{action_type}({domain})"
        return action_type
    elif action_type in ['read_file', 'write_file']:
        path_match = re.search(r"path='([^']+)'", action)
        if path_match:
            path = path_match.group(1)
            if '/workspace/' in path:
                return f"{action_type}(workspace)"
            elif '/Documents/' in path:
                return f"{action_type}(Documents)"
            elif '/instruction/' in path:
                return f"{action_type}(instruction)"
            return f"{action_type}({path.split('/')[-1]})"
        return action_type
    elif action_type == 'finish':
        return action_type
    
    return action

def calculate_path_similarity(agent_path: List[str], golden_path: List[str]) -> float:
    """
    Calculate similarity between agent path and golden path using sequence alignment.
    Returns a score between 0 and 1, where 1 is perfect match.
    """
    if not agent_path or not golden_path:
        return 0.0
    
    normalized_agent = [normalize_action(action) for action in agent_path]
    normalized_golden = [normalize_action(action) for action in golden_path]
    
    matcher = SequenceMatcher(None, normalized_golden, normalized_agent)
    similarity = matcher.ratio()
    
    return similarity


def detect_redundancy(agent_path: List[str]) -> float:
    """
    Detect redundant actions in the agent path.
    Returns a penalty score between 0 and 1, where 1 is the most redundant.
    """
    if len(agent_path) <= 1:
        return 0.0
    
    normalized_actions = [normalize_action(action) for action in agent_path]
    action_counts = {}
    
    for action in normalized_actions:
        action_counts[action] = action_counts.get(action, 0) + 1
    
    total_duplicates = sum(count - 1 for count in action_counts.values() if count > 1)
    redundancy_penalty = min(total_duplicates / len(agent_path), 1.0)
    
    return redundancy_penalty

def calculate_efficiency_score(
    agent_path: List[str],
    golden_path: List[str],
    path_similarity_weight: float = 0.7,
    redundancy_penalty_weight: float = 0.3
) -> Dict[str, float]:
    """
    Calculate overall efficiency score comparing agent path to golden path.
    
    Args:
        agent_path: List of standardized action strings from agent trajectory
        golden_path: List of standardized action strings from golden path
        path_similarity_weight: Weight for path similarity component (0-1)
        redundancy_penalty_weight: Weight for redundancy penalty (0-1)
    
    Returns:
        Dictionary containing:
        - efficiency_score: Overall score (0-100)
        - path_similarity: Similarity score (0-1)
        - redundancy_penalty: Redundancy penalty (0-1)
        - path_length_ratio: Ratio of agent path length to golden path length
    """
    path_similarity = calculate_path_similarity(agent_path, golden_path)
    
    redundancy_penalty = detect_redundancy(agent_path)
    
    if len(golden_path) > 0:
        path_length_ratio = len(agent_path) / len(golden_path)
    else:
        path_length_ratio = float('inf') if agent_path else 1.0
    
    efficiency_score = (
        path_similarity_weight * path_similarity * 100 -
        redundancy_penalty_weight * redundancy_penalty * 100
    )
    
    efficiency_score = max(0, min(100, efficiency_score))
    
    return {
        'efficiency_score': efficiency_score,
        'path_similarity': path_similarity,
        'redundancy_penalty': redundancy_penalty,
        'path_length_ratio': path_length_ratio,
        'agent_path_length': len(agent_path),
        'golden_path_length': len(golden_path)
    }

def generate_diagnostic_report(
    agent_path: List[str],
    golden_path: List[str],
    scores: Dict[str, float]
) -> str:
    """
    Generate a report comparing agent path to golden path.
    """
    report = []
    report.append("=" * 60)
    report.append("EFFICIENCY EVALUATION REPORT")
    report.append("=" * 60)
    report.append("")
    
    report.append(f"Overall Efficiency Score: {scores['efficiency_score']:.2f}/100")
    report.append("")
    
    report.append("Component Scores:")
    report.append(f"  Path Similarity: {scores['path_similarity']:.3f} (0-1)")
    report.append(f"  Redundancy Penalty: {scores['redundancy_penalty']:.3f} (0-1)")
    report.append(f"  Path Length Ratio: {scores['path_length_ratio']:.2f}x")
    report.append("")
    
    report.append("Path Comparison:")
    report.append(f"  Golden Path Length: {scores['golden_path_length']} actions")
    report.append(f"  Agent Path Length: {scores['agent_path_length']} actions")
    report.append("")
    
    report.append("Golden Path Actions:")
    for i, action in enumerate(golden_path, 1):
        report.append(f"  {i}. {action}")
    report.append("")
    
    report.append("Agent Path Actions:")
    for i, action in enumerate(agent_path, 1):
        report.append(f"  {i}. {action}")
    report.append("")
    
    report.append("Summary of results:")
    if scores['path_similarity'] < 0.5:
        report.append("  - Agent path deviates significantly from optimal path")
    if scores['redundancy_penalty'] > 0.3:
        report.append("  - High redundancy")
    if scores['path_length_ratio'] > 1.5:
        report.append("  - Agent path is significantly longer than optimal")
    if scores['path_length_ratio'] < 0.7:
        report.append("  - Agent path is shorter than expected")
    
    report.append("=" * 60)
    
    return "\n".join(report)
