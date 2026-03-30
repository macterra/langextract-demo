import os

import langextract as lx
from langextract import prompting
from langextract.core import data
from langextract.core import format_handler as fh
from dotenv import load_dotenv

load_dotenv()

model_id = "gpt-4.1-mini"
api_key = os.getenv("OPENAI_API_KEY")

# prompt = """Extract ONLY Cone Penetration Test (CPT) sounding depth measurements.
# Include boring type, minimum depth, maximum depth, and unit."""

prompt = """extract boring depth and  measurements.
Include boring type, number of borings, minimum depth, maximum depth, and unit."""

examples = [
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings to depths of 50 feet bgs",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Two"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet")
        ]
    ),
    lx.data.ExampleData(
        text="8 test borings to depths ranging from 100 to 200 feet below ground surface",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="test borings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="8"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="100"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="200"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet")
        ]
    ),
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings to depths of 50 feet bgs and three test borings to 100 feet",
        extractions=[
            # CPT group
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Two"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
            # Test boring group
            lx.data.Extraction(extraction_class="boring_type", extraction_text="test borings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="three"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="100"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="100"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
        ]
    )
]

def print_prompt(text: str):
    prompt_template = prompting.PromptTemplateStructured(description=prompt)
    prompt_template.examples.extend(examples)

    format_handler = fh.FormatHandler(
        format_type=data.FormatType.JSON,
        use_wrapper=True,
        wrapper_key=data.EXTRACTIONS_KEY,
        use_fences=False,
        attribute_suffix=data.ATTRIBUTE_SUFFIX,
    )

    generator = prompting.QAPromptGenerator(
        template=prompt_template,
        format_handler=format_handler,
    )

    print("\nPrompt:")
    print(generator.render(question=text))


def extract_text(text: str):
    result = lx.extract(
        text_or_documents=text,
        prompt_description=prompt,
        examples=examples,
        model_id=model_id,
        api_key=api_key,
        show_progress=True
    )

    #print_prompt(text)
    print("\nExtractions:")
    for ext in result.extractions:
        print(f"  {ext.extraction_class}: {ext.extraction_text}")


text = """Terracon’s geotechnical scope of work included the advancement of eight test borings to approximate depths of 211.5 to 611.5 feet below the ground surface (bgs) and two Cone Penetration Test soundings to approximate depths of 50 feet bgs."""
text_2 = """Two Cone Penetration Test soundings to depths of 50 feet bgs."""
text_3 = """Three test borings were advanced to approximate depths of 120 feet below ground surface."""
text_4 = """The field investigation included six test borings ranging from 35 to 80 feet bgs and one Cone Penetration Test sounding to 45 feet bgs."""

extract_text(text)
extract_text(text_2)
extract_text(text_3)
extract_text(text_4)
