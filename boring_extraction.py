import os
import re

import langextract as lx
from dotenv import load_dotenv
from langextract import prompt_validation as pv
from pydantic import BaseModel, field_validator, model_validator

load_dotenv()

MODEL_ID = "gpt-4.1-mini"
API_KEY = os.getenv("OPENAI_API_KEY")

PROMPT = """extract boring depth and measurements.
Include boring type, number of borings, minimum depth, maximum depth, and unit.
If only some fields are present, return the partial extraction with the fields that are available."""

BORING_TYPE_PATTERNS = (
    r"\btest borings?\b",
    r"\bsoil borings?\b",
    r"\brock borings?\b",
    r"\bmonitoring well borings?\b",
    r"\bcone penetration tests?\b",
    r"\bcone penetration test soundings?\b",
    r"\bcpt soundings?\b",
    r"\bcpts?\b",
    r"\bsoundings?\b",
    r"\bborings?\b",
)


def filter_context_keys() -> re.Pattern[str]:
    return re.compile("|".join(BORING_TYPE_PATTERNS), re.IGNORECASE)


EXAMPLES = [
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings to depths of 50 feet bgs",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Two"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
        ],
    ),
    lx.data.ExampleData(
        text="8 test borings to depths ranging from 100 to 200 feet below ground surface",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="test borings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="8"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="100"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="200"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
        ],
    ),
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings to depths of 50 feet bgs and three test borings to 100 feet",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Two"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
            lx.data.Extraction(extraction_class="boring_type", extraction_text="test borings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="three"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="100"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="100"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
        ],
    ),
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings were advanced to 50 feet.",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Two"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
        ],
    ),
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings reached 50 feet.",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Two"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
        ],
    ),
    lx.data.ExampleData(
        text="Three test borings were completed to 120 feet.",
        extractions=[
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Three"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="120"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet"),
        ],
    ),
    lx.data.ExampleData(
        text="Three test borings were completed.",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="test borings"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="Three"),
        ],
    ),
    lx.data.ExampleData(
        text="Cone Penetration Test soundings were performed.",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test soundings"),
        ],
    ),
    lx.data.ExampleData(
        text="Laboratory testing of soils collected at the boring locations revealed low expansion potential.",
        extractions=[],
    ),
    lx.data.ExampleData(
        text="Groundwater was not encountered during the site reconnaissance visit.",
        extractions=[],
    ),
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
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}

TENS_WORDS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}


def parse_number_word(value: str) -> int | None:
    normalized = value.strip().lower().replace("-", " ")
    normalized = re.sub(r"\(\s*(\d+)\s*\)", r"\1", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    digit_matches = re.findall(r"\d+", normalized)

    if len(digit_matches) == 1:
        return int(digit_matches[0])

    if normalized.isdigit():
        return int(normalized)
    if normalized in NUMBER_WORDS:
        return NUMBER_WORDS[normalized]
    if normalized in TENS_WORDS:
        return TENS_WORDS[normalized]

    parts = normalized.split()
    if len(parts) == 2 and parts[0] in TENS_WORDS and parts[1] in NUMBER_WORDS:
        return TENS_WORDS[parts[0]] + NUMBER_WORDS[parts[1]]

    if len(parts) == 2 and parts[1] == "hundred" and parts[0] in NUMBER_WORDS:
        return NUMBER_WORDS[parts[0]] * 100

    if (
        len(parts) == 4
        and parts[1] == "hundred"
        and parts[2] == "and"
        and parts[0] in NUMBER_WORDS
    ):
        remainder = parse_number_word(parts[3])
        if remainder is not None:
            return NUMBER_WORDS[parts[0]] * 100 + remainder

    if len(parts) == 3 and parts[1] == "hundred" and parts[0] in NUMBER_WORDS:
        remainder = parse_number_word(parts[2])
        if remainder is not None:
            return NUMBER_WORDS[parts[0]] * 100 + remainder

    return None


def parse_numeric_value(value: str) -> float | None:
    normalized = value.strip().lower().replace("-", " ")
    normalized = re.sub(r"\(\s*(\d+(?:\.\d+)?)\s*\)", r"\1", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    decimal_matches = re.findall(r"\d+(?:\.\d+)?", normalized)
    if len(decimal_matches) == 1:
        return float(decimal_matches[0])

    parsed_word_number = parse_number_word(normalized)
    if parsed_word_number is not None:
        return float(parsed_word_number)

    return None


class BoringRecord(BaseModel):
    boring_type: str | None = None
    number_of_borings: int | None = None
    min_depth: float | None = None
    max_depth: float | None = None
    unit: str | None = None

    @field_validator("number_of_borings", mode="before")
    @classmethod
    def normalize_boring_count(cls, value):
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            parsed_value = parse_number_word(value)
            if parsed_value is not None:
                return parsed_value
            return None
        return None

    @field_validator("min_depth", "max_depth", mode="before")
    @classmethod
    def normalize_depth_value(cls, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            parsed_value = parse_numeric_value(value)
            if parsed_value is not None:
                return parsed_value
            return None
        return None

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
            if "boring_type" not in current_record:
                current_record[ext.extraction_class] = ext.extraction_text
                continue
            groups.append(current_record)
            current_record = {}
        elif ext.extraction_class in current_record:
            previous_boring_type = current_record.get("boring_type")
            groups.append(current_record)
            current_record = {}

            # If the model starts a new group without repeating boring_type,
            # carry the prior type forward so we don't lose the earlier record.
            if previous_boring_type is not None:
                current_record["boring_type"] = previous_boring_type

        current_record[ext.extraction_class] = ext.extraction_text

    if current_record:
        groups.append(current_record)

    return groups


def build_boring_records(groups: list[dict[str, str]]) -> list[BoringRecord]:
    return [BoringRecord.model_validate(group) for group in groups]


def extract_boring_data(
    text: str,
    *,
    model_id: str = MODEL_ID,
    api_key: str | None = API_KEY,
    show_progress: bool = True,
):
    return lx.extract(
        text_or_documents=text,
        prompt_description=PROMPT,
        examples=EXAMPLES,
        model_id=model_id,
        api_key=api_key,
        show_progress=show_progress,
        prompt_validation_level=pv.PromptValidationLevel.OFF,
    )


def normalize_boring_records(extractions: list[lx.data.Extraction]) -> list[BoringRecord]:
    groups = group_boring_extractions(extractions)
    return build_boring_records(groups)


def extract_context_keys(
    text: str,
    *,
    model_id: str = MODEL_ID,
    api_key: str | None = API_KEY,
    show_progress: bool = False,
) -> list[BoringRecord]:
    result = extract_boring_data(
        text,
        model_id=model_id,
        api_key=api_key,
        show_progress=show_progress,
    )
    return normalize_boring_records(result.extractions)
