import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

# Check file paths
def load_xml(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} not found!")
        exit(1)
    return ET.parse(file_path).getroot()

def get_script_directory():
    return os.path.dirname(os.path.abspath(__file__))

# Introduce Component data and filter out duplicates
def get_component_info(db_root, subtype_id):
    for component in db_root.find('Components').findall('Component'):
        if component.find('SubtypeId').text == subtype_id:
            display_name = component.find('DisplayName').text
            blueprints = []
            for bp in db_root.find('Blueprints').findall('Blueprint'):
                if bp.find('DisplayName').text == display_name:
                    blueprints.append(bp)
            if len(blueprints) > 1:
                print(f"Duplicate Blueprint entry found, processing the last: {display_name}, total of {len(blueprints)}")
            return display_name, blueprints[-1] if blueprints else None
    return None, None

# Convert Component name into Blueprint name
def find_prerequisite_info(db_root, subtype_id):
    for component in db_root.find('Components').findall('Component'):
        if component.find('SubtypeId').text == subtype_id:
            return component.find('DisplayName').text
    return None

# Check and store valid Result/s field of Blueprint
def get_result_amount(blueprint):
    result_element = blueprint.find('Result')
    if result_element is not None and 'Amount' in result_element.attrib:
        return float(result_element.attrib['Amount'])
    
    results_element = blueprint.find('Results')
    if results_element is not None:
        result_elements = results_element.findall('Item')
        if result_elements and 'Amount' in result_elements[0].attrib:
            return float(result_elements[0].attrib['Amount'])
    
    return None

# All the math to divide the Component count by Result amount and multiply the result by Item Component counts
def calculate_totals(input_root, db_root):
    categorized_totals = {}
    total = {}
    for display_name in input_root.findall('DisplayName'):
        name = display_name.attrib['Name']
        components = display_name.findall('Component')
        display_totals = {}
        for component in components:
            subtype = component.attrib['Subtype']
            count = int(component.attrib['Count'])
            display_name, blueprint = get_component_info(db_root, subtype)
            if not blueprint:
                print(f"No matching Blueprint for Component: {display_name}")
                continue
            
            result_amount = get_result_amount(blueprint)
            if result_amount is None:
                print(f"No result amount found for Blueprint: {display_name}")
                continue

            for item in blueprint.find('Prerequisites').findall('Item'):
                item_amount = float(item.attrib['Amount'])
                item_type = item.attrib['TypeId']
                item_subtype = item.attrib['SubtypeId']
                total_amount = (count / result_amount) * item_amount
                
                if item_subtype not in display_totals:
                    display_totals[item_subtype] = {'TypeId': item_type, 'Amount': 0}
                display_totals[item_subtype]['Amount'] += total_amount

                if item_subtype not in total:
                    total[item_subtype] = {'TypeId': item_type, 'Amount': 0}
                total[item_subtype]['Amount'] += total_amount

                # Check for prerequisite components and process matches
                prerequisite_display_name = find_prerequisite_info(db_root, item_subtype)
                if prerequisite_display_name:
                    blueprint_display_name, prerequisite_blueprint = get_component_info(db_root, item_subtype)
                    if prerequisite_blueprint:
                        prerequisite_result_amount = get_result_amount(prerequisite_blueprint)
                        if prerequisite_result_amount is None:
                            print(f"No Result amount found for Blueprint prerequisite: {prerequisite_display_name}")
                            continue

                        for prerequisite_item in prerequisite_blueprint.find('Prerequisites').findall('Item'):
                            prerequisite_item_amount = float(prerequisite_item.attrib['Amount'])
                            prerequisite_item_type = prerequisite_item.attrib['TypeId']
                            prerequisite_item_subtype = prerequisite_item.attrib['SubtypeId']
                            prerequisite_total_amount = (total_amount / prerequisite_result_amount) * prerequisite_item_amount
                            
                            if prerequisite_item_subtype not in display_totals:
                                display_totals[prerequisite_item_subtype] = {'TypeId': prerequisite_item_type, 'Amount': 0}
                            display_totals[prerequisite_item_subtype]['Amount'] += prerequisite_total_amount

                            if prerequisite_item_subtype not in total:
                                total[prerequisite_item_subtype] = {'TypeId': prerequisite_item_type, 'Amount': 0}
                            total[prerequisite_item_subtype]['Amount'] += prerequisite_total_amount

                        # Remove the excessive output entries if SubtypeID in Item was found in Components DispayName
                        if item_subtype in display_totals:
                            del display_totals[item_subtype]
                        if item_subtype in total:
                            del total[item_subtype]
                            print(f"Removed match-in-match item from list: {item_subtype}")

        categorized_totals[name] = display_totals
    return categorized_totals, total

# Writing and composing the output file
def write_output(categorized_totals, total, output_path):
    root = ET.Element('Definitions')
    
    # Add categories by DisplayName
    for display_name, totals in categorized_totals.items():
        display_elem = ET.SubElement(root, 'DisplayName', {'Name': display_name})
        for subtype, info in totals.items():
            ET.SubElement(display_elem, 'Component', {
                'Subtype': subtype,
                'TypeId': info['TypeId'],
                'Count': str(info['Amount'])
            })

    # Add the final Total category
    total_elem = ET.SubElement(root, 'Total')
    for subtype, info in total.items():
        ET.SubElement(total_elem, 'Component', {
            'Subtype': subtype,
            'TypeId': info['TypeId'],
            'Count': str(info['Amount'])
        })

    # Convert to string with pretty printing
    xml_str = ET.tostring(root, encoding='utf-8')
    pretty_xml_str = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="    ")

    # Write to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_xml_str)

# Run the code
if __name__ == "__main__":
    script_dir = get_script_directory()
    db_file = os.path.join(script_dir, "parsedData.xml")
    input_file = os.path.join(script_dir, "exportComponents.xml")
    output_file = os.path.join(script_dir, "exportMaterials.xml")

    db_root = load_xml(db_file)
    input_root = load_xml(input_file)

    categorized_totals, total = calculate_totals(input_root, db_root)
    write_output(categorized_totals, total, output_file)
