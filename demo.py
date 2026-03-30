import langextract as lx

model_id = "phi3.5"  # or "gemma2:2b"
model_url = "http://localhost:11434"

# prompt = """Extract ONLY Cone Penetration Test (CPT) sounding depth measurements.
# Include boring type, minimum depth, maximum depth, and unit."""

prompt = """extract boring depth and  measurements.
Include boring type, number of borings, minimum depth, maximum depth, and unit."""

examples = [
    lx.data.ExampleData(
        text="Two Cone Penetration Test soundings to depths of 50 feet bgs",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test"),
            lx.data.Extraction(extraction_class="number_of_borings", extraction_text="2"),
            lx.data.Extraction(extraction_class="min_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="max_depth", extraction_text="50"),
            lx.data.Extraction(extraction_class="unit", extraction_text="feet")
        ]
    ),
    lx.data.ExampleData(
        text="8 test borings to depths ranging from 100 to 200 feet below ground surface",
        extractions=[
            lx.data.Extraction(extraction_class="boring_type", extraction_text="test boring"),
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
            lx.data.Extraction(extraction_class="boring_type", extraction_text="Cone Penetration Test"),
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

text = """Terracon’s geotechnical scope of work included the advancement of eight test borings to approximate depths of 211.5 to 611.5 feet below the ground surface (bgs) and two Cone Penetration Test soundings to approximate depths of 50 feet bgs."""

result = lx.extract(
    text_or_documents=text,
    prompt_description=prompt,
    examples=examples,
    model_id=model_id,
    model_url=model_url,
    show_progress=True
)

print("\nExtractions:")
for ext in result.extractions:
    print(f"  {ext.extraction_class}: {ext.extraction_text}")

# text = """Laboratory testing of soils collected at the boring locations revealed the near-surface soil possesses “low” expansion potential when testing in accordance with the ASTM International D4829 test method (Figures A1 and A2)."""

# result = lx.extract(
#     text_or_documents=text,
#     prompt_description=prompt,
#     examples=examples,
#     model_id=model_id,
#     model_url=model_url,
#     show_progress=True,
#     resolver_params={"suppress_parse_errors": True},
# )

# print("\nExtractions:")
# for ext in result.extractions:
#     print(f"  {ext.extraction_class}: {ext.extraction_text}")
