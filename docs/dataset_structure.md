# Dataset Structure Documentation

## Current Structure

### Data Pipeline Flow
1. **PGN Download**: Games are downloaded from Lichess API and stored in `Backend/data/pgn_games/pgn_games_{rating}/`
2. **Bitboard Generation**: PGN files are converted to bitboards and stored in `Backend/data/bit_boards/bit_boards_{rating}/{username}/`
3. **User Tracking**: User information and game counts are tracked in `Backend/data/user_record.csv`

### Current File Structure
```
Backend/data/
├── pgn_games/
│   └── pgn_games_{rating}/
│       └── pgn_games_{username}.json
├── bit_boards/
│   └── bit_boards_{rating}/
│       └── {username}/
│           ├── x.npy          # Input bitboards (15, 8, 8)
│           ├── x2.npy         # Transformed input bitboards
│           ├── y.npy          # Output move bitboards (2, 8, 8)
│           ├── y2.npy         # Transformed output bitboards
│           └── white_bitboard.npy  # Boolean array for player color
└── user_record.csv            # User metadata and game counts
```

### Current Bitboard Format
- **x**: Shape (N, 15, 8, 8) - 15 channels (12 piece channels + 2 legal move channels + 1 turn channel)
- **y**: Shape (N, 2, 8, 8) - 2 channels (from_square, to_square)
- **x2**: Alternative transformed input format
- **y2**: Alternative transformed output format

## Proposed New Structure

### Requirements
1. Each dataset should have training and evaluation parts
2. Each dataset should have an associated JSON metadata file
3. No duplicate positions across datasets (using FEN as unique identifier)
4. FEN indexing for position deduplication

### New Directory Structure
```
Backend/data/
├── datasets/
│   ├── dataset_v1/
│   │   ├── train/
│   │   │   ├── x.npy
│   │   │   ├── x2.npy
│   │   │   ├── y.npy
│   │   │   ├── y2.npy
│   │   │   └── fen_index.json  # FEN to sample index mapping
│   │   ├── eval/
│   │   │   ├── x.npy
│   │   │   ├── x2.npy
│   │   │   ├── y.npy
│   │   │   ├── y2.npy
│   │   │   └── fen_index.json
│   │   └── metadata.json
│   ├── dataset_v2/
│   │   └── [same structure]
│   └── global_fen_registry.json  # Registry of all FENs across all datasets
├── pgn_games/  # [unchanged]
└── user_record.csv  # [unchanged]
```

### Metadata JSON Structure
```json
{
  "dataset_name": "dataset_v1",
  "version": "1.0",
  "created_at": "2026-05-15T22:41:00Z",
  "rating_range": {
    "min": 1650,
    "max": 1750,
    "target": 1700
  },
  "split": {
    "train_size": 100000,
    "eval_size": 10000,
    "total_size": 110000
  },
  "sources": [
    {
      "username": "player1",
      "games_contributed": 5000,
      "rating": 1720
    }
  ],
  "bitboard_format": {
    "x_shape": [15, 8, 8],
    "y_shape": [2, 8, 8],
    "dtype": "bool"
  },
  "fen_deduplication": {
    "total_unique_positions": 95000,
    "duplicates_removed": 15000
  }
}
```

### FEN Index Structure
```json
{
  "fen_to_index": {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1": 0,
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": 1
  },
  "index_to_fen": {
    "0": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "1": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
  }
}
```

### Global FEN Registry Structure
```json
{
  "datasets": {
    "dataset_v1": {
      "fens": ["fen1", "fen2", ...],
      "count": 95000
    },
    "dataset_v2": {
      "fens": ["fen3", "fen4", ...],
      "count": 80000
    }
  },
  "last_updated": "2026-05-15T22:41:00Z"
}
```

## Implementation Plan

### 1. FEN Extraction
- Modify `from_chess_board_create_bit_boards` to also extract FEN strings
- Store FEN alongside bitboard during generation

### 2. Deduplication Process
- Before creating a new dataset:
  1. Extract all FENs from candidate positions
  2. Check against `global_fen_registry.json`
  3. Filter out positions already present in other datasets
  4. Add remaining FENs to registry

### 3. Train/Eval Split
- After deduplication, split positions into train/eval
- Common split ratios: 90/10 or 80/20
- Ensure stratified sampling by player rating if needed

### 4. Metadata Generation
- Generate `metadata.json` with dataset information
- Track sources, sizes, and deduplication statistics

### 5. File Organization
- Save train and eval splits separately
- Include FEN index files for both splits
- Update global registry after dataset creation

## Key Benefits

1. **No Data Leakage**: FEN deduplication ensures positions don't appear in multiple datasets
2. **Reproducibility**: Metadata files track dataset provenance
3. **Flexibility**: Easy to create multiple datasets for different experiments
4. **Transparency**: Clear tracking of data sources and transformations
5. **Evaluation Integrity**: Separate eval sets prevent overfitting to specific positions

## Migration Path

### Phase 1: Add FEN Extraction
- Modify existing bitboard generation to extract FENs
- Save FEN arrays alongside bitboards

### Phase 2: Create Registry System
- Initialize `global_fen_registry.json`
- Implement FEN checking logic

### Phase 3: Reorganize Existing Data
- Create `datasets/` directory structure
- Migrate existing bitboards to new format
- Generate metadata for existing data

### Phase 4: Update Pipeline
- Modify `PipelineManager` to use new structure
- Implement deduplication in data addition process
- Add train/eval splitting logic
