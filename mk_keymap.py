#!/usr/bin/env python3

import re
import requests
import sys
from pathlib import Path


URL = "https://github.com/qmk/qmk_firmware/file-list/master/quantum/keymap_extras"
key_regexp = re.compile(
    r"^#define\s*(?P<slug>..)_(?P<new_keycode>\S*)\s*(?P<kc_keycode>\S*)(\s*//\s*(?P<comment>.*))?"
)
sep_regexp = re.compile(r"^/(/|\*)\s*(?P<comment>.*)")


def list_qmk_keymap():
    r = requests.get(URL)
    return set(re.findall(r"keymap_[^\./]*\.h", r.text))


def generate(keymap):
    print(f"using reference: {keymap}")
    r = requests.get(
        f"https://raw.githubusercontent.com/qmk/qmk_firmware/master/quantum/keymap_extras/{keymap}"
    )
    slug = ""
    content = []
    seen = {}
    for line in r.text.split("\n"):
        key = re.search(key_regexp, line)
        sep = re.search(sep_regexp, line)
        if key:
            slug = key["slug"]
            kc = key["kc_keycode"]
            for i in range(10):
                kc = kc.replace(f"KC_{i}", f"KC.N{i}")
            kc = kc.replace("KC_", "KC.")
            kc = kc.replace("S(", "KC.LSFT(")
            kc = kc.replace("ALGR(", "KC.RALT(")

            # expand self ref to previously defined keycode
            for m in re.finditer(slug + "_\w*", kc):
                try:
                    kc = kc.replace(m.group(), seen[m.group()])
                except KeyError:
                    pass

            new = key["new_keycode"]
            if new.isdigit():
                new = "N" + new

            s = f"        '{new}': {kc},"
            seen[slug + "_" + key["new_keycode"]] = kc

            try:
                s += f"  # {key['comment']}"
            except IndexError:
                pass
            content.append(s)

        elif sep and sep["comment"]:
            if "Copyright" in line or "clang" in line:
                continue
            s = f"        # {sep['comment']}"
            content.append(s)

    print(f"To stay coherent, use the slug {slug} in your keymap (in place of KC)")
    name = re.search(r"[^_]*_(.*)\.h", keymap).group(1).upper()
    print(
        f"default class name: {name}"
    )

    layout = """from kmk.keys import KC
from kmk.extensions.keymap_extras.base import KeyMapConverter


class {}(KeyMapConverter):
    # Generated mapping from:
    # https://github.com/qmk/qmk_firmware/blob/master/quantum/keymap_extras/{}
    # might need some tweaking...

    MAPPING = {{
{}
    }}
    """.format(
        name, keymap, "\n".join(content)
    )

    with open(keymap.replace(".h", ".py"), "w") as fp:
        fp.write(layout)


if __name__ == "__main__":
    lang = sys.argv[1] if len(sys.argv) == 2 else ""

    if not lang:
        print(
            "You should pass an argument with a search term (probably your language abreviation), and if necessary refine it to select only one keymap."
        )
        print(
            f"You can also consult {URL} to check the list and the files content first..."
        )
        sys.exit(1)

    choices = sorted(keymap for keymap in list_qmk_keymap() if lang in keymap)
    if not choices:
        print("Your search term is too restrictif. No keymap match it...")
        sys.exit(2)

    if lang + ".h" in choices:
        keymap = lang + ".h"
    elif "keymap_" + lang + ".h" in choices:
        keymap = "keymap_" + lang + ".h"
    elif len(choices) > 1:
        print("The following keymap match your given name:")
        print(choices),
        print("Please refine your search term.")
        sys.exit(0)
    else:
        keymap = choices[0]

    generate(keymap)
