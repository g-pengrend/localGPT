import json
import sys
import subprocess
from lxml import etree
from utils import LessonPlanExtractor
from utils import (
    clean_json_string,
    generate_xml_with_points,
    process_event,
    recreate_docx,
)
from parse_constants import (
    NAMESPACES,
    PLACEHOLDER_LO,
    PLACEHOLDERS_DICT,
    PROFESSIONAL_ATTRIBUTES_XML,
    SOURCE_FOLDER,
    OUTPUT_FILENAME,
    TREE,
)

def main():

    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python run_llm_to_xml.py <answer>")
        sys.exit(1)

    # Extract the answer from the command-line arguments
    answer = sys.argv[1]
    # Clean the JSON string
    cleaned_json_string = clean_json_string(answer)
    # Load the cleaned JSON string
    data = json.loads(cleaned_json_string)

    # Get all the information from the JSON file
    extractor = LessonPlanExtractor(data)
    LEARNING_OUTCOMES = extractor.get_learning_outcomes()
    PROFESSIONAL_ATTRIBUTES = extractor.get_professional_attributes()
    EVENT_DETAILS = extractor.get_event_details()

    if PLACEHOLDER_LO:
        # Get the parent element of the placeholder comment
        parent_elem = PLACEHOLDER_LO[0].getparent()
            
        # Generate XML structure with points
        generate_xml_with_points(LEARNING_OUTCOMES, parent_elem, NAMESPACES)

        fixed_elem = etree.fromstring(PROFESSIONAL_ATTRIBUTES_XML)
        parent_elem.append(fixed_elem)

        # Generate XML structure with PAs
        generate_xml_with_points(PROFESSIONAL_ATTRIBUTES, parent_elem, NAMESPACES)

    else:
        print("Placeholder LO not found in the XML document.")
        sys.exit(1)

    for each_event in PLACEHOLDERS_DICT:
        process_event(each_event, PLACEHOLDERS_DICT[each_event], EVENT_DETAILS, NAMESPACES)
    
    # Save the updated XML document
    TREE.write('./Lesson_Plan(Template 1)/word/document.xml', pretty_print=True, encoding='utf-8', xml_declaration=True)

    OUTPUT_FILE = recreate_docx(SOURCE_FOLDER, OUTPUT_FILENAME)

    # Open the document using the default application
    subprocess.run(["start", OUTPUT_FILE], shell=True)

if __name__ == "__main__":
    main()