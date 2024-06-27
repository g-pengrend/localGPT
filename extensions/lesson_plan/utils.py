import re
from lxml import etree
import uuid
import os
import zipfile
import os

class LessonPlanExtractor:
    def __init__(self, data):
        """
        Initializes the LessonPlanExtractor with the provided data. (json.loads format)

        Parameters:
        data (dict): A dictionary containing the lesson plan data with the following structure:
            {
                "lessonPlan": {
                    "learningOutcomes": [...],
                    "professionalAttributes": [...],
                    "events": [
                        {
                            "event1": "Event Name",
                            "content": [
                                {"activity": "Activity Name", "duration": "Duration", "method": "Method"}
                            ]
                        },
                        ...
                    ]
                }
            }
        """
        self.data = data

    def get_learning_outcomes(self):
        """
        Extracts learning outcomes from the lesson plan data.

        Returns:
        list: A list of learning outcomes.
        """
        return self.data['lessonPlan']['learningOutcomes']

    def get_professional_attributes(self):
        """
        Extracts professional attributes from the lesson plan data.

        Returns:
        list: A list of professional attributes.
        """
        return self.data['lessonPlan']['professionalAttributes']

    def get_event_details(self):
        """
        Extracts event details from the lesson plan data and structures them by event keys.

        Returns:
        dict: A dictionary where each key is an event key (e.g., "event1") and each value is a dictionary
              containing the event name and its contents. The contents are a list of dictionaries with
              details about each activity within the event.
              
              Example:
              {
                  "event1": {
                      "event_name": "Introduction",
                      "contents": [
                          {"activity": "Lecture", "duration": "30 minutes", "method": "Presentation"},
                          {"activity": "Discussion", "duration": "15 minutes", "method": "Interactive"}
                      ]
                  },
                  ...
              }
        """
        event_details = {}
        events = self.data['lessonPlan']['events']

        for event in events:
            for key in event:
                if key.startswith("event"):
                    event_name = event[key]
                    event_contents = []
                    for item in event['content']:
                        activity = item['activity']
                        duration = item['duration']
                        method = item['method']
                        event_contents.append({
                            "activity": activity,
                            "duration": duration,
                            "method": method
                        })
                    event_details[key] = {
                        "event_name": event_name,
                        "contents": event_contents
                    }

        return event_details

def clean_json_string(llm_output):
    """
    Extract and clean a JSON string from a given input string.

    Parameters:
    llm_output (str): The input string containing JSON content.

    Returns:
    str: The cleaned and corrected JSON string.
    """
    # Extract JSON content from the input string
    json_start = llm_output.find('{')
    json_end = llm_output.rfind('}')
    if json_start == -1 or json_end == -1:
        raise ValueError("No valid JSON object found in the input string.")
    
    json_string = llm_output[json_start:json_end + 1]

    # Replace problematic characters or sequences
    json_string = re.sub(r'\n|\s+', ' ', json_string)  # Replace newlines and multiple spaces with a single space
    json_string = re.sub(r',\s*([}\]])', r'\1', json_string)  # Remove trailing commas before closing braces/brackets
    json_string = re.sub(r'\\', r'\\\\', json_string)  # Escape backslashes
    json_string = re.sub(r'(?<!\\)"', r'\\"', json_string)  # Escape unescaped double quotes
    json_string = re.sub(r'\\"(.*?)\\"', r'"\1"', json_string)  # Unescape double quotes within strings

    # Fix missing commas between key-value pairs
    json_string = re.sub(r'(?<=\})(\s*)(?=\{)', r'\1, ', json_string)  # Add comma between objects in an array
    json_string = re.sub(r'(?<=\])(\s*)(?=\[)', r'\1, ', json_string)  # Add comma between arrays in an array
    json_string = re.sub(r'(?<=\d)(\s*)(?=\{)', r'\1, ', json_string)  # Add comma between numbers and objects
    json_string = re.sub(r'(?<=\])(\s*)(?=\{)', r'\1, ', json_string)  # Add comma between closing bracket and opening brace

    # Correct the JSON formatting
    json_string = json_string.replace('\\"', '"')  # Revert escaped quotes to normal quotes

    return json_string

# Function to generate XML structure for points or attributes
def generate_xml_with_points(items, parent, namespaces):
    for item in items:
        p_elem = etree.SubElement(parent, '{' + namespaces['w'] + '}p', attrib={
            '{' + namespaces['w14'] + '}paraId': str(uuid.uuid4()),
            '{' + namespaces['w14'] + '}textId': str(uuid.uuid4()),
            '{' + namespaces['w'] + '}rsidR': '00292B85',
            '{' + namespaces['w'] + '}rsidRPr': '00292B85',
            '{' + namespaces['w'] + '}rsidRDefault': '00292B85',
            '{' + namespaces['w'] + '}rsidP': '00292B85'
        })
        p_pr = etree.SubElement(p_elem, '{' + namespaces['w'] + '}pPr')
        p_style = etree.SubElement(p_pr, '{' + namespaces['w'] + '}pStyle', attrib={'{' + namespaces['w'] + '}val': 'ListParagraph'})
        num_pr = etree.SubElement(p_pr, '{' + namespaces['w'] + '}numPr')
        ilvl = etree.SubElement(num_pr, '{' + namespaces['w'] + '}ilvl', attrib={'{' + namespaces['w'] + '}val': '0'})
        num_id = etree.SubElement(num_pr, '{' + namespaces['w'] + '}numId', attrib={'{' + namespaces['w'] + '}val': '5'})
        r_pr = etree.SubElement(p_pr, '{' + namespaces['w'] + '}rPr')
        sz = etree.SubElement(r_pr, '{' + namespaces['w'] + '}sz', attrib={'{' + namespaces['w'] + '}val': '22'})
        sz_cs = etree.SubElement(r_pr, '{' + namespaces['w'] + '}szCs', attrib={'{' + namespaces['w'] + '}val': '22'})
        u = etree.SubElement(r_pr, '{' + namespaces['w'] + '}u', attrib={'{' + namespaces['w'] + '}val': 'single'})
        r = etree.SubElement(p_elem, '{' + namespaces['w'] + '}r')
        r_pr = etree.SubElement(r, '{' + namespaces['w'] + '}rPr')
        sz = etree.SubElement(r_pr, '{' + namespaces['w'] + '}sz', attrib={'{' + namespaces['w'] + '}val': '22'})
        sz_cs = etree.SubElement(r_pr, '{' + namespaces['w'] + '}szCs', attrib={'{' + namespaces['w'] + '}val': '22'})
        t = etree.SubElement(r, '{' + namespaces['w'] + '}t')
        t.text = item
        
# Function to generate XML structure for events
def generate_event_xml(event, parent, event_number, index, namespaces):
    sequence_value = f"{event_number}.{index + 1}"
    
    tr_elem = etree.SubElement(parent, '{' + namespaces['w'] + '}tr', attrib={
        '{' + namespaces['w'] + '}rsidR': '005A6BFF',
        '{' + namespaces['w'] + '}rsidRPr': '00B62852',
        '{' + namespaces['w14'] + '}paraId': str(uuid.uuid4()),
        '{' + namespaces['w14'] + '}textId': str(uuid.uuid4()),
        '{' + namespaces['w'] + '}rsidTr': '00A06E5D'
    })
    tr_pr = etree.SubElement(tr_elem, '{' + namespaces['w'] + '}trPr')
    tr_height = etree.SubElement(tr_pr, '{' + namespaces['w'] + '}trHeight', attrib={'{' + namespaces['w'] + '}val': '558'})
    
    # Column for sequence value (e.g., 1.1, 1.2)
    tc_elem = etree.SubElement(tr_elem, '{' + namespaces['w'] + '}tc')
    tc_pr = etree.SubElement(tc_elem, '{' + namespaces['w'] + '}tcPr')
    tc_width = etree.SubElement(tc_pr, '{' + namespaces['w'] + '}tcW', attrib={'{' + namespaces['w'] + '}w': '567', '{' + namespaces['w'] + '}type': 'dxa'})

    p_elem = etree.SubElement(tc_elem, '{' + namespaces['w'] + '}p', attrib={
        '{' + namespaces['w14'] + '}paraId': str(uuid.uuid4()),
        '{' + namespaces['w14'] + '}textId': str(uuid.uuid4()),
        '{' + namespaces['w'] + '}rsidR': '005A6BFF',
        '{' + namespaces['w'] + '}rsidRPr': '00B62852',
        '{' + namespaces['w'] + '}rsidRDefault': '00A06E5D',
        '{' + namespaces['w'] + '}rsidP': '00AE4681'
    })
    p_pr = etree.SubElement(p_elem, '{' + namespaces['w'] + '}pPr')
    jc = etree.SubElement(p_pr, '{' + namespaces['w'] + '}jc', attrib={'{' + namespaces['w'] + '}val': 'center'})
    r_pr = etree.SubElement(p_pr, '{' + namespaces['w'] + '}rPr')
    sz = etree.SubElement(r_pr, '{' + namespaces['w'] + '}sz', attrib={'{' + namespaces['w'] + '}val': '22'})
    sz_cs = etree.SubElement(r_pr, '{' + namespaces['w'] + '}szCs', attrib={'{' + namespaces['w'] + '}val': '22'})

    r_elem = etree.SubElement(p_elem, '{' + namespaces['w'] + '}r')
    r_pr = etree.SubElement(r_elem, '{' + namespaces['w'] + '}rPr')
    sz = etree.SubElement(r_pr, '{' + namespaces['w'] + '}sz', attrib={'{' + namespaces['w'] + '}val': '22'})
    sz_cs = etree.SubElement(r_pr, '{' + namespaces['w'] + '}szCs', attrib={'{' + namespaces['w'] + '}val': '22'})

    t_elem = etree.SubElement(r_elem, '{' + namespaces['w'] + '}t')
    t_elem.text = sequence_value

    # Columns for activity, duration, method, and fourth column
    for field, width, align in zip(['activity', 'duration', 'method', 'fourth_column'], ['5528', '1134', '1560', '1000'], ['left', 'center', 'center', 'center']):
        tc_elem = etree.SubElement(tr_elem, '{' + namespaces['w'] + '}tc')
        tc_pr = etree.SubElement(tc_elem, '{' + namespaces['w'] + '}tcPr')
        tc_width = etree.SubElement(tc_pr, '{' + namespaces['w'] + '}tcW', attrib={'{' + namespaces['w'] + '}w': width, '{' + namespaces['w'] + '}type': 'dxa'})

        p_elem = etree.SubElement(tc_elem, '{' + namespaces['w'] + '}p', attrib={
            '{' + namespaces['w14'] + '}paraId': str(uuid.uuid4()),
            '{' + namespaces['w14'] + '}textId': str(uuid.uuid4()),
            '{' + namespaces['w'] + '}rsidR': '005A6BFF',
            '{' + namespaces['w'] + '}rsidRPr': '00B62852',
            '{' + namespaces['w'] + '}rsidRDefault': '00A06E5D',
            '{' + namespaces['w'] + '}rsidP': '00AE4681'
        })
        p_pr = etree.SubElement(p_elem, '{' + namespaces['w'] + '}pPr')
        jc = etree.SubElement(p_pr, '{' + namespaces['w'] + '}jc', attrib={'{' + namespaces['w'] + '}val': align})  # Adjust alignment here
        r_pr = etree.SubElement(p_pr, '{' + namespaces['w'] + '}rPr')
        sz = etree.SubElement(r_pr, '{' + namespaces['w'] + '}sz', attrib={'{' + namespaces['w'] + '}val': '22'})
        sz_cs = etree.SubElement(r_pr, '{' + namespaces['w'] + '}szCs', attrib={'{' + namespaces['w'] + '}val': '22'})

        r_elem = etree.SubElement(p_elem, '{' + namespaces['w'] + '}r')
        r_pr = etree.SubElement(r_elem, '{' + namespaces['w'] + '}rPr')
        sz = etree.SubElement(r_pr, '{' + namespaces['w'] + '}sz', attrib={'{' + namespaces['w'] + '}val': '22'})
        sz_cs = etree.SubElement(r_pr, '{' + namespaces['w'] + '}szCs', attrib={'{' + namespaces['w'] + '}val': '22'})

        t_elem = etree.SubElement(r_elem, '{' + namespaces['w'] + '}t')
        if field != 'fourth_column':
            t_elem.text = event[field]
        else:
            t_elem.text = ""

def process_event(event_key, placeholder, event_details, namespaces):
    parent_elem = placeholder[0].getparent()
    event_number = event_key.split()[-1]
    for index, event in enumerate(event_details[event_key]['contents']):
        generate_event_xml(event, parent_elem, event_number, index, namespaces)

# Function to recreate DOCX file
def recreate_docx(source_folder, output_filename):
    # Check if the output file already exists and create a new filename if it does
    base, extension = os.path.splitext(output_filename)
    counter = 1
    new_output_filename = output_filename

    while os.path.exists(new_output_filename):
        new_output_filename = f"{base}_{counter}{extension}"
        counter += 1

    # Create a new ZIP file
    with zipfile.ZipFile(new_output_filename, 'w') as new_zip:
        # Iterate through the source folder
        for root, dirs, files in os.walk(source_folder):
            for file in files:
                # Write each file to the new ZIP file
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_folder)
                new_zip.write(file_path, arcname=arcname)
    
    return new_output_filename