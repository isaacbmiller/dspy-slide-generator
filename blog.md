## DSPy Dev Blog -- Recreating Ramp slide builder in DSPy

Its Friday July 11 at 8:05. I am going to give myself three hours to recreate the slide generator from Alex from Ramp's [tocite] recent talk about context engineering. I am going to hard time limit to 3 hours and see how far I can get.

Ive don'e some thinking on the treadmill but really thats about it.

Lets get started. [commit 1]

His talk is here: https://youtu.be/KRMkR1n2Kfw?si=2eCoyK_dVJww9miu

He breaks down the slide generator into 4 parts(quoted directly):

1. Parsing documents, data, and multimedia content - Processes diverse inputs including documents, data and multimedia content.
2. Narrative Synthesis and Outlining - AI agents analyze content and create coherent story structure
3. Parallelized slide generation & refinement - multiple agents work simultaneously to create and polish slides
4. Tournament based selection and finalization - best versions selected through competitive evaluation

Lets break his talk down further:

### Phase 1: Parsing documents, data, and multimedia content

Data files (csvs, excel) -- pattern recognition, statistical analysis

deep research for web analysis - query decomposition, knowledge synthesis

brand guidelines (pdf, powerpoint) -- colors, typography and layouts

### Phase 2: Narrative Synthesis and Outlining

Has as inputs:

1. User goal and intent

2. Core data insights

3. research findings

4. brand tone and voice

Comes up with a high level narrative arc

### Phase 3: Parallelized slide generation & refinement

story arc -> 5-10 slides -> structured outline with detailed specs per slide

detailed spec: Title, data, visual, layout, tone

### Phase 4: Agentic loop for generation and refinement

Generates react code from outline, renders in a headless browser, takes a screenshot, send to LLM to critique and refine code, repeat until satisfactory

Interesting: generates 10-20 variants per slide using different temperatures; Its unclear what else is varied.

"20 parallel variants generated concurrently"

50-100 slides for each

Does a tournament selection of the best slides -- 1v1 in order to saturate the token distribution on a per slide basis

shows temperature in range(0.1, 0.9, 0.2), but thats only 5 variants -- its unclear if there are other steps in between

I am just going to assume that the temperature is varied when generating the structured outline per slide, and then the implementation is back to temperature 0.1.

## Planning time!

That took me 20 minutes woof.

### Phase 1

What is the system that I want to design?

CSV understanding seems really hard to implement for v0. I think that using this doc will be my reference point for evaluation (i will also use my "Why I bet on DSPy blog"). Generating brand tone and voice would be important to make this generalize more, but this is a v0; Ill just ask claude to write some dspy brand guidelines from the website. This can be improved later.

Getting those into structured outputs is not that hard. The cool fun thing to do here is actually the content generation and code generation and rendering and iterative loop and the tournament selection as a funny inference strategy.

I guess lets do the structured outputs first. Wow I dont even know what my ideal set of structured outputs is for example: this literal blog. All 4 of the narrative synthesis inputs would come from different pipelines.

UGH okay I will just hard code a single example of the structured inputs because the deep research part is less interesting to me. I still have 2.5 hours tho so we will see how far I get.

Okay copied in my blog from before. Going to ask claude to write the brand guidelines now. JK i used o4-mini -- got a markdown file output -- now using AMP to convert it into json

Prompt:
> Look into dspy the framework (dspy.ai and on github) and generate brand, tone, and voice guidelines from that. Include image, color, font/typography references if helpful.

AMP prompt:
> Turn the dspy brand markdown into a structured json that has: brand, tone, and voice sections linking to the respective markdown sections

Okay dspy_brand_structure.json looks fine enough for now.

Ill also hard code the user intent and goal:

Intent: Persuade the audience in order to understand the value of DSPy as a forward thinking framework
Goal: Generate a slide deck that informs the audience of the core function of dspy as a way to solve problems with compound LLM systems.

Research findings I will hardcode to just include the "Why I bet on DSPy blog.md"

### Phase 2

Coming up with a high level narrative arc actually seems not that hard.

We want 3-5 bullets each with...

Went to chatgpt bc im lazy:
> If you were going to create a very simple schema for a slide show containing the story arc in 3-5 bullet points, what are 5 options for the schema

Gave me decent options but I would want something more general to encompass all of them

> Is there a generalized schema for this?

tldr:
list[dict[name: str, bullets: list[str]]]

### Phase 3

Title, data, visual, layout, tone

Title is string, everything else is list[str]

Lets have approximately the following structure:
Story arc -> list[name, description] per slide

[name, description] -> Slide[title, data, visual, layout, tone]

I worry that this will be slop on slop on slop but this is also just a recreation of the system that Alex wrote.

Maybe not because it will be grounded in the provided research.

I guess this is where I need to start generating variants per slide? Will need to verify that the variants look different when I get to that point.

### Phase 4

This phase makes more sense at temp 0 or 0.1, so I think it has to be the previous one by process of elimination.

Slide -> code

Take that code, render it somehow?

I don't know off the dome what framework to use for this -- will ask ChatGPT; Maybe playwright in an e2b instance?

get screenshot, iterate

Really this looks like a while loop or a ReAct loop, not clear which.

Maybe its a while loop first.

judge = ChainOfThought("slide outline: Slide, screenshot: DSPy.Image -> is_satisfactory: bool, critique: str")

One important note here is that generation order matters. I want the model to have room to reason before it commits to is_satisfactory or not. If I didnt give the chain of thought, then it would commit to is_satisfactory in a single token, or if I moved critique before is_satisfactory, it would be forced to give a criqique.

I can flesh out my judge by actually thinking through what the important features of a slide are, but for the sake of getting started, I will just use the single binary.

Tournament part is fairly straight forward. I can pass in the final screenshots for A and B. I would use a stronger reasoning model here as a judge if I have a choice.

Okay I feel good lets get actually coding.

## Wahoo Implementation time

First step is setting up my first example