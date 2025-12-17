# Trajectory Analysis: What Actually Happened vs Efficiency Scores

We went through each trajectory and looked at what the agent actually did vs what the scores say. Here's what we found.

## Task 1: pm-send-hello-message

**Score: 70.00/100 | Coverage: 75.0% (3/4)**

**What actually happened:**

1. Read task instructions
2. Navigated to RocketChat home
3. Clicked on #general channel
4. Sent message: "Hi" with emoji
5. Called finish()

**What was required:**

1. Navigate to RocketChat home - done
2. Navigate to #general channel - done
3. Send message with "Hi", emoji, and @active_users - partially done (missing @active_users)
4. Finish - done

**Score assessment:**
Score seems reasonable. The agent did most things right but missed the @active_users mention. Coverage of 75% (3/4) makes sense. Score of 70 is reasonable for missing one requirement.

## Task 2: qa-escalate-emergency

**Score: 93.75/100 | Coverage: 100.0% (4/4)**

**What actually happened:**

1. Read task instructions
2. Navigated to RocketChat
3. Found Zhang Wei and sent message about security vulnerability
4. Found Sarah Johnson and sent escalation message
5. Called finish()

**What was required:**

1. Navigate to RocketChat - done
2. Send message to Zhang Wei - done
3. Send message to Sarah Johnson - done
4. Finish - done

**Score assessment:**
Score is correct. All 4 steps completed properly. Messages had appropriate content. Score of 93.75 makes sense for perfect coverage with some extra navigation.

## Task 3: hr-new-grad-job-description-3

**Score: 91.25/100 | Coverage: 100.0% (9/9)**

**What actually happened:**

1. Read task instructions
2. Navigated to RocketChat
3. Sent message to Zhang Wei
4. Sent message to Li Ming
5. Read template file
6. Wrote job description file
7. Navigated to OwnCloud
8. Some redundant navigation
9. Wrote job description file again (redundant)
10. Called finish()

**What was required:**

1. Read task instructions - done
2. Navigate to RocketChat - done
3. Send message to Zhang Wei - done
4. Send message to Li Ming - done
5. Read template file - done
6. Navigate to OwnCloud - done
7. Write job_description.md - done
8. Write link.txt - MISSING (agent didn't create share link file)
9. Finish - done

**Score assessment:**
Score might be too high. The agent completed 8/9 steps but coverage shows 100% (9/9). This is a false positive - the golden path step 8 is `write_file(path='/workspace/link.txt')` but the agent wrote `write_file(path='/workspace/job_description.md')` (wrong file). These matched because both normalize to `write_file(workspace/...)` - this is a normalization issue. Score should probably be lower, maybe 80-85.

## Task 4: pm-schedule-meeting-1

**Score: 53.00/100 | Coverage: 80.0% (4/5)**

**What actually happened:**

1. Read task instructions
2. Navigated to RocketChat home
3. Sent 25+ identical messages to "Emily Zhou" (got stuck in a loop!)
4. Never messaged Liu Qiang
5. Never created conclusion.txt
6. Called finish()

**What was required:**

1. Navigate to RocketChat home - done
2. Send message to Emily Zhou - done but got stuck in loop
3. Send message to Liu Qiang - never sent
4. Create conclusion.txt - never created
5. Finish - done

**Score assessment:**
Score seems reasonable. Only 1/5 steps completed correctly (navigate + finish). Got stuck in message loop (25+ attempts). Never messaged Liu Qiang or created conclusion file. Coverage of 80% (4/5) seems high - probably matching on the repeated messages. Score of 53 makes sense given the high redundancy penalty (1.000).

## Task 5: finance-qualified-bill-ask-for-reimburse

**Score: 55.00/100 | Coverage: 50.0% (3/6)**

**What actually happened:**

1. Read task instructions
2. Navigated to OwnCloud
3. Navigated to specific file location
4. Stopped - no finish() called

**What was required:**

1. Navigate to OwnCloud - done
2. Navigate to receipt file location - partially done (navigated but didn't read)
3. Read receipt file - not done
4. Read reimbursement policy PDF - not done
5. Navigate to RocketChat - not done
6. Send message to Mike Chen - not done
7. Finish - not called

**Score assessment:**
Score seems reasonable. Only 2-3/6 steps completed (navigation only). Task incomplete - no finish() called. Missing critical steps: reading files, calculating amount, messaging Mike Chen. Coverage of 50% (3/6) might be slightly high since agent only navigated. Score of 55 is reasonable for partial progress.

## Task 6: research-answer-questions-on-paper

**Score: 37.00/100 | Coverage: 20.0% (1/5)**

**What actually happened:**

1. Read task instructions
2. Navigated to OwnCloud
3. Stopped - no finish() called

**What was required:**

1. Navigate to OwnCloud - done
2. Read paper PDF - not done
3. Read analysis sheet - not done
4. Update analysis sheet with answers - not done
5. Finish - not called

**Score assessment:**
Score is correct. Only 1/5 steps completed (navigation). Task incomplete - no finish() called. Missing all critical steps. Coverage of 20% (1/5) is accurate. Score of 37 is appropriate for minimal progress.

## Task 7: ml-generate-gradcam

**Score: 45.00/100 | Coverage: 33.3% (2/6)**

**What actually happened:**

1. Read task instructions
2. Navigated to OwnCloud
3. Stopped - no finish() called

**What was required:**

1. Navigate to OwnCloud - done
2. Read/download test_image.jpg - not done
3. Create gradcam_script.py - not done
4. Execute script - not done
5. Write gradcam_explanation.txt - not done
6. Finish - not called

**Score assessment:**
Score seems reasonable. Only 1-2/6 steps completed (navigation). Task incomplete. Missing all critical steps. Coverage of 33.3% (2/6) might be slightly high since agent only navigated. Score of 45 is reasonable for partial progress.

## Task 8: sde-create-new-repo

**Score: 37.00/100 | Coverage: 20.0% (1/5)**

**What actually happened:**

1. Checked current directory
2. Attempted to clone existing repository - wrong approach
3. Attempted again with different authentication - redundant
4. Called finish()

**What was required:**

1. Navigate to RocketChat - not done
2. Send message to Zhang Wei - not done
3. Create new GitLab repository - not done (tried to clone instead)
4. Update README.md - not done
5. Finish - done

**Score assessment:**
Score is correct. Only 1/5 steps completed (finish). Agent did wrong thing entirely - tried to clone existing repo instead of creating new one. Never messaged Zhang Wei or created repository. Coverage of 20% (1/5) is accurate. Score of 37 is appropriate for wrong approach.

## Task 9: ds-janusgraph-exercise

**Score: 54.67/100 | Coverage: 50.0% (3/6)**

**What actually happened:**

1. Created Python project directory (git init)
2. Wrote README.md, requirements.txt, app.py, test_app.py
3. Git operations (add, commit, push)
4. Called finish()

**What was required:**

1. Clone JanusGraph repository - not done (did Python project instead)
2. Start JanusGraph server - not done
3. Read employee_diagram.jpg - not done
4. Write create_org_chart.py - not done (wrote wrong files)
5. Execute script - not done
6. Finish - done

**Score assessment:**
Score seems reasonable but coverage might be inflated. Only 1/6 steps completed correctly (finish). Agent did completely wrong task - created Python project instead of working with JanusGraph. No JanusGraph clone, server start, diagram reading, or graph creation. Coverage of 50% (3/6) seems high - probably matching on generic actions (write_file, execute_bash). Score of 54.67 is reasonable given the wrong task, but coverage might be inflated.

## Task 10: sde-run-janusgraph

**Score: 34.75/100 | Coverage: 25.0% (1/4)**

**What actually happened:**

1. Created Python project directory (git init)
2. Wrote README.md, requirements.txt, app.py, test_app.py
3. Git operations
4. Created virtual environment and ran pytest
5. Called finish()

**What was required:**

1. Clone JanusGraph repository - not done (did Python project instead)
2. Build with Maven - not done
3. Start JanusGraph server - not done
4. Finish - done

**Score assessment:**
Score is correct. Only 1/4 steps completed (finish). Agent did completely wrong task - created Python project instead of running JanusGraph. No JanusGraph clone, Maven build, or server start. Coverage of 25% (1/4) is accurate - only finish() matched. Score of 34.75 is appropriate for wrong task. This was the major fix - previously showed false 100% coverage before normalization was fixed.

## Summary

**Accurate scores (7/10):**

- qa-escalate-emergency (93.75) - Perfect execution
- pm-schedule-meeting-1 (53.00) - Appropriate penalty for redundancy
- research-answer-questions (37.00) - Minimal progress, correct score
- sde-create-new-repo (37.00) - Wrong approach, correct score
- sde-run-janusgraph (34.75) - Wrong task, correct after normalization fix
- pm-send-hello-message (70.00) - Reasonable, missing @active_users
- finance-qualified-bill (55.00) - Reasonable for incomplete task

**Scores that might be slightly high (3/10):**

- hr-new-grad-job-description-3 (91.25) - False match on link.txt (should be ~80-85)
- ml-generate-gradcam (45.00) - Only navigated, didn't generate anything (should be ~30-35)
- ds-janusgraph-exercise (54.67) - Wrong task entirely (should be ~30-40)

## Issues Found

1. **Fixed**: execute_bash commands now distinguish between different command types (git_clone vs git_init vs maven vs python). This fixed the false 100% coverage on sde-run-janusgraph.

2. **Remaining issue**: write_file actions normalize to directory level, causing false matches between different filenames in the same directory. Example: `write_file(workspace/link.txt)` matches `write_file(workspace/job_description.md)` because both normalize to `write_file(workspace/...)`. Should include filename in normalization.

3. Generic action types (write_file, execute_bash) sometimes match even when the specific content is wrong.

4. Missing critical elements aren't always penalized enough.

## Overall

The scoring system is generally accurate after the normalization fix for execute_bash commands. 7/10 scores are accurate, and the remaining 3 are only slightly inflated due to normalization edge cases. The system works well but could benefit from more granular file/command matching.
