'''
Цей скрипт порівнює два файла з аліасами.
Він знаходить які адреси аліасів присутні в другому файлі,але відсутні в першому.
Потім він створює новий файл "new_aliases.xml", який копіює перший файл та додає відсутні адреси з другого.
'''

import xml.etree.ElementTree as ET
import os
from collections import defaultdict

def process_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    aliases_dict = defaultdict(list)

    for alias in root.findall(".//alias"):
        name = alias.find("name")
        addresses = alias.findall("address")
        
        if name is not None:
            alias_name = name.text
            alias_addresses = ' '.join([address.text for address in addresses if address.text is not None])
            aliases_dict[alias_name].append(alias_addresses)
    
    return aliases_dict, tree

def compare_addresses(list_a, list_b):
    addresses_a = set(list_a.split())
    addresses_b = set(list_b.split())
    missing_addresses = addresses_b - addresses_a

    if missing_addresses:
        print(f"  Addresses in the second list but not in the first list:")
        for address in missing_addresses:
            print(f"    {address}")
    else:
        print("  No new addresses in the second list compared to the first list.")

def merge_addresses(list_a, list_b):
    addresses_a = set(list_a.split())
    addresses_b = set(list_b.split())
    merged_addresses = addresses_a.union(addresses_b)
    return ' '.join(sorted(merged_addresses))

#Файли, які порівнюються(скріпт знаходить які адреси аліасів присутні в другому файлі,але відсутні в першому)
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
file_names = ["test-aliases-main.xml", "test-aliases-motovylivka.xml"]

all_aliases = defaultdict(list)

first_file_aliases, first_tree = process_xml_file(os.path.join(desktop_path, file_names[0]))
second_file_aliases = process_xml_file(os.path.join(desktop_path, file_names[1]))[0]

for file_name in file_names:
    file_path = os.path.join(desktop_path, file_name)
    aliases, _ = process_xml_file(file_path)
    for alias_name, address_lists in aliases.items():
        all_aliases[alias_name].extend(address_lists)

for alias_name, address_lists in all_aliases.items():
    print(f"Alias: {alias_name}")
    print(f"Number of address lists: {len(address_lists)}")
    for i, addr_list in enumerate(address_lists):
        print(f"  List {i + 1}: {addr_list}")
    
    if len(address_lists) >= 2:
        compare_addresses(address_lists[0], address_lists[1])
    else:
        print("  Not enough lists to compare")
    print()

for alias_name, address_lists in second_file_aliases.items():
    if alias_name in first_file_aliases:
        merged_addresses = merge_addresses(first_file_aliases[alias_name][0], address_lists[0])
        first_file_aliases[alias_name][0] = merged_addresses

root = first_tree.getroot()
for alias in root.findall(".//alias"):
    name = alias.find("name")
    if name is not None and name.text in first_file_aliases:
        addresses = alias.findall("address")
        
        for address in addresses:
            alias.remove(address)
        
        new_address = ET.SubElement(alias, "address")
        new_address.text = first_file_aliases[name.text][0]

#Назва нового файлу
new_file_path = os.path.join(desktop_path, "new_aliases.xml")
first_tree.write(new_file_path, encoding="utf-8", xml_declaration=True)

print(f"Merged aliases have been saved to: {new_file_path}")