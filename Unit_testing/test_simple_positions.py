import json
import tempfile
import unittest
from pathlib import Path

import chess
import numpy as np

from Backend.data_pipeline import from_PGN_generate_bitboards as gen
from Backend.model_evaluation.simple_positions import (
    load_catalog, catalog_identity, expected_indices, normalize_case, prepare, score_predictions,
)
from Backend.model_evaluation.position_tool import save_case
from Backend.model_evaluation.create_dataset_for_simple_positions import main as export


class SimplePositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog()

    def test_square_labels_match_training_and_all_piece_planes(self):
        for square in chess.SQUARES:
            index = gen.chess_square_to_source_index(square)
            self.assertEqual(gen.source_index_to_chess_square(index), square)
            source, _ = gen.from_chess_move_create_bitboard(chess.Move(square, square ^ 8))
            self.assertEqual(int(source.argmax()), index)
            board = chess.Board(None)
            board.set_piece_at(square, chess.Piece(chess.KNIGHT, chess.WHITE))
            encoded = gen.from_chess_board_create_bit_boards(board)
            self.assertEqual(int(encoded[1].argmax()), index)
            self.assertEqual(gen.transform_index(square), index)
        self.assertEqual([gen.chess_square_to_source_index(chess.parse_square(s)) for s in ('a8','h8','a1','h1')], [0,7,56,63])

    def test_legacy_eight_labels_are_consistently_file_reversed(self):
        directory = Path(__file__).resolve().parents[1]/'Backend/model_evaluation'
        audit = json.loads((directory/'legacy_simple_positions_audit.json').read_text(encoding='utf-8'))
        repaired = load_catalog(directory/'legacy_simple_positions_repaired.json')
        self.assertEqual(len(audit),8)
        for old, case in zip(audit,repaired['cases']):
            move = chess.Move.from_uci(case['moves'][0])
            self.assertEqual(old['target_square_number'] ^ 7,move.from_square)
            self.assertIn(move,chess.Board(case['fen']).legal_moves)

    def test_entire_catalog_is_legal_and_solutions_have_the_claimed_property(self):
        self.assertGreaterEqual(len(self.catalog['cases']), 150)
        self.assertEqual(len({chess.Board(c['fen']).turn for c in self.catalog['cases']}), 2)
        for case in self.catalog['cases']:
            board = chess.Board(case['fen'])
            self.assertTrue(board.is_valid(), case['id'])
            for uci in case['moves']:
                move = chess.Move.from_uci(uci)
                self.assertIn(move, board.legal_moves)
                after = board.copy(); after.push(move)
                if case['category'] == 'mate_in_1': self.assertTrue(after.is_checkmate())
                elif case['category'] == 'free_queen':
                    self.assertEqual(board.piece_at(move.to_square).piece_type, chess.QUEEN)
                    self.assertFalse(after.is_attacked_by(after.turn, move.to_square))

    def test_multiple_mating_sources_are_all_accepted_and_orientation_diagnosed(self):
        cases = [c for c in self.catalog['cases'] if len(expected_indices(c)) > 1]
        self.assertTrue(cases)
        selected = {'schema_version': 2, 'version': 'fixture', 'cases': cases[:1]}
        x, y = prepare(selected)
        self.assertEqual(x.shape, (1,15,8,8))
        self.assertEqual(y.sum(), 1)
        p = np.zeros((1,64)); p[0,expected_indices(cases[0])[-1]] = 1
        self.assertEqual(score_predictions(selected,p)['metrics']['accuracy'], 1)
        singleton = next(c for c in self.catalog['cases'] if len(expected_indices(c)) == 1)
        selected['cases'] = [singleton]
        p = np.zeros((1,64)); p[0,expected_indices(singleton)[0] ^ 7] = 1
        report = score_predictions(selected,p)
        self.assertEqual(report['metrics']['accuracy'], 0)
        self.assertEqual(report['orientation_top1_accuracy']['flip_files'], 1)

    def test_promotion_choices_for_both_colors_and_missing_suffix(self):
        white = chess.Board('8/6P1/5k2/8/6K1/8/8/8 w - - 0 1')
        for board, uci in ((white, 'g7g8'), (white.mirror(), 'g2g1')):
            case = {'id':'promotion', 'fen':board.fen(), 'category':'other', 'rationale':'Promotion check.'}
            with self.assertRaisesRegex(ValueError, 'Choose a promotion piece'):
                normalize_case({**case, 'moves':[uci]})
            for piece in 'qrbn':
                result = normalize_case({**case, 'moves':[uci+piece]})
                self.assertEqual(result['moves'], [uci+piece])
            san = board.san(chess.Move.from_uci(uci+'n'))
            self.assertEqual(normalize_case({**case,'moves':[san]})['moves'], [uci+'n'])

    def test_bad_probabilities_and_wrong_labels_rejected(self):
        with self.assertRaises(ValueError): score_predictions(self.catalog, np.ones((len(self.catalog['cases']),64)))
        case = dict(self.catalog['cases'][0])
        case['moves'] = ['a6a7']
        with self.assertRaises(ValueError): normalize_case(case)

    def test_authoring_export_duplicates_and_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'catalog.json'
            path.write_text(json.dumps(self.catalog))
            with self.assertRaises(ValueError): save_case(path, self.catalog['cases'][0])
            before = catalog_identity(self.catalog)['sha256']
            fresh = normalize_case({'id':'new-case', 'category':'mate_in_1',
                'fen':'k7/6R1/7R/8/8/8/3K4/8 w - - 0 1', 'moves':['Rh8#'], 'rationale':'Immediate ladder mate.'})
            save_case(path,fresh)
            self.assertNotEqual(before, catalog_identity(load_catalog(path))['sha256'])
            target = Path(directory)/'positions.csv'
            export(target)
            self.assertIn('TargetSquare',target.read_text())

    def test_notebook_writes_readable_per_position_report(self):
        from Backend.training_pipeline.validation import validate_arrays, validate_metrics
        root = Path(__file__).resolve().parents[1]
        notebook = json.loads((root/'Backend/kaggle/notebooks/evaluate-model.ipynb').read_text(encoding='utf-8'))
        source = next(''.join(c['source']) for c in notebook['cells'] if 'simple_report_path.write_text' in ''.join(c.get('source',[])))
        loop = source[source.index('for test_name, dataset_x, dataset_y in evaluation_datasets:'):source.index('report_path = Path("/kaggle/working/evaluation_report.json")')]
        catalog = {**self.catalog,'cases':self.catalog['cases'][:2]}
        x,y = prepare(catalog)
        class Model:
            def predict(self,*args,**kwargs): return y
        with tempfile.TemporaryDirectory() as directory:
            loop = loop.replace('/kaggle/working/simple_positions_report.json',str(Path(directory)/'report.json').replace('\\','/'))
            env={'simple_catalog':catalog,'evaluation_datasets':[('simple_v2',x,y)],'model':Model(),
                 'score_predictions':score_predictions,'validate_arrays':validate_arrays,'validate_metrics':validate_metrics,
                 'evaluation_results':{'datasets':{}},'Path':Path,'json':json}
            exec(loop,env)
            report=json.loads((Path(directory)/'report.json').read_text())
            self.assertEqual(report['metrics']['accuracy'],1)
            self.assertEqual(len(report['positions']),2)


if __name__ == '__main__': unittest.main()
