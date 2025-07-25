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

Seems like they kinda just go traverse the entire mind map and generate an item per section