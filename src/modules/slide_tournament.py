import dspy
import math
from typing import Literal, List
from src.schemas.schemas import Slide

class PairwiseSlideJudge(dspy.Signature):
    """Compare two slides and provide preference with reasoning"""
    screenshot_A: dspy.Image = dspy.InputField()
    screenshot_B: dspy.Image = dspy.InputField()
    preference: Literal['A', 'B'] = dspy.OutputField()
    reasoning: str = dspy.OutputField()

class SlideTournament(dspy.Module):
    """Single elimination tournament for slides using pairwise judging"""
    
    def __init__(self):
        super().__init__()
        self.judge = dspy.ChainOfThought(PairwiseSlideJudge)
    
    def forward(self, slides: List[Slide]) -> Slide:
        """Run tournament and return winning slide"""
        if not slides:
            raise ValueError("Cannot run tournament with no slides")
        
        if len(slides) == 1:
            return slides[0]
        
        # Create bracket with byes for non-power-of-2 sizes
        bracket = self._create_bracket(slides)
        
        while len(bracket) > 1:
            next_round = []
            
            # Process pairs in current roun
            for i in range(0, len(bracket), 2):
                if i + 1 < len(bracket):
                    # Normal matchup
                    winner = self._judge_matchup(bracket[i], bracket[i + 1])
                    next_round.append(winner)
                else:
                    # Bye (odd number of contestants)
                    next_round.append(bracket[i])
            
            bracket = next_round
        
        return bracket[0]
    
    def _create_bracket(self, slides: List[Slide]) -> List[Slide]:
        """Create initial bracket, handling non-power-of-2 sizes"""
        n = len(slides)
        
        # If already power of 2, return as-is
        if n & (n - 1) == 0:
            return slides.copy()
        
        # Find next power of 2
        next_power = 2 ** math.ceil(math.log2(n))
        byes_needed = next_power - n
        
        # Higher seeded slides get byes (assume order matters)
        bracket = slides[:byes_needed].copy()  # These get byes
        bracket.extend(slides[byes_needed:])   # These play first round
        
        return bracket
    
    def _judge_matchup(self, slide_a: Slide, slide_b: Slide) -> Slide:
        """Judge a single matchup between two slide screenshots"""
        result = self.judge(
            screenshot_A=slide_a.dspy_image(),
            screenshot_B=slide_b.dspy_image()
        )
        
        return slide_a if result.preference == 'A' else slide_b