import os
import json
import re

# Paths
LOCALES_DIR = 'src/i18n/locales/en'
SRC_DIR = 'src'

def load_translations():
    translations = {}
    for filename in os.listdir(LOCALES_DIR):
        if filename.endswith('.json'):
            ns = filename.replace('.json', '')
            with open(os.path.join(LOCALES_DIR, filename), 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, val in data.items():
                    # We only care about string values
                    if isinstance(val, str) and len(val.strip()) > 2 and '{{' not in val:
                        translations[val.strip()] = f"{ns}:{key}"
    return translations

def process_file(filepath, translations):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    namespaces_used = set()
    
    # Sort translations by length descending to match longest first
    sorted_items = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)

    for text, key_path in sorted_items:
        ns = key_path.split(':')[0]
        
        # Regex to match exactly >Text< or > Text <
        # and replace with >{t('ns:key')}<
        escaped_text = re.escape(text)
        
        # Match JSX text
        pattern_jsx = r'>\s*' + escaped_text + r'\s*<'
        def repl_jsx(match):
            namespaces_used.add(ns)
            return f">{{t('{key_path}')}}<"
        
        content = re.sub(pattern_jsx, repl_jsx, content)
        
        # Match "Text" in attributes (simplified, risky but often works for placeholders if no variables)
        pattern_attr = r'placeholder="' + escaped_text + r'"'
        def repl_attr(match):
            namespaces_used.add(ns)
            return f'placeholder={{t(\'{key_path}\')}}'
        content = re.sub(pattern_attr, repl_attr, content)
        
        pattern_title = r'title="' + escaped_text + r'"'
        def repl_title(match):
            namespaces_used.add(ns)
            return f'title={{t(\'{key_path}\')}}'
        content = re.sub(pattern_title, repl_title, content)

    if content != original_content:
        # Inject import if needed
        if 'useTranslation' not in content:
            import_statement = "import { useTranslation } from 'react-i18next';\n"
            # insert after last import
            imports = list(re.finditer(r'^import .*;', content, re.MULTILINE))
            if imports:
                last_import = imports[-1]
                insert_idx = last_import.end() + 1
                content = content[:insert_idx] + import_statement + content[insert_idx:]
            else:
                content = import_statement + content
                
        # Inject hook inside the first exported function if not present
        if 'const { t }' not in content and 'const {' not in content.split('useTranslation')[0][-20:]:
            # find export const or export function
            match = re.search(r'export (?:const|function) (\w+)[^\(]*\([^\)]*\)[^\{]*\{', content)
            if match:
                ns_str = "['" + "', '".join(namespaces_used) + "']"
                hook_statement = f"\n  const {{ t }} = useTranslation({ns_str});\n"
                insert_idx = match.end()
                content = content[:insert_idx] + hook_statement + content[insert_idx:]

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

def main():
    translations = load_translations()
    print(f"Loaded {len(translations)} translation strings.")
    
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith('.tsx'):
                filepath = os.path.join(root, file)
                process_file(filepath, translations)

if __name__ == '__main__':
    main()
