from typing import Dict, List

class TranslationService:
    """
    10-Language UK Multicultural Menu Translation Engine.
    Supports English (en), French (fr), Arabic (ar), Polish (pl), Urdu (ur),
    Bengali (bn), Punjabi (pa), Mandarin (zh), Spanish (es), and Turkish (tr).
    """

    LANGUAGE_METADATA: Dict[str, dict] = {
        "en": {"code": "en", "name": "English", "native_name": "English", "flag": "🇬🇧", "rtl": False, "uk_cities": "Nationwide"},
        "fr": {"code": "fr", "name": "French", "native_name": "Français", "flag": "🇫🇷", "rtl": False, "uk_cities": "London, Eurostar Corridor"},
        "ar": {"code": "ar", "name": "Arabic", "native_name": "العربية", "flag": "🇸🇦", "rtl": True, "uk_cities": "London (Edgware Rd, Knightsbridge), Manchester"},
        "pl": {"code": "pl", "name": "Polish", "native_name": "Polski", "flag": "🇵🇱", "rtl": False, "uk_cities": "London, Birmingham, Leeds, Glasgow"},
        "ur": {"code": "ur", "name": "Urdu", "native_name": "اردو", "flag": "🇵🇰", "rtl": True, "uk_cities": "Bradford, Birmingham, Manchester, East London"},
        "bn": {"code": "bn", "name": "Bengali", "native_name": "বাংলা", "flag": "🇧🇩", "rtl": False, "uk_cities": "Tower Hamlets (Brick Lane), Oldham, Luton"},
        "pa": {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ", "flag": "🇮🇳", "rtl": False, "uk_cities": "Southall, Wolverhampton, Leicester, Coventry"},
        "zh": {"code": "zh", "name": "Mandarin", "native_name": "中文 (普通话)", "flag": "🇨🇳", "rtl": False, "uk_cities": "Soho Chinatown, Manchester, Edinburgh, Cambridge"},
        "es": {"code": "es", "name": "Spanish", "native_name": "Español", "flag": "🇪🇸", "rtl": False, "uk_cities": "London (Elephant & Castle), Bristol, Brighton"},
        "tr": {"code": "tr", "name": "Turkish", "native_name": "Türkçe", "flag": "🇹🇷", "rtl": False, "uk_cities": "Dalston, Harringay, Enfield, North London"},
    }

    MULTICULTURAL_CATALOG: Dict[str, Dict[str, Dict[str, str]]] = {
        "item-1": {
            "pl": {"name": "Ryba z Frytkami (Fish & Chips)", "desc": "Świeży dorsz atlantycki z chrupiącymi frytkami"},
            "ur": {"name": "فش اینڈ چپس (حلال کوڈ)", "desc": "تازہ اٹلانٹک مچھلی اور خستہ چپس"},
            "bn": {"name": "ফিশ অ্যান্ড চিপস", "desc": "তাজা আটলান্টিক কড মাছ এবং মচমচে চিপস"},
            "pa": {"name": "ਫਿਸ਼ ਐਂਡ ਚਿਪਸ", "desc": "ਤਾਜ਼ਾ ਅਟਲਾਂਟਿਕ ਕੌਡ ਮੱਛੀ ਅਤੇ ਕੁਰਕੁਰੇ ਚਿਪਸ"},
            "zh": {"name": "英式炸鱼薯条", "desc": "新鲜大西洋鳕鱼配香脆薯条"},
            "es": {"name": "Pescado y Patatas Fritas (Fish & Chips)", "desc": "Bacalao fresco del Atlántico con patatas crujientes"},
            "tr": {"name": "Balık ve Patates Kızartması (Fish & Chips)", "desc": "Çıtır patates kızartması ile taze Atlantik morina balığı"},
        },
        "item-2": {
            "pl": {"name": "Pełne Śniadanie Angielskie", "desc": "Kiełbaski, bekon, jajka, fasolka, tosty"},
            "ur": {"name": "فل انگلش ناشتہ", "desc": "سوسیجز، بیکن، انڈے، بینز اور ٹوسٹ"},
            "bn": {"name": "ফুল ইংলিশ ব্রেকফাস্ট", "desc": "সসেজ, বেকন, ডিম, বিনস এবং টোস্ট"},
            "pa": {"name": "ਫੁੱਲ ਇੰਗਲਿਸ਼ ਬ੍ਰੇਕਫਾਸਟ", "desc": "ਸੌਸੇਜ, ਬੇਕਨ, ਅੰਡੇ, ਬੀਨਜ਼ ਅਤੇ ਟੋਸਟ"},
            "zh": {"name": "全套英式早餐", "desc": "香肠、培根、鸡蛋、茄汁焗豆与烤吐司"},
            "es": {"name": "Desayuno Inglés Completo", "desc": "Salchichas, bacon, huevos, judías y tostadas"},
            "tr": {"name": "Tam İngiliz Kahvaltısı", "desc": "Sosis, pastırma, yumurta, kuru fasulye ve kızarmış ekmek"},
        },
        "item-3": {
            "pl": {"name": "Rzemieślnicze Piwo IPA (Pinta)", "desc": "Lokalne brytyjskie piwo rzemieślnicze IPA"},
            "ur": {"name": "کرافٹ آئی پی اے پائنٹ", "desc": "مقامی برطانوی کرافٹ بریوری آئی پی اے"},
            "bn": {"name": "ক্রাফট আইপিএ পিন্ট", "desc": "স্থানীয় ইউকে ক্রাফট ব্রিউয়ারি আইপিএ"},
            "pa": {"name": "ਕ੍ਰਾਫਟ ਆਈਪੀਏ ਪਿੰਟ", "desc": "ਸਥਾਨਕ ਯੂਕੇ ਕ੍ਰਾਫਟ ਬਰੂਅਰੀ ਆਈਪੀਏ"},
            "zh": {"name": "精酿 IPA 啤酒 (一品脱)", "desc": "英国本地精酿酒厂鲜酿 IPA"},
            "es": {"name": "Pinta de Cerveza Artesanal IPA", "desc": "Cerveza IPA artesanal de cervecería británica local"},
            "tr": {"name": "Butik IPA Bira (Pint)", "desc": "Yerel İngiliz butik bira fabrikası IPA"},
        },
        "item-4": {
            "pl": {"name": "Sos Tatarski i Groszek z Miętą", "desc": "Domowy sos tatarski i tłuczony groszek z miętą"},
            "ur": {"name": "ٹارٹار ساس اور پودینے والے مٹر", "desc": "گھریلو ٹارٹار ساس اور پودینے کے ساتھ پسے ہوئے مٹر"},
            "bn": {"name": "টার্টার সস ও পুদিনা মটরশুঁটি", "desc": "ঘরে তৈরি টার্টার সস এবং পুদিনা মটরশুঁটি"},
            "pa": {"name": "ਟਾਰਟਰ ਸੌਸ ਅਤੇ ਪੁਦੀਨਾ ਮਟਰ", "desc": "ਘਰ ਦੀ ਬਣੀ ਟਾਰਟਰ ਸੌਸ ਅਤੇ ਪੁਦੀਨੇ ਵਾਲੇ ਮਟਰ"},
            "zh": {"name": "塔塔酱配薄荷青豆泥", "desc": "秘制手工塔塔酱与薄荷鲜青豆泥"},
            "es": {"name": "Salsa Tártara y Guisantes a la Menta", "desc": "Salsa tártara casera y guisantes machacados con menta"},
            "tr": {"name": "Tartar Sos ve Naneli Bezelye Püresi", "desc": "Ev yapımı tartar sos ve ezilmiş naneli bezelye"},
        },
        "item-5": {
            "pl": {"name": "Świeży Sok Pomarańczowy", "desc": "Świeżo wyciskany sok z pomarańczy"},
            "ur": {"name": "تازہ مالٹے کا جوس", "desc": "تازہ نچوڑا ہوا خالص جوس"},
            "bn": {"name": "তাজা কমলার রস", "desc": "সদ্য নিংড়ানো তাজা কমলার রস"},
            "pa": {"name": "ਤਾਜ਼ਾ ਸੰਤਰੇ ਦਾ ਜੂਸ", "desc": "ਤਾਜ਼ਾ ਨਿਚੋੜਿਆ ਹੋਇਆ ਸੰਤਰੇ ਦਾ ਜੂਸ"},
            "zh": {"name": "鲜榨橙汁", "desc": "100% 每日鲜榨纯橙汁"},
            "es": {"name": "Zumo de Naranja Natural", "desc": "Zumo recién exprimido al momento"},
            "tr": {"name": "Taze Sıkılmış Portakal Suyu", "desc": "Günlük taze sıkılmış doğal portakal suyu"},
        },
    }

    def __init__(self):
        self.supported_locales = ["en", "fr", "ar", "pl", "ur", "bn", "pa", "zh", "es", "tr"]

    def get_supported_languages(self) -> List[dict]:
        return [self.LANGUAGE_METADATA[code] for code in self.supported_locales]

    def translate_item(self, item: dict, target_lang: str) -> dict:
        """
        Translates item name and description to target language across all 10 UK multicultural locales.
        Falls back to 'en' if requested language is unavailable.
        """
        lang = (target_lang or "en").lower().strip()
        if lang not in self.supported_locales:
            lang = "en"

        item_id = item.get("id", "")
        name_dict = item.get("name", {})
        desc_dict = item.get("description", {})

        extra_locale = self.MULTICULTURAL_CATALOG.get(item_id, {}).get(lang, {})

        translated_name = (
            name_dict.get(lang)
            or extra_locale.get("name")
            or name_dict.get("en", "Unnamed Item")
        )
        translated_desc = (
            desc_dict.get(lang)
            or extra_locale.get("desc")
            or desc_dict.get("en", "")
        )

        item_copy = dict(item)
        item_copy["name_translated"] = translated_name
        item_copy["description_translated"] = translated_desc
        item_copy["active_language"] = lang
        item_copy["is_rtl"] = self.LANGUAGE_METADATA.get(lang, {}).get("rtl", False)
        return item_copy


translator = TranslationService()
