"""XMLHandler — Đọc/ghi dữ liệu XML. Files: contracts.xml, rental_applications.xml, repair_requests.xml"""
import os
from typing import Dict, List, Optional
from lxml import etree


class XMLHandler:
    @staticmethod
    def _ensure_file(file_path: str, root_tag: str = 'root') -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            root = etree.Element(root_tag)
            tree = etree.ElementTree(root)
            tree.write(file_path, pretty_print=True, xml_declaration=True, encoding='utf-8')

    @staticmethod
    def load(file_path: str, root_tag: str = 'root') -> etree._Element:
        XMLHandler._ensure_file(file_path, root_tag)
        try:
            tree = etree.parse(file_path)
            return tree.getroot()
        except:
            root = etree.Element(root_tag)
            return root

    @staticmethod
    def save(file_path: str, root: etree._Element) -> None:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        tree = etree.ElementTree(root)
        tree.write(file_path, pretty_print=True, xml_declaration=True, encoding='utf-8')

    @staticmethod
    def _element_to_dict(element: etree._Element) -> Dict:
        result = {}
        for child in element:
            text = child.text or ''
            # Tự chuyển đổi kiểu dữ liệu
            if text.isdigit():
                result[child.tag] = int(text)
            else:
                result[child.tag] = text
        return result

    @staticmethod
    def _dict_to_element(tag: str, data: Dict) -> etree._Element:
        element = etree.Element(tag)
        for key, value in data.items():
            child = etree.SubElement(element, key)
            child.text = str(value) if value is not None else ''
        return element

    @staticmethod
    def add_item(file_path: str, item: Dict, root_tag: str = 'root', item_tag: str = 'item') -> Dict:
        root = XMLHandler.load(file_path, root_tag)
        # Auto ID
        max_id = 0
        for elem in root:
            id_elem = elem.find('id')
            if id_elem is not None and id_elem.text and id_elem.text.isdigit():
                max_id = max(max_id, int(id_elem.text))
        item['id'] = max_id + 1
        element = XMLHandler._dict_to_element(item_tag, item)
        root.append(element)
        XMLHandler.save(file_path, root)
        return item

    @staticmethod
    def update_item(file_path: str, item_id: int, updates: Dict, root_tag: str = 'root') -> bool:
        root = XMLHandler.load(file_path, root_tag)
        for elem in root:
            id_elem = elem.find('id')
            if id_elem is not None and id_elem.text == str(item_id):
                for key, value in updates.items():
                    child = elem.find(key)
                    if child is not None:
                        child.text = str(value) if value is not None else ''
                    else:
                        child = etree.SubElement(elem, key)
                        child.text = str(value) if value is not None else ''
                XMLHandler.save(file_path, root)
                return True
        return False

    @staticmethod
    def delete_item(file_path: str, item_id: int, root_tag: str = 'root') -> bool:
        root = XMLHandler.load(file_path, root_tag)
        for elem in root:
            id_elem = elem.find('id')
            if id_elem is not None and id_elem.text == str(item_id):
                root.remove(elem)
                XMLHandler.save(file_path, root)
                return True
        return False

    @staticmethod
    def find_by_id(file_path: str, item_id: int, root_tag: str = 'root') -> Optional[Dict]:
        root = XMLHandler.load(file_path, root_tag)
        for elem in root:
            id_elem = elem.find('id')
            if id_elem is not None and id_elem.text == str(item_id):
                return XMLHandler._element_to_dict(elem)
        return None

    @staticmethod
    def get_all(file_path: str, root_tag: str = 'root') -> List[Dict]:
        root = XMLHandler.load(file_path, root_tag)
        return [XMLHandler._element_to_dict(elem) for elem in root]
