import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

# The following variables are for inserting your game folder path and mod folder path for parsing data.
# Keep in mind that order of list matters. If you wish to add more folders to the list, use any
# variable name ("modFolder1" in example) and any path you wish ("O:\\Games_folder\\steamapps\\workshop\\content\\244850" in example).
# If you wish to disable Blacklist, then just comment any path with "# " in the beginning of the line.
# Example: 
# "blueprintFolder1": "C:\\Users\\MyPC\\AppData\\Roaming\\SpaceEngineers\\Blueprints\\local\\MyShipBuild"
# "blacklistFolder1": "C:/Users/MyPC/AppData/Roaming/SpaceEngineers/Blueprints/local/MyShipBuild"

your_gameBlueprint_folder = {
    "blueprintFolder1": "[Insert your bp.sbc folder path here]"
    # ,"blueprintFolder2": "[Insert your bp.sbc folder path here]"
    }
your_contentBlacklist_folder = {
    "blacklistFolder1": "[Insert your bp.sbc folder path here]"
    # ,"blacklistFolder2": "[Insert your bp.sbc folder path here]"
    }

def parse_input_files(input_dirs, blacklist_dirs):
    input_files = []
    for input_dir in input_dirs.values():
        for root, dirs, files in os.walk(input_dir):
            if any(bl in root for bl in blacklist_dirs.values()):
                continue
            for file in files:
                if file.endswith('.sbc'):
                    input_files.append(os.path.join(root, file))
    return input_files

def parse_database_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_file_path = os.path.join(script_dir, 'parsedData.xml')
    if not os.path.exists(db_file_path):
        print("Database file 'parsedData.xml' not found. Stopping execution.")
        exit(1)
    return ET.parse(db_file_path).getroot()

def parse_component_counts(input_file, database_root, counts):
    tree = ET.parse(input_file)
    root = tree.getroot()
    for cube_grid in root.findall('.//CubeGrid'):
        display_name = cube_grid.find('DisplayName').text
        for block in cube_grid.findall('.//MyObjectBuilder_CubeBlock'):
            subtype_name = block.find('SubtypeName').text
            if subtype_name:
                match_found = False
                for definition in database_root.findall('.//Definition'):
                    subtype_id = definition.find('SubtypeId').text
                    if subtype_id == subtype_name:
                        match_found = True
                        for component in definition.findall('.//Component'):
                            subtype = component.get('Subtype')
                            count = int(component.get('Count'))
                            if display_name not in counts:
                                counts[display_name] = {}
                            if subtype not in counts[display_name]:
                                counts[display_name][subtype] = 0
                            counts[display_name][subtype] += count
                if not match_found:
                    print(f"No match found for block: {subtype_name}")
    return counts

def write_output_file(counts, script_dir):
    root = ET.Element('Definitions')
    total_counts = {}

    for display_name, components in counts.items():
        display_elem = ET.SubElement(root, 'DisplayName')
        display_elem.set('Name', display_name)
        for subtype, count in components.items():
            component = ET.SubElement(display_elem, 'Component')
            component.set('Subtype', subtype)
            component.set('Count', str(count))
            if subtype not in total_counts:
                total_counts[subtype] = 0
            total_counts[subtype] += count

    total_elem = ET.SubElement(root, 'Total')
    for subtype, count in total_counts.items():
        component = ET.SubElement(total_elem, 'Component')
        component.set('Subtype', subtype)
        component.set('Count', str(count))

    tree = ET.ElementTree(root)
    output_path = os.path.join(script_dir, 'exportComponents.xml')

    # Pretty printing
    xmlstr = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
    with open(output_path, "w") as f:
        f.write(xmlstr)

    print(f"Extracted data written to {output_path}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_files = parse_input_files(your_gameBlueprint_folder, your_contentBlacklist_folder)
    database_root = parse_database_file()
    counts = {}
    for input_file in input_files:
        counts = parse_component_counts(input_file, database_root, counts)
    write_output_file(counts, script_dir)

if __name__ == '__main__':
    main()
