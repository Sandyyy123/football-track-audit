"""Audit already-calibrated player observations. No detector or calibration accuracy claimed."""
from __future__ import annotations
import argparse
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass(frozen=True)
class Observation:
    t: float
    x: float
    y: float
    track: str
    shot: str
    calibrated: bool = True
    confidence: float = 1.0

def audit(observations, *, selected_track, max_gap=0.2, confidence_min=0.8,
          speed_limit=12.0, pitch=(105.0, 68.0)):
    """Count only defensible adjacent intervals; never bridge missing/rejected observations.

    Coordinates must already be in metres in one common pitch frame. `speed_limit`
    is an illustrative review threshold, not a universal physiological limit.
    Rejection does not establish a tracking error; it marks uncertainty.
    """
    rows=list(observations)
    params=[max_gap,speed_limit,*pitch,confidence_min]
    if not all(math.isfinite(v) for v in params) or min(max_gap,speed_limit,*pitch)<=0 or not 0<=confidence_min<=1:
        raise ValueError('invalid audit parameters')
    for i,r in enumerate(rows):
        if not all(math.isfinite(v) for v in [r.t,r.x,r.y,r.confidence]):
            raise ValueError('nonfinite observation')
        if not 0<=r.confidence<=1 or not r.track or not r.shot:
            raise ValueError('invalid observation')
        if i and r.t<=rows[i-1].t:
            raise ValueError('timestamps must strictly increase')
    intervals=[]
    for a,b in zip(rows,rows[1:]):
        dt=b.t-a.t;distance=math.hypot(b.x-a.x,b.y-a.y);speed=distance/dt
        reasons=[]
        if a.track!=selected_track or b.track!=selected_track:reasons.append('identity_unresolved')
        if a.shot!=b.shot:reasons.append('camera_cut')
        if not a.calibrated or not b.calibrated:reasons.append('calibration_unverified')
        if min(a.confidence,b.confidence)<confidence_min:reasons.append('low_confidence')
        if dt>max_gap+1e-9:reasons.append('observation_gap')
        if any(not(0<=r.x<=pitch[0] and 0<=r.y<=pitch[1]) for r in [a,b]):reasons.append('outside_pitch')
        if speed>speed_limit:reasons.append('speed_requires_review')
        intervals.append({'start_s':a.t,'end_s':b.t,'duration_s':dt,'distance_m':distance,
                          'speed_m_s':speed,'accepted':not reasons,'reasons':reasons})
    accepted=[x for x in intervals if x['accepted']]
    span=rows[-1].t-rows[0].t if len(rows)>1 else 0
    observed=sum(x['duration_s'] for x in accepted)
    return {'input_observations':len(rows),'accepted_intervals':len(accepted),
            'rejected_intervals':len(intervals)-len(accepted),'observed_duration_s':observed,
            'span_s':span,'time_coverage':observed/span if span else None,
            'observed_distance_m':sum(x['distance_m'] for x in accepted),
            'naive_distance_m':sum(x['distance_m'] for x in intervals),
            'peak_observed_speed_m_s':max((x['speed_m_s'] for x in accepted),default=None),
            'match_distance_estimate':None,'intervals':intervals,
            'limitation':'Observed valid intervals only; no extrapolation across missing play. No detector, calibration or real-match accuracy benchmark.'}

def fixture():
    return [Observation(0,10,20,'7','A'),Observation(.1,10.3,20.4,'7','A'),
            Observation(.2,10.6,20.8,'7','A'),Observation(.3,45,30,'8','A'),
            Observation(.4,11.2,21.6,'7','A'),Observation(.5,11.5,22,'7','A'),
            Observation(1,13,24,'7','A'),Observation(1.1,13.3,24.4,'7','A'),
            Observation(1.2,60,35,'7','B'),Observation(1.3,60.3,35.4,'7','B'),
            Observation(1.4,60.6,35.8,'7','B',False),Observation(1.5,61,36,'7','B')]

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('example.json'));p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    result={'synthetic':True,'selected_track':'7','observations':[asdict(x) for x in fixture()],'audit':audit(fixture(),selected_track='7')}
    if a.dry_run:print(json.dumps(result,indent=2))
    else:a.output.write_text(json.dumps(result,indent=2)+'\n');print(a.output)
