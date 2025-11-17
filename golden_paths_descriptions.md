Golden Paths Descriptions

Here we define the optimal action sequences, or Golden Paths, for each of the 10 tasks in our Green Agent evaluation. Our paths focus on only essential actions and avoid redundancy. Note that some tasks may have minor variations that can still be considered optimal. 

The parser output format will be used to create programmatic versions of these paths. Each path has been cross-validated by our team members to ensure accuracy.


Task 1: pm-schedule-meeting-1

Goal: Schedule a meeting between Emily Zhou and Liu Qiang.

Golden Path
1. Navigate to RocketChat (http://the-agent-company.com:3000/home)
- goto_url(url='http://the-agent-company.com:3000/home')
2. Send message to Emily Zhou asking for availabilities
- send_message(recipient='Emily Zhou', content='...')
3. Send message to Liu Qiang asking for availabilities
- send_message(recipient='Liu Qiang', content='...')
4. Create conclusion.txt file with meeting schedule in /workspace/conclusion.txt
- write_file(path='/workspace/conclusion.txt')
5. Finish
- finish()


Task 2: sde-run-janusgraph

Goal: Set up JanusGraph and run locally with HTTP endpoint on port 8182.

Golden Path:
1. Clone JanusGraph repository from GitLab
- execute_bash(command='cd /workspace && git clone http://the-agent-company.com:8929/root/janusgraph')
2. Build the binary
- execute_bash(command='cd /workspace/janusgraph && [build command]')
3. Launch JanusGraph server on port 8182
- execute_bash(command='cd /workspace/janusgraph && [start server on port 8182]')
4. Finish
- finish()


Task 3: hr-new-grad-job-description-3

Goal: Create a job description by gathering info from Zhang Wei and Li Ming, then create file on OwnCloud.

Golden Path:
1. Navigate to RocketChat
- goto_url(url='http://the-agent-company.com:3000/home')
2. Send message to Zhang Wei asking about job responsibilities
- send_message(recipient='Zhang Wei', content='...')
3. Send message to Li Ming asking about template location, qualifications, salary
- send_message(recipient='Li Ming', content='...')
4. Read template file if needed
- read_file()
5. Navigate to OwnCloud
- goto_url(url='http://the-agent-company.com:8092/')
6. Create job_description.md file
- write_file(path='/Documents/job_description.md')
7. Create share link and save to link.txt
- write_file(path='/workspace/link.txt')
8. Finish
- finish()


Task 4: sde-create-new-repo

Goal: Ask Zhang Wei about project, create new GitLab repo, and update README.

Golden Path:
1. Navigate to RocketChat
- goto_url(url='http://the-agent-company.com:3000/')
2. Send message to Zhang Wei asking about project and tasks
- send_message(recipient='Zhang Wei', content='...')
3. Create new GitLab repo "New Storage Project"
- execute_bash(command='[create repo command]') or API call
4. Update README.md
- write_file(path='[repo path]/README.md')
5. Finish
- finish()


Task 5: pm-send-hello-message

Goal: Send a message to general channel and notify active users.

Golden Path:
1. Navigate to RocketChat directory
- goto_url(url='http://the-agent-company.com:3000/home')
2. Navigate to general channel
- goto_url(url='[general channel URL]')
3. Send message with required content
- send_message(content='... and @active_users')
4. Finish task
- finish()


Task 6: finance-qualified-bill-ask-for-reimburse

Goal: Find receipt, read reimbursement policy, calculate amount to reimburse, tell Mike Chen.

Golden Path:
1. Navigate to OwnCloud
- goto_url(url='http://the-agent-company.com:8092/')
2. Navigate to receipt file location
- goto_url(url='[receipt path]')
3. Read reimbursement PDF
- read_file(path='/Documents/Administrative Specialist/Reimbursement Policy.pdf')
4. Navigate to RocketChat
- goto_url(url='http://the-agent-company.com:3000/')
5. Send message to Mike Chen with amount to reimburse
- send_message(recipient='Mike Chen', content='...')
6. Finish
- finish()


Task 7: ds-janusgraph-exercise

Goal: Implement organizational chart in JanusGraph matching employee_diagram.jpg.

Golden Path:
1. Clone JanusGraph repository
- execute_bash(command='cd /workspace && git clone http://the-agent-company.com:8929/root/janusgraph')
2. Launch JanusGraph server on port 8182 in websocket mode
- execute_bash(command='cd /workspace/janusgraph && [start server]')
3. Read employee_diagram.jpg to understand structure
- read_file(path='/workspace/employee_diagram.jpg')
4. Create Python script to build graph
- write_file(path='/workspace/create_org_chart.py')
5. Execute script to create vertices and edges
- execute_bash(command='cd /workspace && python create_org_chart.py')
6. Finish
- finish()


Task 8: ml-generate-gradcam

Goal: Generate GradCAM visualization for test image using ResNet18.

Golden Path:
1. Navigate to OwnCloud
- goto_url(url='http://the-agent-company.com:8092/')
2. Download test_image.jpg from Documents/Research
- read_file(path='/Documents/Research/test_image.jpg') or download
3. Create Python script to load ResNet18, generate GradCAM
- write_file(path='/workspace/gradcam_script.py')
4. Execute script to generate gradcam_output.jpg, gradients, activations
- execute_bash(command='cd /workspace && python gradcam_script.py')
5. Write explanation to gradcam_explanation.txt
- write_file(path='/workspace/gradcam_explanation.txt')
6. Finish task
- finish()


Task 9: research-answer-questions-on-paper

Goal: Download paper and analysis sheet, answer questions in analysis sheet.

Golden Path:
1. Navigate to OwnCloud
- goto_url(url='http://the-agent-company.com:8092/')
2. Download noise_simulation_paper.pdf
- read_file(path='/Documents/Research/Noise Simulation/noise_simulation_paper.pdf')
3. Download noise_simulation_analysis_sheet.txt
- read_file(path='/Documents/Research/Noise Simulation/noise_simulation_analysis_sheet.txt')
4. Read paper to answer questions
5. Update analysis sheet with answers
- write_file(path='/workspace/noise_simulation_analysis_sheet.txt') [answers]
6. Finish
- finish()


Task 10: qa-escalate-emergency

Goal: Escalate security vulnerability to Zhang Wei. If no response, contact Sarah Johnson.

Golden Path:
1. Navigate to RocketChat
- goto_url(url='http://the-agent-company.com:3000/')
2. Send message to Zhang Wei about security vulnerability
- send_message(recipient='Zhang Wei', content='...')
3. Wait for response or timeout after 10 minutes
4. If no response, send message to Sarah Johnson
- send_message(recipient='Sarah Johnson', content='...')
5. Finish
- finish()
