import dspy
from src.modules.report_generation.schemas import Intent
# generate_expert_intent: Signature = topic, chat_history, role -> intent
# generate_expert_chat_response: Signature = topic, chat_history, role, intent -> response_with_citations
# polish_expert_response: Signature = chat_history, role, response -> refined_response
# search_queries: Signature = topic, chat_history, role, intent -> search_queries: list[str]

