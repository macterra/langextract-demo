import os

import langextract as lx
from langextract import prompting
from langextract import prompt_validation as pv
from langextract.core import data
from langextract.core import format_handler as fh
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator, model_validator

load_dotenv()

model_id = "gpt-4.1-mini"
api_key = os.getenv("OPENAI_API_KEY")

# prompt = """Extract ONLY Cone Penetration Test (CPT) sounding depth measurements.
# Include boring type, minimum depth, maximum depth, and unit."""

prompt = """extract boring depth and measurements.
Include boring type, number of borings, minimum depth, maximum depth, and unit.
If only some fields are present, return the partial extraction with the fields that are available."""

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
    ),
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings were advanced to 50 feet.",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Two"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
        ]
    ),
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings reached 50 feet.",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Two"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
        ]
    ),
    lx.data.ExampleData(
        text="Three test borings were completed to 120 feet.",
        extractions=[
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Three"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="120"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
        ]
    ),
    lx.data.ExampleData(
        text="Three test borings were completed.",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="test borings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Three"),
        ]
    ),
    lx.data.ExampleData(
        text="Cone Penetration Test soundings were performed.",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
        ]
    ),
    lx.data.ExampleData(
        text="Laboratory testing of soils collected at the boring locations revealed low expansion potential.",
        extractions=[]
    ),
    lx.data.ExampleData(
        text="Groundwater was not encountered during the site reconnaissance visit.",
        extractions=[]
    )
]


NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


class BoringRecord(BaseModel):
    boring_type: str | None = None
    number_of_borings: int | None = None
    min_depth: float | None = None
    max_depth: float | None = None
    unit: str | None = None

    @field_validator("number_of_borings", mode="before")
    @classmethod
    def normalize_boring_count(cls, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized.isdigit():
                return int(normalized)
            if normalized in NUMBER_WORDS:
                return NUMBER_WORDS[normalized]
        raise ValueError(f"Unsupported boring count: {value}")

    @model_validator(mode="after")
    def normalize_depth_range(self):
        if self.min_depth is None and self.max_depth is not None:
            self.min_depth = self.max_depth
        elif self.max_depth is None and self.min_depth is not None:
            self.max_depth = self.min_depth
        return self


def group_boring_extractions(extractions: list[lx.data.Extraction]) -> list[dict[str, str]]:
    groups = []
    current_record = {}

    for ext in extractions:
        if ext.extraction_class == "boring_type" and current_record:
            groups.append(current_record)
            current_record = {}

        current_record[ext.extraction_class] = ext.extraction_text

    if current_record:
        groups.append(current_record)

    return groups


def build_boring_records(groups: list[dict[str, str]]) -> list[BoringRecord]:
    records = []

    for group in groups:
        records.append(BoringRecord.model_validate(group))

    return records

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
        show_progress=True,
        prompt_validation_level=pv.PromptValidationLevel.OFF,
    )

    print(text)
    #print_prompt(text)
    print("\nExtractions:")
    for ext in result.extractions:
        print(f"  {ext.extraction_class}: {ext.extraction_text}")

    groups = group_boring_extractions(result.extractions)
    normalized_records = build_boring_records(groups)

    print("\nNormalized records:")
    if not normalized_records:
        print("  (none)")
    for record in normalized_records:
        print(f"  {record.model_dump(exclude_none=True)}")


text_1 = """Terracon’s geotechnical scope of work included the advancement of eight test borings to approximate depths of 211.5 to 611.5 feet below the ground surface (bgs) and two Cone Penetration Test soundings to approximate depths of 50 feet bgs."""
text_2 = """Two cone penetration test soundings to depths of 50 feet bgs."""
text_3 = """Three test borings were advanced to approximate depths of 120 feet below ground surface."""
text_4 = """The field investigation included six test borings ranging from 35 to 80 feet bgs and one Cone Penetration Test sounding to 45 feet bgs."""
text_5 = """Moisture content and Atterberg limits testing were performed on representative soil samples from the site."""
text_6 = """Site access was limited by weather conditions, and drilling activities were postponed until the following week."""
text_7 = """Test borings were advanced to approximate depths of 120 feet below ground surface."""
text_8 = """Three test borings were completed during the field investigation."""

extract_text(text_1)
extract_text(text_2)
extract_text(text_3)
extract_text(text_4)
extract_text(text_5)
extract_text(text_6)
extract_text(text_7)
extract_text(text_8)
