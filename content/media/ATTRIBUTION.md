# Pictogram attribution

The images in `img/` are **not** covered by the repository's MIT licence. They come from
[Global Symbols](https://globalsymbols.com) and are licensed **CC BY-SA 4.0**.

`MANIFEST.csv` records, for every file: the phrase it illustrates, the symbol label that was
matched, the symbol set it came from, its licence, and the URL it was downloaded from. It is
written one row at a time as files arrive, so a crash leaves the images and their provenance
in step.

Two obligations come with CC BY-SA 4.0, and both apply to anything built from this repo:

- **Attribution.** Credit Global Symbols and the symbol set, and keep a link to the source.
  `MANIFEST.csv` holds the per-file detail needed to do that.
- **Share-alike.** A modified pictogram must be released under CC BY-SA 4.0 as well. This
  does not reach the application code, which stays MIT.

`scripts/symbols.py` regenerates the set. It skips any file already present, so it can be
re-run after adding phrases without re-downloading the rest.
