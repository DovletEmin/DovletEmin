# Sources for the generated artwork

Three generators, one shared typesetter. All text is converted to vector
outlines, so every piece renders identically everywhere and depends on no
installed fonts.

| Script | Produces | Notes |
|:--|:--|:--|
| `banner.py` | `header-dark.svg`, `header-light.svg` | Profile header. The lattice is an abstracted Turkmen gul that doubles as a network topology. |
| `carpet.py` | `carpet.svg` | The contribution year woven as a carpet. Drawn on a real knot lattice, so motifs step the way a weave forces them to. Rebuilt daily by the weave workflow. |
| `flow.py` | `upload-path.svg` | Animated walkthrough of the Paylas upload path. |

## Running them

```bash
pip install fonttools
mkdir -p fonts && cd fonts
curl -sSLo Archivo-var.ttf        'https://raw.githubusercontent.com/google/fonts/main/ofl/archivo/Archivo%5Bwdth%2Cwght%5D.ttf'
curl -sSLo IBMPlexMono-Medium.ttf 'https://raw.githubusercontent.com/google/fonts/main/ofl/ibmplexmono/IBMPlexMono-Medium.ttf'
cd ..

python banner.py                       # -> out/header-{dark,light}.svg
python flow.py                         # -> out/upload-path.svg
python carpet.py contrib.json out/carpet.svg
```

`carpet.py` needs a contribution calendar in `contrib.json`. The workflow
fetches it; to do it by hand:

```bash
gh api graphql -f query='{ user(login: "DovletEmin") { contributionsCollection {
  totalCommitContributions totalRepositoriesWithContributedCommits
  contributionCalendar { totalContributions
    weeks { contributionDays { date contributionCount } } } } } }' > contrib.json
```

Every random-looking variation in the carpet is seeded from knot coordinates,
so the same calendar always yields byte-identical output and the daily
workflow never commits noise.

Both typefaces are under the SIL Open Font License. Edit the strings in a
script, rerun it, and copy the result over the file in `assets/`.

## If `assets/carpet.svg` conflicts on a pull

The weave workflow commits a rebuilt carpet whenever it runs, so a push of
your own can land behind it. The file is generated, so never merge it by
hand. Rerun the generator and commit that:

```bash
python carpet.py contrib.json ../carpet.svg
git add ../carpet.svg && git commit
```

Pulling with `git pull --rebase` before you start work avoids most of it.
