import unittest
from nbloader import load_notebook

core = load_notebook()


class StatsTests(unittest.TestCase):
    def test_percentiles(self):
        for samples, expected in [
            ([1, 2, 3, 4, 5], [3.0, 4.6, 4.8, 4.96]),
            ([10, 20], [15.0, 19.0, 19.5, 19.9]),
            ([7], [7.0, 7.0, 7.0, 7.0]),
            ([3, 1, 4, 1, 5, 9, 2, 6], [3.5, 6.9, 7.95, 8.79]),
        ]:
            for q, value in zip([50, 90, 95, 99], expected):
                with self.subTest(samples=samples, q=q):
                    self.assertAlmostEqual(core.percentile(samples, q), value)

    def test_summaries(self):
        keys = ['n', 'failures', 'mean', 'median', 'p95', 'min', 'max', 'stdev']
        for samples, failures, expected in [
            ([12, 15, 11, 18, 14], 0, [5, 0, 14, 14, 17.4, 11, 18, 2.74]),
            ([20], 2, [1, 2, 20, 20, 20, 20, 20, 0]),
            ([], 3, [0, 3, None, None, None, None, None, None]),
            (list(range(1, 11)), 1, [10, 1, 5.5, 5.5, 9.55, 1, 10, 3.03]),
        ]:
            with self.subTest(samples=samples):
                result = core.summarize(samples, failures)
                rounded = {key: round(value, 2) if value is not None else None for key, value in result.items()}
                self.assertEqual(rounded, dict(zip(keys, expected)))

    def test_warmups_and_failures(self):
        calls = []
        def operation(name):
            calls.append(name)
            if len(calls) in (1, 4):
                raise TimeoutError('secret must not be displayed')
            return {'rcode': 3}
        ticks = iter(range(100))
        records = core.measure_trials(operation, 'example.com', 'test', 'repeat',
                                      n=5, warmup=2, clock=lambda: next(ticks))
        self.assertEqual(len(calls), 7)
        self.assertEqual(len([row for row in records if not row['warmup']]), 5)
        summary = core.summarize_records(records)
        self.assertEqual((summary['n'], summary['failures']), (4, 1))
        self.assertEqual(summary['n'] + summary['failures'], 5)
        self.assertEqual(records[0]['error_type'], 'TimeoutError')
        self.assertEqual(records[0]['message'], 'Request timed out')
        self.assertNotIn('secret', repr(records))

    def test_successful_loop(self):
        calls = []
        records = core.measure_trials(lambda name: calls.append(name), 'example.com',
                                      'test', 'repeat', n=5, warmup=2)
        self.assertEqual(len(calls), 7)
        self.assertEqual(core.summarize_records(records)['n'], 5)

    def test_unique_names(self):
        names = [core.scenario_name('example.com', 'unique') for _ in range(100)]
        self.assertEqual(len(set(names)), 100)
        for name in names:
            self.assertRegex(name, r'^[0-9a-f]{16}\.example\.com$')
            self.assertTrue(all(len(label) <= 63 for label in name.split('.')))
        self.assertEqual(core.scenario_name('example.com', 'repeat'), 'example.com')
        with self.assertRaises(ValueError):
            core.scenario_name('example.com', 'invalid')
