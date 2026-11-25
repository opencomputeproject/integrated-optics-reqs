# Optical Connectivity Options

Draft contribution from the Open Compute Project (OCP) Future Technologies Initiative Short Reach Optical Interconnect (SROI) workstream. The source draft is version 0.5.5, dated October 22, 2026, by Jeff Hutchins, Ranovus.

- [Read the contribution on GitHub](contribution.md)
- [Open the browser preview locally](docs/index.html) by opening the downloaded file in a browser.
- [Visit the SROI workstream](https://www.opencompute.org/projects/future-technologies-initiative/short-reach-optical-interconnect/)

## Editing the draft

The content lives in plain text. Edit [the contribution text](data/contribution.json) for prose, attribution, and captions. Edit [the comparison data](data/optical-options.json) for the families, options, comparison values, and terminology notes. The Markdown draft and the browser table are generated from these same inputs. For placement figure changes, update the picker in the browser template and the crop coordinates in the interactions file. Edit the [browser template](src/index.html), [styles](docs/styles.css), or [interactions](docs/explorer.js) to change the presentation. The [original SVG](docs/assets/naming-drawings.svg) remains editable in a vector editor or as text.

Run the following from the repository root to regenerate and check both views. It uses Python 3 and its standard library.

```sh
python3 scripts/build.py
python3 scripts/build.py --check
```

Review the JSON and generated diffs together in pull requests. The preview works locally without a network connection. The `#comparison` anchor links directly to the interactive table. A fragment such as `#figure=npo-hdi` opens a specific placement illustration.

## Source mapping

| Supplied file | Content used |
| --- | --- |
| SROI Optical Naming 0.5.5.docx | Title, version, author, footer date, introduction, table and figure captions, license text, and OCP Foundation text. The full side/top-view figure and header logo are extracted from Word. |
| 26-33.4 Optical Naming Table.xlsx | The `26-33.4 Table` worksheet, `C4:K14` and footnotes in `G16:K16`. The exported table normalizes line wrapping and presents the footnote markers as links. |
| 26-41.5 Naming Drawings.svg | Original vector side drawings. The browser preview crops a view of NPO-HDI. The Word figure remains the source of the complete side/top-view pairs and their legend. |

The workbook’s earlier tabs and unlabeled numeric blocks in rows 20–34 are outside the displayed comparison. The numbers are consistent with palette work: `C20:C22` is RGB 218/233/248, the exact fill used for `E8`. The workbook does not label the number blocks.

The matrix uses colors from the [OCP brand guidelines](https://www.opencompute.org/about/brand-guidelines/). The draft’s Creative Commons Attribution-ShareAlike 4.0 notice and original license wording appear in the [contribution](contribution.md#license).

## Publishing on GitHub Pages

Once the workstream is ready to share the draft, push the files to the intended branch. In the repository's **Settings → Pages**, select **Deploy from a branch** and choose the approved branch and **/docs** folder. The committed browser files are ready to serve. [GitHub Pages publishing settings](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

After GitHub reports the deployment URL, link to the comparison or a specific illustration from the OCP workstream page. A printable draft can link to the same comparison as a companion to the document.
