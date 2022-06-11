# KMK and keymap\_extras
Currently, [KMK](https://github.com/KMKfw/kmk_firmware) do not have a proper way to easily support international keymap. I
guess I'm the first kmk user who happened to not use a qwerty layout. This script
aim to give a automatic way to build your 'translation'.

## Why it is needed ?
Defining your keymap when using for instance an azerty layout (in your OS
configuration) still look the same

```python
layer = [KC.Q, KC.W, KC.E, KC.R, KC.T, KC.Y]
```
but will output 'azerty' when typing all of them. The need to use different
KC that the one that will be outputed is quickly annoying and will need you to make
way too much attempt to get this right.

## QMK's answer
In QMK, the answer was to add new definition with helpfull label that will fallback
to the correct one. Those translation mapping are still annoying to make but are
standardized, made only once and share with the community. You can then have a keymap
that looks like what you will actually type:
```python
layer = [FR.A, FR.Z, FR.E, FR.R, FR.T, FR.Y]
```

## How to do it in KMK
I made a PR to KMK that give us the base class `KeyMapConverter` to store those mapping.
The need being identical to what is done in KMK, a made a script to convert automatically keymaps
from [QMK repo](https://github.com/qmk/qmk_firmware/tree/master/quantum/keymap_extras)
into KMK's python equivalent.

The few existing ones [are here in KMK](https://github.com/KMKfw/kmk_firmware/tree/master/kmk/extensions/keymap_extras)


## Disclaimer
As the currently sole user of such keymap, there is no real consensus on the best way to handle
those in KMK. While the maintainer agreed to merge my suggestion, this might evolve (even
the way the main `KC` is built/populated is currently still being challenged).

## Generating a missing layout
To make your own keymap, for your language/layout, run the script with your language/layout name as an argument. The script will search QMK files for a match.
```
➜ kmk_keymap_extras ./mk_keymap.py
You should pass an argument with a search term (probably your language abreviation), and if necessary refine it to select only one keymap.
You can also consult https://github.com/qmk/qmk_firmware/file-list/master/quantum/keymap_extras to check the list and the files content first...
```

```
➜ kmk_keymap_extras ./mk_keymap.py fr
The following keymap match your given name:
['keymap_dvorak_fr.h', 'keymap_french.h', 'keymap_french_afnor.h', 'keymap_french_mac_iso.h', 'keymap_swiss_fr.h']
Please refine your search term.
```

```
➜ kmk_keymap_extras ./mk_keymap.py french_afnor
using reference: keymap_french_afnor.h
To stay coherent, use the slug FR in your keymap (in place of KC)
default class name: FRENCH_AFNOR
```

Warning: The generated layout **need to be tested** and might need to be refined but that should save you quite some work.
Consider pushing your keymap to KMK in /kmk/extensions/keympa\_extras so that:
- we get more example, users, testers
- your keymap will be updated if this mechanisme (or the KC generation) change


Reference: See [KMK international doc](https://github.com/KMKfw/kmk_firmware/blob/master/docs/international.md)
