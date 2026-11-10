# Simple-position benchmark audit and authoring

## Confirmed label failures in the original eight positions

The original labels were Python-chess square numbers interpreted as expected
**source** squares. Five identify empty squares; one identifies a blocked queen
with no legal move. All eight FEN boards themselves pass Python-chess validity.

**The old labels have a consistent file reversal.** Applying `square ^ 7`
changes a↔h, b↔g, c↔f, d↔e, while retaining ranks. All eight repaired sources
contain a moving-side piece with at least one legal move. This is strong evidence
that the dataset was authored in the horizontally reversed numbering convention
shown in the old helper comments. The current evaluation interpreted those
numbers using standard Python-chess squares.

The repaired sources are h6, c3, c3, h5, e6, d7, e8 and f5 in the original order.
`legacy_simple_positions_repaired.json` keeps exactly those eight boards with
explicit legal moves for a direct corrected-label check. Several opening choices
remain subjective, so this repaired set is separate from the new tactical suite.

| Old entry | Stored expected source | Finding | Resolution |
|---|---|---|---|
| Ladder mate | 40 = a6 | Empty; the unique mating move is h6h8 (Rh8#) | Corrected to h6 |
| Hanging queen | 21 = f3 | Empty; knight c3 can capture queen d5, but can be recaptured by Nf6 | Source is c3; quarantined because it falls outside the strict undefended-queen theme |
| French | 21 = f3 | File reversal gives pawn c3; c3d4 is legal, but this is not a uniquely forced tactical test | Excluded from new tactical suite |
| Scholar's Mate | 32 = a5 | Empty; h5f7 (Qxf7#) mates | Corrected to h5 |
| Exchange French | 43 = d6 | Empty; file reversal gives pawn e6 with legal e6d5 | Excluded from new tactical suite |
| Second hanging queen | 52 = e7 | Black pawn can move, but bishop d7 can capture the queen b5 | Corrected to d7 |
| Unsound sacrifice | 59 = d8 | Queen has no legal move; file reversal gives king e8 with legal e8f7 | Excluded from new tactical suite |
| Latvian Gambit | 34 = c5 | Empty; file reversal gives pawn f5 with legal f5e4 | Excluded from new tactical suite |

The machine-readable original values and legal-move audit are preserved in
`Backend/model_evaluation/legacy_simple_positions_audit.json`. The old reported
0/8 accuracy and high losses cannot establish tactical weakness. Changing the
labels requires reevaluation of the saved models; no retraining is required.
No actual predictions from the recent 4x64/6x64 saved models have been inspected
in this audit because those model files were not available locally.

## Orientation verification

The canonical encoder, move-label encoder and source-index conversion agree
for all 64 squares. Model indices run left to right, then top to bottom from
White's perspective: a8=0, h8=7, a1=56, h1=63. The Python-chess values are
different: a1=0 and a8=56. Authoring uses named moves so these number systems
cannot accidentally be interchanged.

The new per-position report includes raw predicted squares, expected squares,
top five probabilities, the best expected rank, and a diagnostic comparison
against file flips, rank flips and a 180-degree rotation. A transformation
scoring better is evidence to investigate, not permission to change orientation
without inspecting the actual training arrays. The orientation checks establish
current code consistency; they cannot certify historical arrays or model weights.

## Replacement catalog

`Backend/model_evaluation/simple_positions.json` contains **192 cases from 48
base positions**: 128 mate-in-one cases and 64 undefended-queen captures. Three
old tactical positions have corrected labels. Added motifs include ladder mate,
queen-and-king mate, back-rank mate, multiple mating pieces, and queen captures
by several piece types. Mirrored positions exercise both colors and files.
These are correlated variants, not 192 independent tactical ideas. Expand the
number of independently reviewed motifs before claiming broad chess strength.
There are 96 White-to-move and 96 Black-to-move cases. Twenty-eight cases have
only one legal source piece, making their source-only choice mechanically easy;
four cases accept more than one source. The suite is weighted toward rook mates,
so inspect category results rather than treating its aggregate as broad coverage.

Every saved case must have a legal board, an explicit legal move, a category and
an explanation. Mate cases are verified by playing the move and checking mate.
Free-queen cases capture a queen and leave the capturer on an unattacked square;
that local condition is not an engine proof of the best long-term move.
The French/opening cases are excluded from the new benchmark pending review.

When several pieces can satisfy a theme, **all qualifying source squares count
as correct**. Accuracy/top-3 use those accepted sets. Loss is negative log of
the total probability on accepted sources; it equals ordinary cross-entropy
when only one source is accepted. A separate legal-masked accuracy reveals
whether filtering impossible sources would help, while raw accuracy remains
the primary reported result.

This first CNN predicts a piece/source square, not the destination. Correctly
choosing a queen does not prove it would play the mating queen move. Report the
benchmark alongside general-game evaluation, and keep it outside training.
Repeatedly tuning against these examples also warrants a separate held-out
suite of new motifs. No automatic pass threshold has been invented.

## Add positions with a local board editor

From the project folder on the workstation (Python environment needs the
project's `chess`, NumPy and pandas dependencies):

```powershell
python -m Backend.model_evaluation.position_tool serve
```

Open http://127.0.0.1:8765 in a browser. Paste a FEN or enable **Edit pieces**
and place pieces using the palette. Set the side to move, click source and
destination (or enter a SAN move such as `Rh8#`), give the position an ID and
explanation, then validate and save. Illegal moves, theme mismatches and
duplicate positions are rejected. For automatic themes, all equivalent mating
or safe queen-capturing moves are included. Saved examples can be loaded for
review. Editing existing saved records is deliberately done in the JSON file;
the UI appends new positions. Changes to that JSON file are reviewable in Git.
Do not hand-edit the generated CSV.

CLI alternatives:

```bash
python -m Backend.model_evaluation.position_tool audit
python -m Backend.model_evaluation.position_tool add --id ladder-extra --fen "k7/6R1/7R/8/8/8/3K4/8 w - - 0 1" --moves Rh8# --category mate_in_1 --rationale "The second rook gives immediate ladder mate."
python -m Backend.model_evaluation.position_tool evaluate --model /path/to/source_resnet.keras --output /path/to/simple_positions_report.json
python -m Backend.model_evaluation.position_tool --catalog Backend/model_evaluation/legacy_simple_positions_repaired.json evaluate --model /path/to/source_resnet.keras --output /path/to/repaired_eight_report.json
```

Use an environment with Keras and a compatible backend for model evaluation,
such as Kaggle. The orchestration environment does not need a training stack.
The evaluate command reads the saved model and does no fitting or remote logging.

## Notebook integration and interpreting old results

The evaluation notebook exports `simple_positions_report.json` with every case,
category summaries and orientation diagnostics, alongside `evaluation_report.json`.
The new aggregate metric suffix is `simple_v2`; old `simple` scores remain
historical and must not be compared directly with this changed set/definition.
Catalog version, content hash and base-position count are included in reports
and MLflow tags, so added cases can be distinguished later. Download reports from Kaggle outputs or verify retrieval from the configured
MLflow artifact store. Deployment-specific storage diagnostics belong in private
operator notes.

The existing resume command preserves the original staged notebook and Git
revision. Resuming a completed old batch will not reevaluate it on this catalog.
Use the standalone evaluation command against the saved weights in a compatible
environment to obtain corrected scores without retraining.
