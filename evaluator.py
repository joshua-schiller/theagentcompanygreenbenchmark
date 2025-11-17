"""
Main Green Agent Evaluator

Evaluates white agent trajectories by comparing them to golden paths
and calculating efficiency scores.
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List
from parser import parse_trajectory
from golden_paths import get_golden_path, get_all_task_names
from scoring import calculate_efficiency_score, generate_diagnostic_report

def extract_task_name_from_filename(filename: str) -> str:
    """
    Extract task name from trajectory filename.
    Ex: 'traj_pm-schedule-meeting-1-image.json' -> 'pm-schedule-meeting-1'
    """
    task_name = filename.replace('traj_', '').replace('-image.json', '').replace('.json', '')
    return task_name

def evaluate_trajectory(trajectory_path: str, task_name: str = None) -> Dict:
    """
    Evaluate a single trajectory file.
    """
    if task_name is None:
        filename = Path(trajectory_path).name
        task_name = extract_task_name_from_filename(filename)
    
    try:
        agent_path = parse_trajectory(trajectory_path)
    except FileNotFoundError:
        return {
            'error': f'Trajectory file not found: {trajectory_path}',
            'task_name': task_name
        }
    except Exception as e:
        return {
            'error': f'Error parsing trajectory: {e}',
            'task_name': task_name
        }
    
    golden_path = get_golden_path(task_name)
    if not golden_path:
        return {
            'error': f'No golden path found for task: {task_name}',
            'task_name': task_name,
            'agent_path': agent_path
        }
    
    scores = calculate_efficiency_score(agent_path, golden_path)
    report = generate_diagnostic_report(agent_path, golden_path, scores)
    
    return {
        'task_name': task_name,
        'trajectory_path': trajectory_path,
        'scores': scores,
        'agent_path': agent_path,
        'golden_path': golden_path,
        'diagnostic_report': report
    }

def evaluate_multiple_trajectories(trajectory_dir: str, output_file: str = None) -> Dict[str, Dict]:
    """
    Evaluate all trajectory files in a directory.
    
    Args:
        trajectory_dir: Directory containing trajectory JSON files
        output_file: Optional path to save results JSON
    
    Returns:
        Dictionary mapping task names to evaluation results
    """
    trajectory_dir = Path(trajectory_dir)
    results = {}
    
    trajectory_files = list(trajectory_dir.glob('traj_*.json'))
    
    if not trajectory_files:
        print(f"No trajectory files found in {trajectory_dir}")
        return results
        
    for traj_file in trajectory_files:
        print(f"\nEvaluating {traj_file.name}...")
        result = evaluate_trajectory(str(traj_file))
        task_name = result.get('task_name', traj_file.stem)
        results[task_name] = result
        
        if 'error' in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Efficiency Score: {result['scores']['efficiency_score']:.2f}/100")
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description='Green Agent Evaluator. Evaluate agent trajectory efficiency'
    )
    parser.add_argument(
        'trajectory',
        type=str,
        help='Path to trajectory JSON file or directory containing trajectory files'
    )
    parser.add_argument(
        '--task-name',
        type=str,
        default=None,
        help='Task name'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path for results in JSON format'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Print detailed report'
    )
    parser.add_argument(
        '--list-tasks',
        action='store_true',
        help='List all available task names'
    )
    
    args = parser.parse_args()
    
    if args.list_tasks:
        print("Available tasks:")
        for task_name in get_all_task_names():
            print(f" {task_name}")
        return
    
    input_path = Path(args.trajectory)
    
    if not input_path.exists():
        print(f"Error: Path does not exist: {args.trajectory}")
        sys.exit(1)
    
    if input_path.is_file():
        result = evaluate_trajectory(str(input_path), args.task_name)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Task: {result['task_name']}")
        print(f"Trajectory: {result['trajectory_path']}")
        print(f"\nEfficiency Score: {result['scores']['efficiency_score']:.2f}/100")
        print(f"Path Similarity: {result['scores']['path_similarity']:.3f}")
        print(f"Redundancy Penalty: {result['scores']['redundancy_penalty']:.3f}")
        print(f"Path Length Ratio: {result['scores']['path_length_ratio']:.2f}x")
        
        if args.report:
            print("\n" + result['diagnostic_report'])
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\nResults saved to {args.output}")
    
    elif input_path.is_dir():
        results = evaluate_multiple_trajectories(str(input_path), args.output)
        
        print("\n" + "=" * 60)
        print("BATCH EVALUATION SUMMARY")
        print("=" * 60)
        for task_name, result in results.items():
            if 'error' in result:
                print(f"{task_name}: ERROR - {result['error']}")
            else:
                print(f"{task_name}: {result['scores']['efficiency_score']:.2f}/100")
    
    else:
        print(f"Error: Path is neither a file nor directory: {args.trajectory}")
        sys.exit(1)


if __name__ == '__main__':
    main()


