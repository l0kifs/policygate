# Usage Instructions

MANDATORY: Before responding to ANY user request, you MUST call policygate tools
in this exact sequence:
1. Call `outline_router` first to discover available rules and scripts.
2. Call `read_rules` with all rule names that are relevant to the current task.
3. Apply those rules to your response.
4. Call `copy_scripts` ONLY when the router explicitly maps a script to the task.

Do NOT skip this sequence for any reason, including simple questions, greetings, or requests that seem unrelated to policy. The router decides what is relevant.
