"""One-time setup: download argostranslate uk->en translation model."""
import sys
import argostranslate.package
import argostranslate.translate


def install_language_pair(from_code: str, to_code: str) -> bool:
    installed = argostranslate.translate.get_installed_languages()
    src = next((l for l in installed if l.code == from_code), None)
    if src and any(t.to_lang.code == to_code for t in src.translations):
        print(f"Model {from_code}->{to_code} already installed.")
        return True

    print(f"Downloading package index...")
    argostranslate.package.update_package_index()
    available = argostranslate.package.get_available_packages()
    pkg = next((p for p in available if p.from_code == from_code and p.to_code == to_code), None)
    if not pkg:
        print(f"ERROR: package {from_code}->{to_code} not found.")
        return False

    print(f"Downloading {from_code}->{to_code} model (approx 100 MB)...")
    path = pkg.download()
    argostranslate.package.install_from_path(path)
    print(f"Model {from_code}->{to_code} installed successfully.")
    return True


if __name__ == "__main__":
    ok = install_language_pair("uk", "en")
    sys.exit(0 if ok else 1)
