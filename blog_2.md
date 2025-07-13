# DSPy Dev Blog 2 -- Continuing to create Ramp slide builder in DSPy

Okay so the state of the project as of last night was:
1. ✅ Break down the Ramp slide generator architecture
2. ✅ Design schemas for the 4-phase pipeline  
3. ✅ Implement narrative synthesis (Phase 2)
4. ✅ Build slide spec generation (Phase 3)
5. ✅ Create React code generation + screenshot pipeline (Phase 4)
6. ✅ Generate 8 working slides from the DSPy content
7. ❌ Tournament selection (ran out of time)
8. ❌ Iterative refinement loop (ran out of time)

**Current Time: 7/12/2025 6:13 PM**

All of our slide outputs have weird spacing as you can see below. I would imagine that it has something to do with how we are exporting the react code. Or some CSS setting idk.

If the model is able to figure it out, ill look at the logs and just add that into the signature so it doesnt have to fix it every time.

Okay I have my outputs directory a little more sane now.

I need to implement both iteration and the tournament. Doesn't matter which one I do first.

Okay the judge didn't error, time to sanity check the outputs.

Yeah:
>  The slide effectively communicates the problem and uses both text and visuals to reinforce the message. However, the formatting issues—such as words running together and awkward line breaks—detract from readability and professionalism. Fix these text formatting problems to improve clarity. Otherwise, the slide is visually appealing and aligns well with the overview.

It missed the fact that the figure is wack but good start. Lets up the number of iterations and see what it does.

Yeah so it actually doesn't realize that this slide is bad

![Slide](/Users/isaac/projects/dspy-slide-generator/outputs/2025-07-12-18-28-56/0.0/0_0_the_problem__chaining_llms_without_direction.png)

Okay so I added some more specification to the signature:
> Judge if a slide is a high quality slide matching the overview based on outline and screenshot
> Slides should be visibly appealing, well formatted, and easy to understand.
> You should be a harsh judge with high quality standards, ensuring that no misaligned text or figures are present.

I wonder if seeing the code would be helpful for the judge.

It seems like in the generator, screenshot is not being passed back as a dspy.Image.

Yup confirmed

NOTE: This should throw: type checking on images is not strict enough. 

Yeah good enough -- lets move on to the tournament.

 We can get rid of the code and just operate in screenshot land for now. Maybe ill regret this later.

 Tournament should be a module that takes in a list of screenshots and returns the best one.

Moving generate and iterate slides into its own file. Also going to keep the signatures for it in that file.

Gonna see how AMP does on the tournament implementation.
> Implement a tournament dspy module that uses Pairwise slide judge to make a 1v1 single elimination tournament for an arbitrary number of slides passed in

It made up a slide class that has a screenshot and metadata -- lowkey a good idea to capture the code and screenshot together and I thing I could use DSPyType to make it friendly to adapters.

This looks close enough to what I would expect!

Lets try with 4 slides.

There are a few things to pay attention to here. I want to see how different the final slides are.

Right now actually slide_generator will throw if we reach max iterations, this is wrong. We will just return the last screenshot.

The slide names sometimes have weird characters -- quick fix for that.

I actually want a `to_PIL_image` to get the image back out of the screenshot object.

Cursor got me.

Okay first version with variants, lets see how it goes.

We are getting judge iterations on move of them which is lit.

Will put my own opinion down before I see the judge result.

Lowkey these are mid :cry:

Note for when I do prod deployments -- been hearing good things about cloudflare workers recently.

Okay yeah I actually should just make a slide object with a DSPy representation lmao

Gonna have a title, code, filename, screenshot.

This is crazy I cant find the dspy basetype or whatever its called.

RIP I had to go to the github and search for type -- turns out its called Type and you add a format method,

Okay so what do we want our slide type to do?

Kinda icky because I need to add in the image as a content field but alas.

A little tricky syntax here, its a good thing I literally wrote dspy.Image -- someone should fix this!

This code is weird:
```python
class Slide(dspy.BaseType, BaseModel):
    title: str
    code: Optional[str] = None
    filename: Optional[str] = None
    screenshot: Optional[Image.Image] = None

    def format(self):
        return_string = ""
        if self.title:
            return_string += f"Title: {self.title}\n"
        if self.code:
            return_string += f"Code: {self.code}\n"
        if self.screenshot:
            return_string += f"Screenshot:"
        return [{"type": "text", "text": return_string},
                {"type": "image", "image": dspy.Image.from_PIL(self.screenshot).format()}]
```

Hmmm got an error that I need to implement:
`__get_pydantic_core_schema__`; lets see what amp can do here

Actually ill just arbitrary types allowed=true

Im out of my depth on the core_schema understanding -- its been a minute

Okay now I actually want to update my generator signatures and judges to use Slide instead of Screenshot.

Im anticipating some debugging here.

```
Unsupported image type: <class 'NoneType'>
2025/07/12 19:49:19 WARNING mlflow.tracing.fluent: Failed to start span Predict.forward: Error calling function `serialize_model`: ValueError: Unsupported image type: <class 'NoneType'>. For full traceback, set logging level to debug.
```

wow this was kinda hard
Went all the way into Predict

NOTE: forward doesnt automatically pick up the type hint of the `__call__` return type in a module

Okay everything is working again! that took like 2 hours but I stopped and got dinner.