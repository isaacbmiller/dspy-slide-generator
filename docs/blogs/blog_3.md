# DSPy Dev Blog 2 -- Continuing to create Ramp slide builder in DSPy

Okay so the state of the project is initially complete when we freeze the first components.

1. ✅ Break down the Ramp slide generator architecture
2. ✅ Design schemas for the 4-phase pipeline  
3. ✅ Implement narrative synthesis (Phase 2)
4. ✅ Build slide spec generation (Phase 3)
5. ✅ Create React code generation + screenshot pipeline (Phase 4)
6. ✅ Generate 8 working slides from the DSPy content
7. ✅ Tournament selection
8. ✅ Iterative refinement loop

Now we need a Deep research/storm clone.

Link to Co-Storm is [here](https://github.com/stanford-oval/storm)

Im attaching a screenshot from their paper here.

Theres 3 "roles" that are used:
1. User
2. Expert
3. Moderator

I won't implement user support yet.

Each agent response gets a label of:
1. Original Question
2. Information Request
3. Potential Answer
4. Further Details

The rough flows are:

History goes in

Expert
1. Choose between Ask or answer question
2. For ask question:
2a. Generate Question
2b. Polish utterance
3. Update mind map

2. For answer question:
3. Generate search queries
4. Retrieve information
5. Filter retrieved sources
6. Generate cited response
7. Polish utterance
8. Update mind map

Moderator:

1. rerank unused information
2. Generate new question with mind map
3. Polish utterance + Update participant list

At the end a cited report is generated

Stop condition is L consecutive turns of expert responses
with intents being either POTENTIAL ANSWER or FURTHER DETAILS

To update mind map:
Either insert or reorganize.
Insert uses semantic similarity between question and concept then prompts the LM to choose the final placement (appendix B)

When a concept c has more than K pieces of information:
M triggers the reorganize
1. LM generates a list of new subtopic names under c
1a. applies insert to place each piece of information associated with c in the subtree rooted at c. 
2. cleaning process to iteratively delete concepts with no supporting information and collapse concepts with only one subtopic. 

To get experts:
Co-Storm retrieves the background of topic t with a search
query and gives it to an LM to generate the expert
list P = {p1, ..., pN }.

To generate an utterance
1. choose the intent ai based on the discourse history {u1, ..., ui−1} 
2. If the intent is POTENTIAL ANSWER or FURTHER DETAILS:
2a. we prompt the LM to generate a search query q 
2b. retrieve information with a search engine
2c. generate a response with citations;

To generate the moderator’s utterance:
1. generate questions based on uncited sources
retrieved since the last moderator turn. 
2. reranks each piece of information i based on the
similarity to the topic t and the dissimilarity to
its associated question q.

I still dont know how they generate the report from the mind map...

Ohhh okay I had to go to the github and look in the actual runner class that they have, but they just pass in the knowledge base to an article generation module. About to look at what that generation module does.

Seems like they kinda just go traverse the entire mind map and generate an item per section. They also include sources

Okay lets write some pseudocode:

So theres like some big loop overall. Unclear how many iterations it works for to generate the mind map.

"""The discourse begins with N experts, P = {p1, ..., pN }, discussing the topic t for one turn per expert"""

N, K, L, α are set to 3, 10, 2, and 0.5

"""we terminate the informationseeking session once it reaches 30 search queries
for Co-STORM"""

Lowkey i dont like that design -- I want something that intelligently ends when it answers the user's question. I guess we will just use number of iterations for now and then evolve to either user guided when I make the web version or interactive.

```python
# HPARAMS:
N = 3 # number of experts
K = 10 # when to trigger concept reorganization
L = 2 # max number of non question turns in a row
alpha = 0.5 # weight of the similarity to the topic t in the reranking vs the dissimilarity to its associated question q


# When a concept c has more than K pieces of information:
# M triggers the reorganize
# 1. LM generates a list of new subtopic names under c
# 1a. applies insert to place each piece of information associated with c in the subtree rooted at c. 
# 2. cleaning process to iteratively delete concepts with no supporting information and collapse concepts with only one subtopic. 


class MindMap:
    def insert(current_node, new_node):
        # idk yet
        self.clean()
    
    def clean():
        for node in bfs(self.root):
            if node.num_children() > K:
                self.reorganize(node)
    
    def reorganize(self, node):
        new_subtopics = self.lm.generate_subtopics(node)
        old_children = node.childen
        node.children = []
        node.children = new_subtopics
        mapping = map_old_children_to_subtopics(old_children, new_subtopics)

        for old_child, subtopic in mapping:
            self.insert(subtopic, old_child)

        # TODO: delete concepts with no supporting information and collapse concepts with only one subtopic

def retrieve(search_queries: list[str]) -> list[str]: # I dont know what shape this data takes yet 
    ...
    documents = retrieval_api(search_queries)
    documents = rerank(documents)
    documents = filter(documents)
    return documents

def similarity_score(i:str, t:str, q:str):
    """Returns the similarity score between a piece of information i, a topic t, and a question q.
    i,t,q are compared as text embeddings
    """
    return cos(i,t)**alpha * (1-cos(i,q))**(1-alpha)

# I dont know if topic needs to be included at this point
generate_expert_intent: Signature = topic, chat_history, role -> intent
generate_expert_chat_response: Signature = topic, chat_history, role, intent -> response_with_citations
polish_expert_response: Signature = chat_history, role, response -> refined_response
search_queries: Signature = topic, chat_history, role, intent -> search_queries: list[str]

class Intent(Enum):
    ORIGINAL_QUESTION = "original_question"
    INFORMATION_REQUEST = "information_request"
    POTENTIAL_ANSWER = "potential_answer"
    FURTHER_DETAILS = "further_details"

    def is_question(self):
        return self == Intent.ORIGINAL_QUESTION or self == Intent.INFORMATION_REQUEST

class GenerateExpertIntentAndResponse(Module):
    def forward(self, topic, chat_history, role) -> intent, response:
        intent = generate_expert_intent(topic, chat_history, role)
        if intent.is_question():
            response = generate_expert_chat_response(topic, chat_history, role, intent)
            polished_response = polish_expert_response(chat_history, role, response)
            return intent, polished_response
        else: # answer
            search_queries = search_queries(topic, chat_history, role, intent)
            relevant_documents = retrieve(search_queries)

            response = generate_expert_chat_response(topic, chat_history, role, intent, relevant_documents)
            polished_response = polish_expert_response(chat_history, role, response)
            return intent, polished_response

generate_experts: Signature = context(?), topic: str -> role_list: List[str]

class ConversationLoop(Module):
    def __init__(self, max_consecutive_answers, initial_expert_roles):
        self.max_consecutive_answers = max_consecutive_answers
        self.expert_roles = initial_expert_roles

    def expert_loop(self, mind_map, topic, chat_history, expert_roles):
        consecutive_answers = 0
        for role in expert_roles:
            intent, response = expert_response_generator(topic, chat_history, role)
            if intent.is_question():
                consecutive_answers = 0
            else:
                consecutive_answers += 1
            chat_history.append(Message(role, intent, response))
            update_mind_map(mind_map, response)
            if consecutive_answers >= self.max_consecutive_answers:
                break
    
    def forward(self, mind_map, topic, chat_history):
        # rerank unused information

        # generate a question
        # polish utterance and add to chat
        self.expert_roles = self.generate_experts(topic)

        self.expert_loop(mind_map, topic, chat_history)



topic = input()
mind_map = MindMap()
expert_response_generator = GenerateExpertIntentAndResponse()
conversation_loop = ConversationLoop(max_consecutive_answers=L)

chat_history: List[Message] = []
expert_roles: List[str] = generate_experts(topic)
# start with one round of answers to the questions from each expert
# I notably am not tracking which documents have been used and cited yet
for role in expert_roles:
    intent, response = expert_response_generator(topic, chat_history, role)
    chat_history.append(Message(role, intent, response))
    update_mind_map(mind_map, response)

for iter in range(max_iter):
    conversation_loop.forward(mind_map, topic, chat_history)

generate_report(mind_map)
```
This module is kinda a monster.

Lets break it down into smaller testable parts to make it more manageable.

I kinda just hand waved over the details of the mind map and the chat history part of the loop.

I know that dspy.History will be useful here but I have actually never used it before.
