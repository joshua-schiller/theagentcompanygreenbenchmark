"""
Scoring functions for comparing agent trajectories to golden paths.

Provides path similarity, redundancy detection, efficiency
scoring, and report generation.
"""

from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
import re

def normalize_action_for_matching(action: str) -> str:
    """
    Normalize an action string for matching comparison.
    Keeps more detail than before - preserves action types, recipients, file paths.
    Only normalizes truly variable content like message text and specific URLs.
    """
    action_type_match = re.match(r'^(\w+)\(', action)
    if not action_type_match:
        return action.lower().strip()
    
    action_type = action_type_match.group(1)
    
    if action_type == 'execute_bash':
        # Keep command structure but normalize whitespace and quotes
        command_match = re.search(r"command='([^']+)'", action)
        if command_match:
            command = command_match.group(1)
            # Normalize whitespace but keep command structure
            command = re.sub(r'\s+', ' ', command.strip())
            return f"{action_type}(command_normalized)"
        return f"{action_type}()"
    
    elif action_type == 'send_message':
        # Keep recipient if present
        recipient_match = re.search(r"recipient='([^']+)'", action)
        if recipient_match:
            recipient = recipient_match.group(1)
            return f"{action_type}(recipient='{recipient}')"
        # No recipient means it's a channel message
        return f"{action_type}(channel)"
    
    elif action_type == 'goto_url':
        # Keep domain and path type
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
                elif '/home' in path:
                    return f"{action_type}(home)"
                return f"{action_type}({domain})"
        return f"{action_type}()"
    
    elif action_type in ['read_file', 'write_file']:
        # Keep file path structure but normalize
        path_match = re.search(r"path='([^']+)'", action)
        if path_match:
            path = path_match.group(1)
            # Keep directory structure
            if '/workspace/' in path:
                filename = path.split('/')[-1]
                return f"{action_type}(workspace/{filename})"
            elif '/Documents/' in path:
                # Keep subdirectory structure
                parts = path.split('/Documents/')
                if len(parts) > 1:
                    subpath = parts[1]
                    return f"{action_type}(Documents/{subpath.split('/')[0]})"
                return f"{action_type}(Documents)"
            elif '/instruction/' in path:
                filename = path.split('/')[-1]
                return f"{action_type}(instruction/{filename})"
            return f"{action_type}({path.split('/')[-1]})"
        return f"{action_type}()"
    
    elif action_type == 'finish':
        return 'finish()'
    
    return action.lower().strip()

def action_similarity(action_1: str, action_2: str) -> float:
    """
    Calculate similarity between two actions using normalized comparison.
    """
    norm_1 = normalize_action_for_matching(action_1)
    norm_2 = normalize_action_for_matching(action_2)
    
    # Exact match after normalization
    if norm_1 == norm_2:
        return 1.0
    
    # Use SequenceMatcher for fuzzy matching
    return SequenceMatcher(None, norm_1, norm_2).ratio()

def align_golden_to_agent(
    golden_path: List[str],
    agent_path: List[str],
    min_similarity: float = 0.45
) -> Tuple[List[Tuple[Optional[str], Optional[str], float]], set[int]]:
    """
    Align golden path steps to agent path steps using greedy matching.
    Returns list of (golden_action, matched_agent_action, similarity) tuples
    and set of used agent indices.
    """
    matches: List[Tuple[Optional[str], Optional[str], float]] = []
    used_indices: set[int] = set()
    
    for golden_action in golden_path:
        best_idx = None
        best_score = 0.0
        
        for idx, agent_action in enumerate(agent_path):
            if idx in used_indices:
                continue
            
            score = action_similarity(golden_action, agent_action)
            if score > best_score:
                best_score = score
                best_idx = idx
        
        if best_idx is not None and best_score >= min_similarity:
            used_indices.add(best_idx)
            matches.append((golden_action, agent_path[best_idx], best_score))
        else:
            matches.append((golden_action, None, 0.0))
    
    return matches, used_indices

def calculate_coverage_score(
    golden_path: List[str],
    agent_path: List[str],
    min_similarity: float = 0.45
) -> Dict[str, float]:
    """
    Calculate coverage-based similarity: how many golden path steps were matched.
    Returns coverage score (0-1) and order score (0-1).
    """
    if not golden_path:
        return {'coverage': 1.0, 'order_score': 1.0, 'matched_count': 0, 'total_count': 0}
    
    if not agent_path:
        return {'coverage': 0.0, 'order_score': 0.0, 'matched_count': 0, 'total_count': len(golden_path)}
    
    matches, used_indices = align_golden_to_agent(golden_path, agent_path, min_similarity)
    
    # Coverage: how many golden steps were matched
    matched_count = sum(1 for _, matched, _ in matches if matched is not None)
    coverage = matched_count / len(golden_path)
    
    # Order score: how well the order matches (reward matching in sequence)
    order_score = 0.0
    if matched_count > 0:
        matched_indices = [i for i, (_, matched, _) in enumerate(matches) if matched is not None]
        if len(matched_indices) > 1:
            # Check if matched steps are in increasing order
            is_ordered = all(matched_indices[i] < matched_indices[i+1] 
                           for i in range(len(matched_indices) - 1))
            if is_ordered:
                order_score = 1.0
            else:
                # Partial order score based on how many are in order
                ordered_pairs = sum(1 for i in range(len(matched_indices) - 1)
                                  if matched_indices[i] < matched_indices[i+1])
                order_score = ordered_pairs / (len(matched_indices) - 1) if len(matched_indices) > 1 else 1.0
        else:
            order_score = 1.0
    
    # Average similarity of matched steps
    matched_similarities = [sim for _, _, sim in matches if sim > 0]
    avg_similarity = sum(matched_similarities) / len(matched_similarities) if matched_similarities else 0.0
    
    return {
        'coverage': coverage,
        'order_score': order_score,
        'matched_count': matched_count,
        'total_count': len(golden_path),
        'avg_similarity': avg_similarity
    }

def detect_harmful_redundancy(agent_path: List[str], window_size: int = 5) -> float:
    """
    Detect harmful redundancy: repeated identical actions within a context window.
    Only penalizes true redundancy, not legitimate repetition (e.g., different files, recipients).
    Returns a penalty score between 0 and 1.
    """
    if len(agent_path) <= 1:
        return 0.0
    
    normalized_actions = [normalize_action_for_matching(action) for action in agent_path]
    
    redundancy_count = 0
    total_windows = 0
    
    # Check redundancy within sliding windows
    for i in range(len(normalized_actions) - window_size + 1):
        window = normalized_actions[i:i + window_size]
        total_windows += 1
        
        # Count duplicates in this window
        action_counts = {}
        for action in window:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        # Penalize actions that appear 3+ times in the window
        for action, count in action_counts.items():
            if count >= 3:
                redundancy_count += (count - 2)  # Penalty for 3rd+ occurrence
    
    # Also check overall redundancy for very repetitive patterns
    overall_counts = {}
    for action in normalized_actions:
        overall_counts[action] = overall_counts.get(action, 0) + 1
    
    # Penalize actions that appear many times overall (e.g., 10+ times)
    excessive_redundancy = 0
    for action, count in overall_counts.items():
        if count >= 10:
            excessive_redundancy += (count - 9)  # Penalty for 10th+ occurrence
    
    # Combine window-based and overall redundancy
    window_penalty = min(redundancy_count / max(len(agent_path), 1), 1.0) if total_windows > 0 else 0.0
    overall_penalty = min(excessive_redundancy / max(len(agent_path), 1), 1.0)
    
    # Take the maximum (worst case)
    redundancy_penalty = min(max(window_penalty, overall_penalty * 0.5), 1.0)
    
    return redundancy_penalty

def calculate_path_length_efficiency(agent_path_length: int, golden_path_length: int, coverage: float = 1.0) -> float:
    """
    Calculate efficiency penalty/bonus based on path length ratio.
    Returns a score between 0 and 1, where 1 is optimal length.
    Reduces penalties when coverage is high (≥0.9).
    """
    if golden_path_length == 0:
        return 1.0 if agent_path_length == 0 else 0.0
    
    ratio = agent_path_length / golden_path_length
    
    # Base penalties
    if ratio <= 1.0:
        # Shorter or equal is fine (might have skipped unnecessary steps)
        return 1.0
    elif ratio <= 1.5:
        # Slightly longer is acceptable
        base_penalty = (ratio - 1.0) * 0.2
    elif ratio <= 2.0:
        # Moderately longer
        base_penalty = 0.1 + (ratio - 1.5) * 0.3
    else:
        # Significantly longer
        base_penalty = 0.25 + (ratio - 2.0) * 0.15
        base_penalty = min(base_penalty, 0.5)  # Cap maximum penalty
    
    # Reduce penalty by 50% if coverage is high (≥0.9)
    if coverage >= 0.9:
        base_penalty = base_penalty * 0.5
    
    return max(0.0, 1.0 - base_penalty)

def calculate_efficiency_score(
    agent_path: List[str],
    golden_path: List[str],
    coverage_weight: float = 0.6,
    order_weight: float = 0.15,
    length_weight: float = 0.1,
    redundancy_weight: float = 0.15
) -> Dict[str, float]:
    """
    Calculate overall efficiency score comparing agent path to golden path.
    Uses coverage-based scoring instead of sequence similarity.
    Rewards complete paths more heavily.
    
    Args:
        agent_path: List of standardized action strings from agent trajectory
        golden_path: List of standardized action strings from golden path
        coverage_weight: Weight for coverage component (default 0.6, increased)
        order_weight: Weight for order preservation (default 0.15)
        length_weight: Weight for path length efficiency (default 0.1, reduced)
        redundancy_weight: Weight for redundancy penalty (default 0.15, reduced)
    
    Returns:
        Dictionary containing:
        - efficiency_score: Overall score (0-100)
        - coverage: Coverage score (0-1)
        - order_score: Order preservation score (0-1)
        - length_efficiency: Path length efficiency (0-1)
        - redundancy_penalty: Redundancy penalty (0-1)
        - path_similarity: Legacy compatibility (coverage score)
        - path_length_ratio: Ratio of agent path length to golden path length
        - completeness_bonus: Bonus points for perfect coverage and order
    """
    # Calculate coverage-based metrics
    coverage_metrics = calculate_coverage_score(golden_path, agent_path)
    coverage = coverage_metrics['coverage']
    order_score = coverage_metrics['order_score']
    
    # Calculate path length efficiency (with coverage-aware penalty reduction)
    length_efficiency = calculate_path_length_efficiency(len(agent_path), len(golden_path), coverage)
    
    # Calculate harmful redundancy
    redundancy_penalty_raw = detect_harmful_redundancy(agent_path)
    
    # Reduce redundancy penalty by 50% if coverage is high (≥0.9)
    if coverage >= 0.9:
        redundancy_penalty = redundancy_penalty_raw * 0.5
    else:
        redundancy_penalty = redundancy_penalty_raw
    
    # Cap total penalties when coverage is perfect
    if coverage >= 1.0:
        # Maximum total penalty is 15 points when coverage is perfect
        length_penalty = (1.0 - length_efficiency) * length_weight * 100
        redundancy_penalty_points = redundancy_penalty * redundancy_weight * 100
        total_penalty = length_penalty + redundancy_penalty_points
        if total_penalty > 15:
            # Scale down penalties proportionally
            scale_factor = 15 / total_penalty
            length_efficiency = 1.0 - (1.0 - length_efficiency) * scale_factor
            redundancy_penalty = redundancy_penalty * scale_factor
    
    # Calculate completeness bonus
    completeness_bonus = 0.0
    if coverage >= 1.0 and order_score >= 0.9:
        completeness_bonus = 10.0  # 10 point bonus for perfect coverage and good order
    
    # Calculate path length ratio
    if len(golden_path) > 0:
        path_length_ratio = len(agent_path) / len(golden_path)
    else:
        path_length_ratio = float('inf') if agent_path else 1.0
    
    # Calculate efficiency score using weighted components
    efficiency_score = (
        coverage_weight * coverage * 100 +
        order_weight * order_score * 100 +
        length_weight * length_efficiency * 100 -
        redundancy_weight * redundancy_penalty * 100 +
        completeness_bonus
    )
    
    efficiency_score = max(0, min(100, efficiency_score))
    
    return {
        'efficiency_score': efficiency_score,
        'coverage': coverage,
        'order_score': order_score,
        'length_efficiency': length_efficiency,
        'redundancy_penalty': redundancy_penalty,
        'path_similarity': coverage,  # Legacy compatibility
        'path_length_ratio': path_length_ratio,
        'agent_path_length': len(agent_path),
        'golden_path_length': len(golden_path),
        'matched_count': coverage_metrics['matched_count'],
        'total_count': coverage_metrics['total_count'],
        'avg_similarity': coverage_metrics['avg_similarity'],
        'completeness_bonus': completeness_bonus
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
    report.append(f"  Coverage: {scores['coverage']:.3f} ({scores.get('matched_count', 0)}/{scores.get('total_count', 0)} golden steps matched)")
    report.append(f"  Order Score: {scores['order_score']:.3f} (0-1)")
    report.append(f"  Length Efficiency: {scores['length_efficiency']:.3f} (0-1)")
    report.append(f"  Redundancy Penalty: {scores['redundancy_penalty']:.3f} (0-1)")
    report.append(f"  Path Length Ratio: {scores['path_length_ratio']:.2f}x")
    if 'avg_similarity' in scores:
        report.append(f"  Average Match Similarity: {scores['avg_similarity']:.3f}")
    if 'completeness_bonus' in scores and scores['completeness_bonus'] > 0:
        report.append(f"  Completeness Bonus: +{scores['completeness_bonus']:.1f} points")
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
    if scores['coverage'] < 0.5:
        report.append("  - Agent path covers less than half of optimal steps")
    elif scores['coverage'] < 0.8:
        report.append("  - Agent path covers most optimal steps")
    else:
        report.append("  - Agent path covers most/all optimal steps")
    
    if scores['redundancy_penalty'] > 0.3:
        report.append("  - High redundancy detected")
    if scores['path_length_ratio'] > 2.0:
        report.append("  - Agent path is significantly longer than optimal")
    elif scores['path_length_ratio'] > 1.5:
        report.append("  - Agent path is moderately longer than optimal")
    if scores['path_length_ratio'] < 0.7:
        report.append("  - Agent path is shorter than expected (may be missing steps)")
    
    report.append("=" * 60)
    
    return "\n".join(report)
