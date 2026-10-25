import unittest,math
from dataclasses import replace
from track_audit import Observation as O,audit,fixture
class AuditTests(unittest.TestCase):
 def run_audit(self,rows,**kw):return audit(rows,selected_track='7',**kw)
 def test_known_path(self):
  r=self.run_audit([O(0,0,0,'7','A'),O(.1,.3,.4,'7','A')]);self.assertAlmostEqual(r['observed_distance_m'],.5);self.assertAlmostEqual(r['peak_observed_speed_m_s'],5)
 def test_fixture_never_extrapolates(self):
  r=self.run_audit(fixture());self.assertEqual(r['accepted_intervals'],5);self.assertAlmostEqual(r['observed_distance_m'],2.5);self.assertAlmostEqual(r['time_coverage'],1/3);self.assertIsNone(r['match_distance_estimate']);self.assertGreater(r['naive_distance_m'],100)
 def test_id_switch_breaks_both_intervals(self):
  rows=[O(0,0,0,'7','A'),O(.1,.1,0,'8','A'),O(.2,.2,0,'7','A')];r=self.run_audit(rows);self.assertEqual(r['accepted_intervals'],0);self.assertTrue(all('identity_unresolved' in x['reasons'] for x in r['intervals']))
 def test_gap_not_interpolated(self):
  r=self.run_audit([O(0,0,0,'7','A'),O(1,1,0,'7','A')]);self.assertEqual(r['observed_distance_m'],0);self.assertIn('observation_gap',r['intervals'][0]['reasons'])
 def test_camera_cut(self):
  r=self.run_audit([O(0,1,1,'7','A'),O(.1,1,1,'7','B')]);self.assertEqual(r['accepted_intervals'],0)
 def test_calibration_required(self):
  r=self.run_audit([O(0,1,1,'7','A',False),O(.1,1,1,'7','A')]);self.assertIn('calibration_unverified',r['intervals'][0]['reasons'])
 def test_low_confidence_preserves_rejection(self):
  r=self.run_audit([O(0,1,1,'7','A',confidence=.2),O(.1,1,1,'7','A')]);self.assertIn('low_confidence',r['intervals'][0]['reasons'])
 def test_outside_pitch(self):
  r=self.run_audit([O(0,-1,1,'7','A'),O(.1,-1,1,'7','A')]);self.assertIn('outside_pitch',r['intervals'][0]['reasons'])
 def test_teleport_is_reviewed(self):
  r=self.run_audit([O(0,0,0,'7','A'),O(.1,30,0,'7','A')]);self.assertIn('speed_requires_review',r['intervals'][0]['reasons']);self.assertIsNone(r['peak_observed_speed_m_s'])
 def test_invalid_timestamps(self):
  for t in [0,-1]:
   with self.assertRaises(ValueError):self.run_audit([O(0,0,0,'7','A'),O(t,0,0,'7','A')])
 def test_nonfinite_and_thresholds(self):
  for v in [math.nan,math.inf]:
   with self.assertRaises(ValueError):self.run_audit([O(0,v,0,'7','A')])
  with self.assertRaises(ValueError):self.run_audit([],max_gap=-1)
 def test_empty_and_stationary(self):
  self.assertIsNone(self.run_audit([])['time_coverage']);r=self.run_audit([O(0,1,1,'7','A'),O(.1,1,1,'7','A')]);self.assertEqual(r['observed_distance_m'],0);self.assertEqual(r['time_coverage'],1)
if __name__=='__main__':unittest.main()
