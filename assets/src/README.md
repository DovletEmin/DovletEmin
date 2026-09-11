# Header source

Regenerates `assets/header-dark.svg` and `assets/header-light.svg`.

Text is converted to vector outlines, so the banner renders identically
everywhere and depends on no installed fonts.

```bash
pip install fonttools
mkdir -p fonts && cd fonts
curl -sSLo Archivo-var.ttf          'https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth%2Cwght%5D.ttf'
curl -sSLo IBMPlexMono-Medium.ttf   'https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Medium.ttf'
cd .. && python banner.py          # writes out/header-{dark,light}.svg
```

Both faces are SIL Open Font License. Edit the strings in `banner.py`,
rerun, and copy `out/*.svg` over the files in `assets/`.
