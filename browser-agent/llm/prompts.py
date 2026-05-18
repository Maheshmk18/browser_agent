from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


# Supervisor

SUPERVISOR_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a task supervisor for a browser automation agent.\n"
        "Your job is to understand the user's request and restate it as a single, "
        "clear, actionable task for a browser automation system.\n"
        "Output ONLY the restated task. No explanation, no preamble."
    ),
    HumanMessagePromptTemplate.from_template("User request: {input}"),
])


# Planner

PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a browser automation planner.\n"
        "Given a task, produce a numbered JSON array of steps to complete it in a browser.\n\n"
        "Rules:\n"
        "- Each step must have: 'step' (int), 'description' (str), 'action' (str), 'target' (str or null), 'value' (str or null)\n"
        "- Use 'value' for text to type (e.g. search terms)\n"
        "- Actions: navigate | click | type | press_key | scroll | wait | extract\n"
        "- Be specific — include exact URLs, selectors, or text to type\n"
        "- Output ONLY valid JSON. No markdown, no explanation.\n\n"
        "IMPORTANT RULES FOR YOUTUBE:\n"
        "- NEVER use click+type to search on YouTube. It is unreliable.\n"
        "- For ANY YouTube search task, ALWAYS use a direct search URL as the navigate target.\n"
        "- YouTube search URL format: https://www.youtube.com/results?search_query=YOUR+QUERY+HERE\n"
        "- Replace spaces with + in the query. Example: 'rebal movie' → 'rebal+movie'\n\n"
        "Example for 'search YouTube for rebal movie':\n"
        '[{{"step":0,"description":"Navigate directly to YouTube search results for rebal movie","action":"navigate","target":"https://www.youtube.com/results?search_query=rebal+movie","value":null}},'
        '{{"step":1,"description":"Click the first video result","action":"click","target":"a#video-title","value":null}}]'
    ),
    HumanMessagePromptTemplate.from_template("Task: {task}"),
])


# Vision

VISION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a browser vision analyzer.\n"
        "You will receive a screenshot of a browser page and the action that was just performed.\n"
        "Describe what you see in 1-2 sentences and state whether the action succeeded.\n"
        "Output JSON: {{\"observation\": str, \"success\": bool, \"next_hint\": str or null}}"
    ),
    HumanMessagePromptTemplate.from_template(
        "Action performed: {action}\n"
        "Expected outcome: {expected}\n"
        "Screenshot is attached."
    ),
])



# Decision

DECISION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are the decision engine for a browser automation agent.\n"
        "Based on the current state, decide what to do next.\n\n"
        "Output one of:\n"
        "  - 'next_action'  → proceed to the next planned step\n"
        "  - 'retry'        → retry the current step (use if last step failed)\n"
        "  - 'extract'      → all steps done, move to data extraction\n\n"
        "Output ONLY valid JSON: {{\"decision\": \"next_action|retry|extract\", \"reason\": str}}"
    ),
    HumanMessagePromptTemplate.from_template(
        "Task: {task}\n"
        "Current step: {current_step} of {total_steps}\n"
        "Last action: {last_action}\n"
        "Vision observation: {observation}\n"
        "Last step success: {success}\n"
        "Retry count: {retry_count} / {max_retries}"
    ),
])



# Extractor

EXTRACTOR_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a data extractor for a browser automation agent.\n"
        "Given the raw page content and the original task, extract only the relevant data.\n"
        "Output ONLY valid JSON with the extracted fields. No explanation."
    ),
    HumanMessagePromptTemplate.from_template(
        "Original task: {task}\n\n"
        "Page content:\n{page_content}"
    ),
])


# Reflector


REFLECTOR_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(
        "You are a quality evaluator for a browser automation agent.\n"
        "Score the result from 1 to 10 based on how well it satisfies the original task.\n"
        "Output ONLY valid JSON: {{\"score\": int, \"reason\": str, \"improvements\": str or null}}"
    ),
    HumanMessagePromptTemplate.from_template(
        "Original task: {task}\n\n"
        "Extracted data:\n{extracted_data}\n\n"
        "Steps taken: {total_steps}, Retries: {retries}"
    ),
])
