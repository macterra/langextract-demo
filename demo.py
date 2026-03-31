from boring_extraction import extract_boring_data
from boring_extraction import normalize_boring_records


def print_extraction_demo(text: str):
    result = extract_boring_data(text, show_progress=True)

    print(text)
    print("\nExtractions:")
    for ext in result.extractions:
        print(f"  {ext.extraction_class}: {ext.extraction_text}")

    normalized_records = normalize_boring_records(result.extractions)

    print("\nNormalized records:")
    if not normalized_records:
        print("  (none)")
    for record in normalized_records:
        print(f"  {record.model_dump(exclude_none=True)}")


TEXTS = [
    """Terracon’s geotechnical scope of work included the advancement of eight test borings to approximate depths of 211.5 to 611.5 feet below the ground surface (bgs) and two Cone Penetration Test soundings to approximate depths of 50 feet bgs.""",
    """Two cone penetration test soundings to depths of 50 feet bgs.""",
    """Three test borings were advanced to approximate depths of 120 feet below ground surface.""",
    """The field investigation included six test borings ranging from 35 to 80 feet bgs and one Cone Penetration Test sounding to 45 feet bgs.""",
    """Moisture content and Atterberg limits testing were performed on representative soil samples from the site.""",
    """Site access was limited by weather conditions, and drilling activities were postponed until the following week.""",
    """Test borings were advanced to approximate depths of 120 feet below ground surface.""",
    """Three test borings were completed during the field investigation.""",
]


def main():
    for text in TEXTS:
        print_extraction_demo(text)


if __name__ == "__main__":
    main()
