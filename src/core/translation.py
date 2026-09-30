from typing import Dict

class TranslationService:
    def __init__(self):
        self.supported_locales = ["en", "fr", "ar"]

    def translate_item(self, item: dict, target_lang: str) -> dict:
        """
        Translates item name and description to target language.
        Falls back to 'en' if requested language is unavailable.
        """
        lang = target_lang if target_lang in self.supported_locales else "en"
        
        name_dict = item.get("name", {})
        desc_dict = item.get("description", {})
        
        translated_name = name_dict.get(lang, name_dict.get("en", "Unnamed Item"))
        translated_desc = desc_dict.get(lang, desc_dict.get("en", ""))
        
        item_copy = dict(item)
        item_copy["name_translated"] = translated_name
        item_copy["description_translated"] = translated_desc
        item_copy["active_language"] = lang
        return item_copy

translator = TranslationService()
