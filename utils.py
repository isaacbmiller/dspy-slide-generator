import dspy

def lm_with_temp(temperature: float = 0.0, model: str = "gpt-4.1"):
    return dspy.LM(model=model, temperature=temperature)
