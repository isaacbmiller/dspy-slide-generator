from src.utils.utils import enable_mlflow
from src.modules.report_generation.report_utils import retrieve
from src.modules.report_generation.report_utils import similarity_score
from src.modules.report_generation.schemas import Intent
import dspy
import rich

class GenerateExpertIntent(dspy.Signature):
    role: str = dspy.InputField()
    history: dspy.History = dspy.InputField()
    intent: Intent = dspy.OutputField()

generate_expert_intent = dspy.ChainOfThought(GenerateExpertIntent)

class GenerateExpertChatResponse(dspy.Signature):
    """Generate the next reponse to the conversation as the expert in the role based on the given intent. Include citations if relevant."""
    
    role: str = dspy.InputField()
    intent: Intent = dspy.InputField()
    chat_history: dspy.History = dspy.InputField()
    response_with_citations: str = dspy.OutputField()

generate_expert_chat_response = dspy.ChainOfThought(GenerateExpertChatResponse)

class PolishExpertResponse(dspy.Signature):
    """Polish the expert response to make it more natural and coherent"""
    chat_history: dspy.History = dspy.InputField()
    role: str = dspy.InputField()
    response_draft: str = dspy.InputField()
    refined_response: str = dspy.OutputField()

polish_expert_response = dspy.ChainOfThought(PolishExpertResponse)

class GenerateSearchQueries(dspy.Signature):
    """Generate diverse search queries to use in search based retrieval related to the current question as the expert in the role."""
    role: str = dspy.InputField()
    intent: Intent = dspy.InputField()
    history: dspy.History = dspy.InputField()
    search_queries: list[str] = dspy.OutputField()

generate_search_queries = dspy.ChainOfThought(GenerateSearchQueries)

class GenerateExpertIntentAndResponse(dspy.Module):
    def forward(self, chat_history: dspy.History, role: str) -> tuple[Intent, str]:
        intent = generate_expert_intent(history=chat_history, role=role).intent
        rich.print(intent)
        # topic = ??
        if intent.is_question():
            # Need citations
            response = generate_expert_chat_response(history=chat_history, role=role, intent=intent)
            polished_response = polish_expert_response(history=chat_history, role=role, response=response)
            return intent, polished_response
        else: # answer
            # search_queries = generate_search_queries(chat_history, role, intent)
            relevant_documents = []
            # relevant_documents = retrieve(search_queries)

            response = generate_expert_chat_response(history=chat_history, role=role, intent=intent, relevant_documents=relevant_documents)
            polished_response = polish_expert_response(history=chat_history, role=role, response=response)
            return intent, polished_response
        
def main():
    user_question = "I want to learn more about the topic Alphafold 3 so I can report this technical breakthrough."
    chat_history = dspy.History(
        messages={
            "intent": Intent.ORIGINAL_QUESTION,
            "message": user_question,
            "role": "user"
        }
    )
    experts = ["AI Expert", "Geneticist", "Molecular biology expert"]
    intent_response_generator = GenerateExpertIntentAndResponse()

    intent, response = intent_response_generator(chat_history, experts[0])

    rich.print(intent)
    rich.print(response)

    

if __name__ == "__main__":
    enable_mlflow()

    main()