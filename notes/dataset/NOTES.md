# Dataset download — decision log (2026-10-06)

Task: [[2026-09-30]] — "Analyze who replies to whom and whether their positions are opposed, complemented with an analysis of users' lifetime in the dataset (2026-10-19)".

Dataset: *A Decade of News Forum Interactions* (DerStandard.at, 2013–2022), doi:10.82201/RVQGUG, CC BY 4.0, BSC Dataverse, version 4 (2026-07-13). Paper: `papers/Fraxanet2025_derstandard-dataset.pdf`.

## Size (from Dataverse API, saved in `files_metadata.json`)

| Folder | Files | Size |
|---|---|---|
| embeddings | 259 | **507.8 GB** (split .tar.xz parts, 896-dim KaLM vectors) |
| votes_files | 120 (monthly) | 24.3 GB |
| comments_files | 120 (monthly) | 7.9 GB |
| articles_files | 10 (yearly) | 0.07 GB |
| users_files | 1 | 0.02 GB |
| summary_files | 13 | 0.02 GB (incl. `faction_users.tab`, `inconsistent_comment_metadata.tab`) |
| scripts + README + Codebook | 25 | <1 MB |
| **Total** | 548 | **540.1 GB** |

Disk C: 953 GB, **779 GB free** on 2026-10-06. Everything fits, but the full download would leave ~239 GB free. None of the files is restricted.

## Decisions

1. **Download everything except embeddings first (~32 GB).** The research question needs:
   - who replies to whom: `comments_files` (`Author_Id`, `Parent_Id`, `Origin_Parent_Id`, `Thread_Level`)
   - opposed positions: there is **no comment text** in the dataset. Stance has to come from signed votes (`votes_files`: who up- or downvotes whom), from `faction_users` (an annotated subset from FAULTANA, i.e. Fraxanet 2024), or from embeddings.
   - user lifetime: `users_files` (`First_Comment`, `Last_Comment`, `First_vote`, `Last_vote`)
   - `articles_files` for topics.
2. **Embeddings (508 GB) are on hold.** They are the only text signal, but they are 94% of the volume. The user decides whether to fetch them (same script plus `--include-embeddings`).
3. Tabular files are downloaded in **original TSV format** (`?format=original`), not the Dataverse-ingested `.tab`. The original is slightly smaller, and the listed MD5 refers to it.
4. Location: `data/derstandard/` at the repo root, outside the Obsidian vault so it doesn't get indexed.
5. `download.py` resumes partial files (HTTP Range), retries with backoff, and verifies size and MD5. Verified files are listed in `data/derstandard/.verified`. Rerunning it is safe and only fetches what's missing.

## Embeddings decision (after asking the user)
User: "Download the thing you deem necessary to run the tests and get a significant result."
→ **Not downloading embeddings.** (The AI's reasons were removed in the 2026-11-21 sweep because they had no source.)
- If needed later: `python download.py ../../../data/derstandard --include-embeddings`, or download a subset by editing `plan()`.


## Files here
- `files_metadata.json` — raw Dataverse file listing
- `README.md`, `Codebook.md` — dataset docs (also downloaded into data/)
- `download.py` — downloader; `download.log` — timestamped progress and retries

## Result (2026-10-06 19:42)
- **Done.** All 289 non-embedding files were downloaded to `data/derstandard/` and every one passed its size and MD5 check (list in `data/derstandard/.verified`). 19:31 → 19:42 (`download.log`).
- On disk: 28 GB (comments 6.8 GB / 120 files, votes 21 GB / 120 files, articles 58 MB, users 17 MB, summary 13 MB, scripts). C: now has 751 GB free.
- Formats confirmed: TSV with header, `NA` for missing. User and comment IDs are 16-hex hashes; timestamps are unix seconds. In `users_file`, `First_Comment = 0` means the user never commented (verified 2026-11-21: `BASE-VERIFICADA.md`, H11). IDs are 16 lowercase hex characters (H10).
- Note: votes rows can have `Author_Id = NA` (deleted author). Handle this when joining replies to votes.

## Next steps for the analysis
1. Reply edges: comments with `Is_Reply = 1`. Join `Parent_Id` → parent's `Author_Id` to get user A → user B edges (drop self-replies and NA authors).
2. **Facciones y negatividad, dos preguntas separadas** (planteamiento del 2026-11-19 [me]; ver WORKLOG):
   - *Quién responde a quién:* para cada respuesta A→B, ¿A y B son de la misma facción FAULTANA o de facciones distintas? La referencia con la que comparar está por decidir (pregunta abierta).
   - *Votos negativos al responder:* ¿quien responde a un comentario tiende a votarlo en contra, más que los comentarios parecidos que vota sin responder? Se compara cada votante consigo mismo (Mantel–Haenszel por votante × nivel de polémica) y no se formula entre facciones.

   > **Cambio de método (2026-11-21).** La versión original de este punto medía la oposición juntando los votos de A hacia B con las etiquetas de facción y comparando con parejas aleatorias del mismo artículo. Era un razonamiento circular: las facciones de FAULTANA se construyen con votos y son mayoritariamente negativas entre ellas, así que encontrar negatividad entre facciones reproduce la definición. El método nuevo lo evita usando las facciones solo para quién responde a quién y midiendo la negatividad con los votos, sin formularla entre facciones.
3. Lifetime: `Last_Comment - First_Comment` from `users_file`. Relate it to how often a user receives or makes antagonistic replies.
