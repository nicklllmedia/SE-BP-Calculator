import os
import xml.etree.ElementTree as ET
import xml.dom.minidom

# The following variables are for inserting your game folder path and mod folder path for parsing data.
# Keep in mind that order of list matters. If you wish to add more folders to the list, use any
# variable name ("modFolder1" in example) and any path you wish ("O:\\Games_folder\\steamapps\\workshop\\content\\244850" in example).
# If you wish to disable Blacklist, then just comment any path with "# " in the beginning of the line.
# Example: 
# "modFolder1": "O:\\Games_folder\\steamapps\\workshop\\content\\244850"
# "blacklistFolder1": "O:/Games_folder/steamapps/workshop/content/244850/3000136372"

your_gameContentData_folder = {
    "vanillaGamePath": "[Insert your game folder path here]"
    ,"modFolder1": "[Insert your mod folder path here]"
    # ,"modFolder2": "[Insert your mod folder path here]"
    }
your_contentBlacklist_folder = {
    "blacklistFolder1": "[Insert your mod folder path here]"
    # ,"blacklistFolder2": "[Insert your blacklist folder here]"
    }

# Parsing folders and search for direct match of Elements and SubElements
def parse_sbc_files(folder_dict, blacklist_dict):
    components = {}
    blueprints = {}
    cube_blocks = {}

    for folder_path in folder_dict.values():
        for root_dir, _, files in os.walk(folder_path):
            if any(os.path.commonpath([root_dir, blacklisted]) == blacklisted for blacklisted in blacklist_dict.values()):
                continue

            for filename in files:
                if filename.endswith('.sbc'):
                    file_path = os.path.join(root_dir, filename)
                    try:
                        tree = ET.parse(file_path)
                        root = tree.getroot()

                        for component in root.findall('.//Component'):
                            subtype_id = component.find('./Id/SubtypeId')
                            display_name = component.find('./DisplayName')

                            if subtype_id is not None and display_name is not None:
                                key = (subtype_id.text, display_name.text)
                                components[key] = {
                                    'SubtypeId': subtype_id.text,
                                    'DisplayName': display_name.text
                                }

                        for blueprint in root.findall('.//Blueprint'):
                            subtype_id = blueprint.find('./Id/SubtypeId')
                            display_name = blueprint.find('./DisplayName')
                            prerequisites = blueprint.findall('./Prerequisites/Item')
                            results = blueprint.findall('./Results/Item')
                            result = blueprint.find('./Result')

                            if subtype_id is not None and display_name is not None:
                                key = (subtype_id.text, display_name.text)
                                blueprint_data = {
                                    'SubtypeId': subtype_id.text,
                                    'DisplayName': display_name.text,
                                    'Prerequisites': sum_items(prerequisites),
                                    'Results': sum_items(results),
                                    'Result': {
                                        'Amount': result.get('Amount'),
                                        'TypeId': result.get('TypeId'),
                                        'SubtypeId': result.get('SubtypeId')
                                    } if result is not None else {}
                                }
                                blueprints[key] = blueprint_data

                        for cube_block in root.findall('.//CubeBlocks/Definition'):
                            subtype_id = cube_block.find('./Id/SubtypeId')
                            display_name = cube_block.find('./DisplayName')
                            cube_size = cube_block.find('./CubeSize')
                            components_elements = cube_block.findall('./Components/Component')

                            if subtype_id is not None and display_name is not None and cube_size is not None:
                                key = (subtype_id.text, display_name.text, cube_size.text)
                                cube_block_data = {
                                    'SubtypeId': subtype_id.text,
                                    'DisplayName': display_name.text,
                                    'CubeSize': cube_size.text,
                                    'Components': sum_components(components_elements)
                                }
                                cube_blocks[key] = cube_block_data

                    except ET.ParseError as e:
                        print(f"Error parsing file {filename}: {e}")

    print(f"Found {len(components)} unique components.")
    print(f"Found {len(blueprints)} unique blueprints.")
    print(f"Found {len(cube_blocks)} unique cube blocks.")
    return list(components.values()), list(blueprints.values()), list(cube_blocks.values())

# Combining the matching Prerequisites for Blueprints and matching Components for Blocks
def sum_items(items):
    item_dict = {}

    for item in items:
        subtype_id = item.get('SubtypeId')
        amount = float(item.get('Amount', 0))

        if subtype_id in item_dict:
            item_dict[subtype_id] += amount
        else:
            item_dict[subtype_id] = amount

    return [{'SubtypeId': k, 'Amount': v, 'TypeId': next(item.get('TypeId') for item in items if item.get('SubtypeId') == k)} for k, v in item_dict.items()]

def sum_components(components):
    component_dict = {}

    for component in components:
        subtype_id = component.get('Subtype')
        count = int(component.get('Count', 0))

        if subtype_id in component_dict:
            component_dict[subtype_id] += count
        else:
            component_dict[subtype_id] = count

    return [{'Subtype': k, 'Count': v} for k, v in component_dict.items()]

# Combines and writes all the data into "debug1.xml"
def write_to_output_file(output_path, components, blueprints, cube_blocks):
    root = ET.Element('Definitions')

    components_element = ET.SubElement(root, 'Components')
    for comp in components:
        component_element = ET.SubElement(components_element, 'Component')
        subtype_id_element = ET.SubElement(component_element, 'SubtypeId')
        subtype_id_element.text = comp['SubtypeId']
        display_name_element = ET.SubElement(component_element, 'DisplayName')
        display_name_element.text = comp['DisplayName']

    blueprints_element = ET.SubElement(root, 'Blueprints')
    for bp in blueprints:
        blueprint_element = ET.SubElement(blueprints_element, 'Blueprint')
        subtype_id_element = ET.SubElement(blueprint_element, 'SubtypeId')
        subtype_id_element.text = bp['SubtypeId']
        display_name_element = ET.SubElement(blueprint_element, 'DisplayName')
        display_name_element.text = bp['DisplayName']
        
        prerequisites_element = ET.SubElement(blueprint_element, 'Prerequisites')
        for item in bp['Prerequisites']:
            item_element = ET.SubElement(prerequisites_element, 'Item', Amount=str(item['Amount']), TypeId=item['TypeId'], SubtypeId=item['SubtypeId'])

        results_element = ET.SubElement(blueprint_element, 'Results')
        for item in bp['Results']:
            item_element = ET.SubElement(results_element, 'Item', Amount=str(item['Amount']), TypeId=item['TypeId'], SubtypeId=item['SubtypeId'])

        if bp['Result']:
            result_element = ET.SubElement(blueprint_element, 'Result', Amount=bp['Result']['Amount'], TypeId=bp['Result']['TypeId'], SubtypeId=bp['Result']['SubtypeId'])

    cube_blocks_element = ET.SubElement(root, 'CubeBlocks')
    for cb in cube_blocks:
        definition_element = ET.SubElement(cube_blocks_element, 'Definition')
        subtype_id_element = ET.SubElement(definition_element, 'SubtypeId')
        subtype_id_element.text = cb['SubtypeId']
        display_name_element = ET.SubElement(definition_element, 'DisplayName')
        display_name_element.text = cb['DisplayName']
        cube_size_element = ET.SubElement(definition_element, 'CubeSize')
        cube_size_element.text = cb['CubeSize']
        
        components_element = ET.SubElement(definition_element, 'Components')
        for component in cb['Components']:
            component_element = ET.SubElement(components_element, 'Component', Subtype=component['Subtype'], Count=str(component['Count']))

    try:
        xml_str = ET.tostring(root, encoding='utf-8', method='xml')
        pretty_xml_str = xml.dom.minidom.parseString(xml_str).toprettyxml(indent="    ")

        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(pretty_xml_str)
    except Exception as e:
        print(f"Error writing to output file: {e}")

if __name__ == "__main__":
    output_file = os.path.join(os.path.dirname(__file__), 'parsedData.xml')

    components, blueprints, cube_blocks = parse_sbc_files(your_gameContentData_folder, your_contentBlacklist_folder)
    write_to_output_file(output_file, components, blueprints, cube_blocks)
    print(f"Extracted data written to {output_file}")
