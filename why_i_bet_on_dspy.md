---
title: "Why I bet on DSPy"
excerpt: ""
coverImage: "/assets/blog/preview/cover.jpg"
date: "2024-08-10T09:35:07.322Z"
author:
  name: Isaac Miller
  picture: "/assets/blog/authors/joe.jpeg"
ogImage:
  url: "/assets/blog/preview/cover.jpg"
estimatedReadingTime: "11 minute read"
---

## Why I bet on DSPy

If you don't know what [DSPy](https://github.com/stanfordnlp/dspy) is, it is an open-source framework that helps you compose multiple LLM calls together in a principled manner to solve a problem.

### Traditional ML vs LLM Systems for problem solving

In traditional machine learning, you need a problem to solve or a reason to do it. You can't just “do machine learning.” You do it to decrease churn, predict sales, recommend products, etc.

You also need to collect data representing what you can observe about the problem, and then you can make predictions based off of it. If you are training an image classifier to discern "hot dog" or "not hot dog" you know what success looks like for your model. Given some labeled dataset, you know if your model is good or not along with other properties about where the model does well e.g. precision and recall.

You only know these things because you have a problem you are trying to solve. Without a problem you are training a model without a loss function or objective which doesn't make sense. Training it for what??

The same applies to LLMs, although people will tell you otherwise. Just because LLMs can generate unstructured data/text, that does not change the fact that to generate value, you need to use them to solve an actual problem, and the problem should **likely** be able to be quantified in a dataset or metric of some sort.

LLM calls chained together without evaluations are unsustainable for trying to solve real-world problems in the long term. How can you know if you are editing your prompts in the right direction? How do you know if you are actually solving the problem? What if your data distribution changes? What if you want to edit your pipeline slightly?

You can use LLMs to solve problems, and you can do so in creative manners that defy what would have seemed possible three years ago, but you cannot escape the fact that these problems need to be anchored to reality - to data.

> ***If problems are nails, and an LLM is your hammer, DSPy is like having an aimbot to hit the nails.***

Unfortunately, neither DSPy, OpenAI, nor YC S24 company “Lang + {any 4 letter word}” can create a nail where it never existed. You cannot shove LLMs into every situation or every problem and expect them to work.

So when should you use LLMs? This actually isn't really a question I can answer. There are traditional NLP tasks that they are good for, e.g. summarization, QA, sentiment analysis, and then you can be creative with the rest of the implementation. It could be code gen in a clever way, idea generation, filtering, rephrasing user queries. Let your imagination go wild. The class of problems where having an unlimited creative engine is massive. **However, you cannot forget that you need to solve a real problem that at least someone cares about.**

## So how exactly does DSPy force you to think about your problem?

DSPy forces you to use *verifiable* feedback to solve your problem. This could be a comparison to ground truth, e.g., multiple-choice questions, classification, or even using an LLM to judge how good an answer is. Regardless, you need to compare against something in order to make any actual progress on the thing that you care about!

At least from the Twitter circles I am in, people are starting to enter the "trough of disillusionment" part of the AI hype cycle. I think they are correct to do so, as they realize that AGI is not coming in the next 12 months, and this can be quite disappointing for them.

This is great for me because I now know the actual use cases of LLMs in pipelines. The real insight here is that despite LLMs not being AGI or able to do reasoning in a traditional sense, they are really, really good at pattern matching, matching a distribution, and being creative. DSPy uses this to create “Reasoning systems” that can actually perform what they are supposed to.

## What do most people not understand about LLMs?

“Reasoning systems” being in quotes is a core part of what people don't understand. LLMs can generate the correct text to solve many kinds of problems, especially when prompted correctly. They can sometimes do this in a zero-shot (no examples) manner. This is an incredibly impressive yet incredibly random process. DSPy just helps facilitate that randomness, hopefully being in the direction that you want it to ~likely~ help you solve your problem.

LLMs are, at heart, nothing more than really goddamn good next-token predictors. When you show them what the next token should be in the form of examples, they excel. With stochastic systems, there is no guarantee that anything is correct; it's all about probability. DSPy tries to maximize the conditional probability of achieving the highest possible score on your metric, given everything you know and can formulate about the problem.

## Why does automatic prompt optimization work?

When people talk about "automatic prompt optimization," they often think of systems where LLMs critique, improve, argue, and give feedback to improve the prompt. This is generally the wrong way to use LLMs.

LLMs are amazing creative idea generators. DSPy understands and harnesses that. When DSPy does prompt optimization, it gives an LLM the current prompt and says, "Hey, come up with creative variations of this that might solve the problem better." Then, it actually tries those variations on your evaluation set to see if they solve the problem better. If they don't numerically do better on whatever metric you care about, the ideas are thrown away. It almost looks like an evolutionary algorithm where the prompts are evaluated for their fitness.

There is no "deductive LLM reasoning" involved, no "textual gradients", just harnessing the strengths of LLMs as creative engines. Shocking again, DSPy tying back the optimization it does to the real world and seeing if it can help improve on your own problem.

Be skeptical when people tell you that LLMs are giving feedback and doing reasoning. I am not saying that textual feedback and these agentic loops will never work. They will! Not too far in the future! Do not, however, get fooled into thinking that just because a bunch of LLMs throw nonsense at each other for millions of tokens, anything valuable can be produced without verifying it in the real world.

Much like the idea of “Talk being cheap,” LLMs talking is only getting cheaper. It is time to take them and conquer amazingly hard problems that we never thought possible, or at least get started.

## What now?

I want you to leave this post with two main ideas:

1. Generally, you should define systems in terms of the inputs, the outputs, the steps it takes to get there, and how you know you have done a good job. DSPy forces you to do that, but oftentimes, it's just a good damn idea to think about what success actually means in any problem you are trying to solve.
2. LLMs are not good at reasoning and should not be used as such. If you need to do a reasoning step, try to verify and connect it to the real world as much as possible. Use LLMs as creative engines because they are really good at it. Generate ideas and cull them down using other methods; do anything but ask an LLM to do your multiplication for you.

To answer the question in the title succinctly, I personally think that DSPy is and will continue to be an amazing tool for solving real-world problems with compound LLM systems.

It is one of few frameworks that are committed to evolving with new research instead of being a one-and-done paper-based repo.

### (Aside) What's currently wrong with DSPy?

The framework **has its issues**! I am well aware of them, and I think and talk a lot about how to improve it.

The primary issue to me is that the framework as a whole isn't wholly reliable. Quirks, like the one of the newest pipeline Optimizers not working with the Assertions feature, can make it hard to trust new features. The older optimizers are consistent, but many of the newer features are less documented or have bugs.

Some of the optimizer ideas are powerful enough and good enough that people will write their own mini versions of the framework for their specific use cases. On the one hand, great! The idea is good enough that people will go out of their way to implement it. On the other hand, damn, the framework isn't stable enough right now to support these usecases we need to be innovating at the forefront of the framework. We need people pushing any new features beyond the edge of what's possible.

My perspective here is that the team knows where the good and bad developer experiences are, and we are shifting our focus to fixing this experience across the framework and making DSPy consistently reliable. I can't stop people from breaking off the main framework and building their own thing, but by doing so they are opting out of the incoming reliability and future optimizations that DSPy brings.

The second biggest problem with the framework is that it isn't approachable to beginners. This is such a fair criticism. DSPy has chosen to be opinionated about the way a few abstractions work and to use new terminology to describe things. These choices are always made as trade-offs, and we will probably never know if they are correct or not. I don't know if the answer is to change the terminology or just make better tutorials/lessons to help introduce you to the framework gently. I would lead towards the tutorial side, but that could be wrong! The terminology tends to be there for a reason, and whether or not that is justified is up to the user.

I see reliability and approachability as the framework's two biggest flaws. The good news is that both of these things can be improved. I am lucky to have found something that I believe in so much at a conceptual level that I will stick with and work through the big issues. If you have tried DSPy and gotten frustrated and quit, let me know. The only way we can help is either guess at the problem or hear from people who have experienced it, and if you take one thing from this article I would prefer to do things with data.

### Conclusion

Let's be realistic: the AI ecosystem and DSPy are both evolving. There will continue to be bugs, and we will continue to fix them. There will still continue to be things wrong with the framework. DSPy is lucky to have an amazing OSS community that tries to fix these bugs and improve the framework at what it does best. I speak for all of the DSPy contributors when I say that we care immensely about the framework and making it the best possible way to program with language models.

---

Notes:

* If you are reading this before August 25, 2024 and in SF, we are having a DSPy community picnic at Golden Gate Park! Lu.ma is [here](https://lu.ma/03f7pesv).
* This was heavily inspired by listening to [@rao2z](https://x.com/rao2z) on MLST and discussions with [Omar Khattab](https://x.com/lateinteraction).
* Opinions are my own :)
* Some language is imprecise here, and I am okay with that. This post is more about the general motivation behind DSPy.
* The DSPy discord is awesome! I am fairly active in the help channels, so feel free to tag me if something goes wrong.
* I love yapping about DSPy. DM me on Twitter [@Isaacbmiller1](https://x.com/isaacbmiller1) or email at <isaac@isaacmiller.dev>.