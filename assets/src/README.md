# Sources for the generated artwork

Two generators, one shared typesetter. All text is converted to vector
outlines, so every piece renders identically everywhere and depends on no
installed fonts.

| Script | Produces | Notes |
|:--|:--|:--|
| `banner.py` | `header-dark.svg`, `header-light.svg` | Profile header. The lattice is an abstracted Turkmen gul that doubles as a network topology. |
| `flow.py` | `upload-path-dark.svg`, `upload-path-light.svg` | The Paylas upload path: 200 parts woven into a runner as they land in MinIO, the drop at part 77, the resume, a live S3 log and odometer counters. |

`carpet.svg` is not built here. The weave workflow rebuilds it every morning
with [Haly](https://github.com/DovletEmin/haly), the action this carpet grew
into: the contribution year as a Tekke rug, with wool pile and abrash done in
SVG filters.

## Running them

```bash
pip install fonttools
mkdir -p fonts && cd fonts
curl -sSLo Archivo-var.ttf        'https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth%2Cwght%5D.ttf'
curl -sSLo IBMPlexMono-Medium.ttf 'https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Medium.ttf'
cd ..

python banner.py                       # -> out/header-{dark,light}.svg
python flow.py                         # -> out/upload-path-{dark,light}.svg
```

Both typefaces are under the SIL Open Font License. Edit the strings in a
script, rerun it, and copy the result over the file in `assets/`.

## If `assets/carpet.svg` conflicts on a pull

The weave workflow commits a rebuilt carpet whenever it runs, so a push of
your own can land behind it. The file is generated, so never merge it by
hand. Take the remote copy and let the next run rebuild it:

```bash
git checkout origin/main -- assets/carpet.svg
git add assets/carpet.svg
```

Or run the workflow from the Actions tab once you have pushed. Pulling with
`git pull --rebase` before you start work avoids most of it.
