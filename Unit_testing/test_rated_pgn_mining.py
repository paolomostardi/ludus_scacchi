"""Clock, split, shard and exact-overlap regression checks for PGN mining."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

from Backend.data_pipeline.audit_position_overlap import audit, chunk_paths
from Backend.data_pipeline.download_lichess_prefix import download
from Backend.data_pipeline.mine_rated_pgn import event_class, mine


def game(site, event, white_elo, black_elo, time_control, moves):
    headers = [f'[Event "{event}"]', f'[Site "https://lichess.org/{site}"]',
               '[Result "*"]', f'[WhiteElo "{white_elo}"]',
               f'[BlackElo "{black_elo}"]', f'[TimeControl "{time_control}"]']
    return "\n".join(headers) + "\n\n" + moves + " *\n\n"


class RatedPgnMiningTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_before_move_clock_rating_and_bullet_filter(self):
        self.assertEqual(event_class("Rated UltraBullet tournament"), "ultrabullet")
        self.assertIsNone(event_class("Unknown event"))
        text = game("Abcdef12", "Rated Blitz game", 1500, 1700, "60+0",
                    "1. e4 { [%clk 0:00:12] } e5 { [%clk 0:00:50] } "
                    "2. Nf3 { [%clk 0:00:10] }")
        text += game("Abcdef13", "Rated Bullet game", 1500, 1500, "60+0",
                     "1. d4 { [%clk 0:00:40] }")
        text += game("Abcdef14", "Rated Rapid game", 1500, 1500, "15+0",
                     "1. d4 { [%clk 0:00:14] } d5 { [%clk 0:00:13] } "
                     "2. c4 { [%clk 0:00:12] } e6 { [%clk 0:00:11] }")
        source = self.root / "sample.pgn"
        source.write_text(text, encoding="utf-8")
        result = mine(source, self.root / "mined", shard_rows=2)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["counts"]["games_bullet"], 1)
        self.assertEqual(result["counts"]["moves_rating_match"], 6)
        self.assertEqual(result["counts"]["moves_low_clock"], 3)
        self.assertEqual(sum(s["rows"] for s in result["splits"].values()), 3)
        self.assertEqual(result["source_sha256"], __import__("hashlib").sha256(source.read_bytes()).hexdigest())
        for split in ("training", "evaluation"):
            for x_path in chunk_paths(self.root / "mined" / split):
                x = np.load(x_path)
                y = np.load(x_path.with_name(x_path.stem + "_y.npy"))
                keys = np.load(x_path.with_name(x_path.stem + "_game_keys.npy"))
                self.assertEqual(x.shape[1:], (15, 8, 8))
                self.assertEqual(y.shape, (len(x), 2, 8, 8))
                self.assertEqual(len(keys), len(x))

    def test_bounded_download_refuses_full_response(self):
        class FullResponse:
            status = 200
            headers = {}

            def __enter__(self): return self
            def __exit__(self, *_): pass

        output = self.root / "prefix.zst"
        with patch("Backend.data_pipeline.download_lichess_prefix.urllib.request.urlopen",
                   return_value=FullResponse()):
            with self.assertRaisesRegex(RuntimeError, "bounded HTTP Range"):
                download("2017-04", output, 1024)
        self.assertFalse(output.exists())

    def test_partial_source_drops_last_game(self):
        source = self.root / "prefix.pgn"
        source.write_text(game("Abcdef12", "Rated Blitz", 1500, 1500, "60+0",
                               "1. e4 { [%clk 0:00:50] }")
                          + game("Abcdef13", "Rated Blitz", 1500, 1500, "60+0",
                                 "1. d4 { [%clk 0:00:50] }"), encoding="utf-8")
        result = mine(source, self.root / "partial", partial=True)
        self.assertEqual(result["counts"]["games_scanned"], 1)
        self.assertFalse(result["source_complete"])

    def test_promotion_piece_is_preserved(self):
        source = self.root / "promotion.pgn"
        headers = ('[Event "Rated Rapid"]\n[Site "https://lichess.org/Abcdef15"]\n'
                   '[Result "*"]\n[WhiteElo "1500"]\n[BlackElo "1600"]\n'
                   '[TimeControl "60+0"]\n[SetUp "1"]\n'
                   '[FEN "8/6P1/5k2/8/6K1/8/8/8 w - - 0 1"]\n\n')
        source.write_text(headers + '1. g8=Q { [%clk 0:00:50] } *\n', encoding="utf-8")
        result = mine(source, self.root / "promotion")
        split = next(name for name, item in result["splits"].items() if item["rows"])
        promotion = np.load(self.root / "promotion" / split / "chunk_0_promotion.npy")
        self.assertEqual(promotion.tolist(), [5])

    def test_overlap_filter_removes_shared_positions_and_games(self):
        source = self.root / "sample.pgn"
        source.write_text(
            game("Abcdef12", "Rated Blitz", 1500, 1500, "60+0",
                 "1. e4 { [%clk 0:00:50] } e5 { [%clk 0:00:50] }")
            + game("Abcdef13", "Rated Blitz", 1500, 1500, "60+0",
                   "1. e4 { [%clk 0:00:50] } c5 { [%clk 0:00:50] }"), encoding="utf-8")
        result = mine(source, self.root / "mined", eval_percent=50, shard_rows=2)
        # The exact split of these two IDs is deterministic but need not place
        # one game on each side for this test, so construct a known eval row.
        train = self.root / "mined" / "training"
        eval_dir = self.root / "mined" / "evaluation"
        train_x = chunk_paths(train)
        if not train_x:
            self.skipTest("Fixture hashes assigned both games to evaluation")
        x0 = np.load(train_x[0])[0]
        y0 = np.load(train_x[0].with_name("chunk_0_y.npy"))[0]
        key0 = np.load(train_x[0].with_name("chunk_0_game_keys.npy"))[0]
        other = x0.copy()
        other[0, 6, 0] = 1
        other[0, 6, 4] = 0
        np.save(eval_dir / "chunk_99.npy", np.stack((x0, other)))
        np.save(eval_dir / "chunk_99_y.npy", np.stack((y0, y0)))
        np.save(eval_dir / "chunk_99_game_keys.npy", np.asarray((b"other-game", key0), dtype="S32"))
        np.save(eval_dir / "chunk_99_ply.npy", np.asarray((1, 2), dtype=np.uint16))
        np.save(eval_dir / "chunk_99_promotion.npy", np.asarray((0, 0), dtype=np.uint8))
        counts = audit(train_x, [eval_dir / "chunk_99.npy"], self.root / "index.sqlite",
                       cleaned_dir=self.root / "clean")
        self.assertEqual(counts["evaluation_overlap_rows"], 1)
        self.assertEqual(counts["evaluation_game_overlap_rows"], 1)
        self.assertEqual(counts["evaluation_kept_rows"], 0)
        self.assertEqual(json.loads((self.root / "clean" / "overlap_report.json").read_text())["status"], "complete")


if __name__ == "__main__":
    unittest.main()
