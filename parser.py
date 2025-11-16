import json
import re


def parse_trajectory(json_log_path):
    """
    Parse a trajectory JSON log file and extract standardized major actions.
    
    Args:
        json_log_path: Path to the JSON log file
        
    Returns:
        List of standardized action strings
    """
    with open(json_log_path, 'r') as f:
        data = json.load(f)
    
    actions = []
    
    # Convert to list with indices for look-ahead capability
    data_list = list(data)
    
    for idx, obj in enumerate(data_list):
        # Filter: Only process objects where source is "agent" and action exists
        # Skip observations (objects with observation key)
        if obj.get('source') != 'agent':
            continue
        if 'observation' in obj:
            continue
        if 'action' not in obj:
            continue
        
        action_type = obj.get('action')
        args = obj.get('args', {})
        
        # Handle different action types
        if action_type == 'run':
            # execute_bash: extract command from args['command']
            if 'command' in args:
                cmd = args['command']
                actions.append(f"execute_bash(command='{cmd}')")
        
        elif action_type == 'run_ipython':
            # read_file or write_file: parse args['code'] to find file_editor calls
            if 'code' in args:
                code = args['code']
                # Look for file_editor(**{'command': '...', 'path': '...'})
                # Pattern: file_editor(**{'command': 'view', 'path': '...'})
                # or file_editor(**{'command': 'create', 'path': '...'})
                # or file_editor(**{'command': 'insert', 'path': '...'})
                # or file_editor(**{'command': 'str_replace', 'path': '...'})
                
                # Extract path using regex
                path_match = re.search(r"'path':\s*'([^']+)'", code)
                if path_match:
                    path = path_match.group(1)
                    
                    # Check for command type
                    command_match = re.search(r"'command':\s*'([^']+)'", code)
                    if command_match:
                        command = command_match.group(1)
                        
                        if command == 'view':
                            actions.append(f"read_file(path='{path}')")
                        elif command in ['create', 'insert', 'str_replace']:
                            actions.append(f"write_file(path='{path}')")
        
        elif action_type == 'browse_interactive':
            # goto_url or send_message: parse args['browser_actions']
            if 'browser_actions' in args:
                browser_actions = args['browser_actions']
                
                # Check for goto('...')
                goto_match = re.search(r"goto\(['\"]([^'\"]+)['\"]\)", browser_actions)
                if goto_match:
                    url = goto_match.group(1)
                    actions.append(f"goto_url(url='{url}')")
                    continue
                
                # Check for send_message: fill('...', '...') followed by press(..., 'Enter') or click(...)
                # We need to find fill('...', '...') and extract the second argument (message content)
                # Then check if it's followed by press(..., 'Enter') or click(...)
                # Improved regex to handle messages with quotes and special characters
                # Pattern: fill(quote1...quote1, quote2...quote2) where quotes can be ' or "
                # Use non-greedy matching with backreferences to handle the closing quote properly
                fill_match = re.search(r"fill\((['\"])(.*?)\1\s*,\s*(['\"])(.*?)\3\)", browser_actions, re.DOTALL)
                if fill_match:
                    # Check if followed by press(..., 'Enter') or click(...) in the same action
                    has_press_or_click = re.search(r"(press\([^)]*['\"]Enter['\"]\)|click\([^)]*\))", browser_actions)
                    
                    # Also check if the next agent action has a click (for cases where fill and click are separate)
                    if not has_press_or_click:
                        # Look ahead in the data list to find the next agent action
                        for look_ahead_idx in range(idx + 1, min(idx + 5, len(data_list))):
                            next_obj = data_list[look_ahead_idx]
                            if (next_obj.get('source') == 'agent' 
                                and 'observation' not in next_obj
                                and 'action' in next_obj):
                                if next_obj.get('action') == 'browse_interactive':
                                    next_ba = next_obj.get('args', {}).get('browser_actions', '')
                                    if 'click' in next_ba and 'fill' not in next_ba:
                                        has_press_or_click = True
                                        break
                                else:
                                    # If we hit a non-browse_interactive action, stop looking
                                    break
                    
                    if has_press_or_click:
                        message = fill_match.group(4)  # Fourth group is the message content (second argument)
                        
                        # Try to extract recipient from message content
                        # Pattern: "Hello [Name]," or "Hello [Name]!" or "Hello [Name] "
                        recipient = None
                        hello_match = re.search(r"Hello\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", message)
                        if hello_match:
                            recipient = hello_match.group(1)
                        
                        # If recipient found, include it in the output
                        if recipient:
                            actions.append(f"send_message(recipient='{recipient}', content='{message}')")
                        else:
                            actions.append(f"send_message(content='{message}')")
        
        elif action_type == 'finish':
            actions.append("finish()")
    
    return actions


if __name__ == '__main__':
    # List of example JSON files
    json_files = [
        'traj_sde-run-janusgraph-image.json',
        'traj_pm-schedule-meeting-2-image-claude.json',
        'traj_hr-new-grad-job-description-3-image.json'
    ]
    
    # Output file name
    output_file = 'parsed_actions_output.txt'
    
    # Process each file and write to output file
    with open(output_file, 'w') as out_f:
        for filename in json_files:
            print(f"\n{filename}:")
            out_f.write(f"\n{filename}:\n")
            try:
                actions = parse_trajectory(filename)
                # Write as formatted JSON for readability
                output_json = json.dumps(actions, indent=2)
                print(output_json)
                out_f.write(output_json)
                out_f.write("\n")
            except Exception as e:
                error_msg = f"Error processing {filename}: {e}"
                print(error_msg)
                out_f.write(error_msg + "\n")
    
    print(f"\nOutput written to {output_file}")

