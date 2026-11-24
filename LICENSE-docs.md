# Licence for documents and data

The code (`src/`, `scripts/`, `tests/`) is under the MIT licence in `LICENSE`.

Everything else written for this project is under the
[Creative Commons Attribution 4.0 International licence (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/):
- the documents (`README.md`, `PLAN.md`, `LOG.md`, `CLAUDE.md`, `docs/`, `reports/`,
  `research_notes/`);
- the stimulus manifests and generated images;
- the local models' per-trial results in `runs/`.

Not covered by either licence:
- **Human results from the source papers.** The human effect sizes quoted in `docs/` and
  `reports/` come from the cited publications. Cite those papers when you use them.
- **Short quotations from published work** in `docs/`, `reports/` and `research_notes/`
  remain their authors'.
- **Replies from models served through NVIDIA's free API.** They are not published here:
  NVIDIA's API Trial Terms of Service (section 4.2) do not allow its generated content to
  be redistributed. The reports give aggregate statistics only.
- **The open-weight models themselves.** They are under their own licences, recorded with
  each pinned model in `src/aesx/models/registry.py`.
