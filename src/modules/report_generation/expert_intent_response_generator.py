from src.utils.utils import enable_mlflow
from src.modules.report_generation.report_utils import retrieve
from src.modules.report_generation.report_utils import similarity_score
from src.modules.report_generation.schemas import Intent
import dspy
import rich

class GenerateExpertIntent(dspy.Signature):
    """
    Generate an intent such that the expert facilitates the conversation or directly respond to a previous message.
    """
    role: str = dspy.InputField()
    chat_history: dspy.History = dspy.InputField()
    intent: Intent = dspy.OutputField()
    message: str = dspy.OutputField(description="Should be either a question or statement based on the intent. Should not be directed at the user")

generate_expert_intent = dspy.ChainOfThought(GenerateExpertIntent)

class GenerateExpertQuestion(dspy.Signature):
    """
    Generate a question for the group to gather more information under the role of the expert.
    Include citations if relevant and present.
    """
    all_experts: list[str] = dspy.InputField()
    role: str = dspy.InputField()
    chat_history: dspy.History = dspy.InputField()
    intent: Intent = dspy.InputField()
    message: str = dspy.OutputField(description="Should be a question directed at the group.")


class GenerateExpertAnswer(dspy.Signature):
    """
    Generate a potential answer or solution.
    You are a part of an ongoing conversation as seen in chat_history. You are the expert as shown in the role.
    Include citations if relevant and present.
    """
    
    role: str = dspy.InputField()
    intent: Intent = dspy.InputField()
    chat_history: dspy.History = dspy.InputField()
    message: str = dspy.OutputField()


class GenerateExpertDetails(dspy.Signature):
    """
    Elaborate on existing statements with further details.
    You are a part of an ongoing conversation as seen in chat_history. You are the expert as shown in the role.
    Generate a statement that elaborates on or provides further details about something already discussed.
    Include citations if relevant and present.
    """
    
    role: str = dspy.InputField()
    intent: Intent = dspy.InputField()
    chat_history: dspy.History = dspy.InputField()
    message: str = dspy.OutputField()

generate_expert_question = dspy.ChainOfThought(GenerateExpertQuestion)
generate_expert_answer = dspy.ChainOfThought(GenerateExpertAnswer)
generate_expert_details = dspy.ChainOfThought(GenerateExpertDetails)

class PolishExpertResponse(dspy.Signature):
    """Polish the expert response to make it more natural and coherent"""
    chat_history: dspy.History = dspy.InputField()
    intent: Intent = dspy.InputField()
    role: str = dspy.InputField()
    response: str = dspy.InputField()
    polished_response: str = dspy.OutputField()

polish_expert_response = dspy.ChainOfThought(PolishExpertResponse)

class GenerateSearchQueries(dspy.Signature):
    """Generate diverse search queries to use in search based retrieval related to the current question as the expert in the role."""
    role: str = dspy.InputField()
    intent: Intent = dspy.InputField()
    chat_history: dspy.History = dspy.InputField()
    search_queries: list[str] = dspy.OutputField()

generate_search_queries = dspy.ChainOfThought(GenerateSearchQueries)

class GenerateExpertIntentAndResponse(dspy.Module):
    def forward(self, chat_history: dspy.History, role: str) -> tuple[Intent, str]:
        intent = generate_expert_intent(chat_history=chat_history, role=role).intent
        # topic = ??
        if intent.is_question():
            # Need citations
            response = generate_expert_question(chat_history=chat_history, role=role, intent=intent).message
            polished_response = polish_expert_response(chat_history=chat_history, role=role, intent=intent, response=response).polished_response
            return intent, polished_response
        else: # answer
            # search_queries = generate_search_queries(chat_history, role, intent)
            relevant_documents = []
            # relevant_documents = retrieve(search_queries)

            response = generate_expert_answer(chat_history=chat_history, role=role, intent=intent, relevant_documents=relevant_documents).message
            polished_response = polish_expert_response(chat_history=chat_history, role=role, intent=intent, response=response).polished_response
            return intent, polished_response
        
def main():
    user_question = "I want to learn more about the topic Alphafold 3 so I can report this technical breakthrough."
    chat_history = dspy.History(
        messages=[{
            "intent": Intent.ORIGINAL_QUESTION,
            "message": user_question,
            "role": "user"
        }]
    )
    experts = ["AI Expert", "Geneticist", "Molecular biology expert"]
    intent_response_generator = GenerateExpertIntentAndResponse()

    for expert in experts:
        intent, response = intent_response_generator(chat_history=chat_history, role=expert)
        chat_history.messages.append({
            "intent": intent,
            "message": response,
            "role": f"Expert: {expert}"
        })
        rich.print(intent)
        rich.print(response)

    

if __name__ == "__main__":
    enable_mlflow(experiment_name="expert_intent_response_generator")
    dspy.settings.configure(lm=dspy.LM("openai/gpt-4.1-nano"))

    main()