# DSPy Slide Generator Agent Guide

## Overview
This codebase implements a DSPy-based slide generation system that creates presentation slides from content using compound LLM pipelines. The system follows a 4-phase pipeline architecture with tournament-based selection and iterative refinement.

## Quick Commands

### Development
```bash
# Run the main slide generator
python src/core/main.py

# MLflow tracking (start in separate terminal)
mlflow ui --port 5000
```

## DSPy Pipeline Architecture

### 4-Phase Pipeline
1. **Content Input** (`PresentationInputs`) - User goals, intent, data, brand guidelines
2. **Narrative Generation** - Extract 3-5 key narrative points from content
3. **Slide Overview** - Generate 5-10 slide specifications from narrative
4. **Code Generation + Screenshot** - Create React components and capture images

### Core DSPy Patterns Used

#### 1. Signature-Based Design
- All LLM interactions defined as `dspy.Signature` classes
- Input/output fields clearly specified with type hints
- Signatures live in `src/schemas/signatures.py`

```python
class NarrativeGenerator(dspy.Signature):
    """Generate a list of 3-5 narrative points"""
    presentation_inputs: PresentationInputs = dspy.InputField()
    narrative_points: list[NarrativePoint] = dspy.OutputField()
```

#### 2. Module Composition
- Main logic implemented as `dspy.Module` subclasses
- Modules compose signatures with reasoning strategies (ChainOfThought)
- Modules handle state management and iteration logic

```python
class SlideGenerator(dspy.Module):
    def __init__(self):
        self.narrative_generator = dspy.ChainOfThought(NarrativeGenerator)
        self.slide_generator = dspy.ChainOfThought(SlideOverviewGenerator)
```

#### 3. Temperature-Based Variation
- Uses multiple temperature settings (0.0, 0.25, 0.5, 0.75) for variation
- Batch processing with `num_threads=10` for parallel generation
- Tournament selection to pick best variants

#### 4. Iterative Refinement Loop
- Judge-based feedback system with satisfaction checks
- Up to `max_iter` attempts to improve slide quality
- Feedback incorporated into next iteration attempt

#### 5. Tournament Selection
- Pairwise comparison using visual judgment
- Single elimination bracket for multiple slide variants
- Handles non-power-of-2 contestant counts with byes

### Data Schema Patterns

#### Core Entities
- `PresentationInputs` - Input specification with goals, intent, data
- `NarrativePoint` - Structured narrative with name and bullet points  
- `SlideOverview` - High-level slide specification
- `DetailedSlideInputs` - Detailed slide requirements (title, data, visual, layout, tone)
- `Slide` - Final slide with React code and screenshot

#### Custom DSPy Types
- `Slide` extends `dspy.BaseType` for multimodal handling
- Includes PIL Image integration for screenshot storage
- Custom formatting for LLM consumption

### MLflow Integration
- Automatic experiment tracking with `mlflow.dspy.autolog()`
- Experiment naming: "slide_generator"
- Tracks model calls, parameters, and artifacts

### File Organization Conventions

#### Imports
- Use absolute imports from `src.` root
- Separate schema imports from utility imports
- Keep external library imports at top

#### Module Structure
- One primary DSPy module per file
- Related signature classes co-located with modules
- Utility functions separated into `utils/`

#### Data Management
- Brand guidelines in JSON format under `data/brand/`
- Content sources under `docs/` (blogs, research)
- Generated outputs timestamped under `outputs/`

### Testing & Validation
- Visual validation through screenshot generation
- Judge-based quality assessment
- Tournament comparison for variant selection

### Brand & Styling
- Centralized brand guidelines in JSON format
- Consistent styling through `BrandGuidelines` schema
- React component generation follows brand specifications

## Development Patterns

### Adding New Signatures
1. Define in `src/schemas/signatures.py`
2. Include proper docstrings and type hints
3. Use semantic field names

### Creating New Modules  
1. Inherit from `dspy.Module`
2. Compose signatures in `__init__`
3. Implement `forward()` method
4. Handle iteration and state management

### Working with Images
- Use PIL Images for internal processing
- Convert to `dspy.Image` for LLM consumption
- Save screenshots with descriptive filenames

### Temperature Experimentation
- Use `lm_with_temp()` utility for consistent LM configuration
- Batch process multiple temperatures for diversity
- Select best results through tournament

This architecture enables systematic slide generation with quality control, variation, and iterative improvement using DSPy's structured approach to LLM pipeline development.
