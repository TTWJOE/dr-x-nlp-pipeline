from argostranslate import package, translate

# One-time setup (downloads EN -> AR package if missing)
def setup_translation():
    available_packages = package.get_available_packages()
    en_ar_package = next((p for p in available_packages if p.from_code == "en" and p.to_code == "ar"), None)

    if en_ar_package:
        print("🔁 Downloading English ➝ Arabic translation package...")
        package.install_from_path(en_ar_package.download())

def translate_to_arabic(text: str) -> str:
    installed_languages = translate.get_installed_languages()
    from_lang = next((lang for lang in installed_languages if lang.code == "en"), None)
    to_lang = next((lang for lang in installed_languages if lang.code == "ar"), None)

    if from_lang and to_lang:
        translation = from_lang.get_translation(to_lang)
        return translation.translate(text)
    else:
        raise RuntimeError("⚠️ English ➝ Arabic language package is not installed.")
