# coding: utf-8
# Copyright 2021 D-Wave Systems Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


def make_reverse_anneal_schedule(s_target=0.0, hold_time=10.0, ramp_back_slope=0.2, ramp_up_time=0.0201,
                                 ramp_up_slope=None):
    """Build annealing waveform pattern for reverse anneal feature.

    Waveform starts and ends at s=1.0, descending to a constant value
    s_target in between, following a linear ramp.

      s_target:   s-parameter to descend to (between 0 and 1)
      hold_time:  amount of time (in us) to spend at s_target (must be >= 2.0us)
      ramp_slope: slope of transition region, in units 1/us
    """
    # validate parameters
    if s_target < 0.0 or s_target > 1.0:
        raise ValueError("s_target must be between 0 and 1")
    if hold_time < 0.0:
        raise ValueError("hold_time must be >= 0")
    if ramp_back_slope > 0.2:
        raise ValueError("ramp_back_slope must be <= 0.2")
    if ramp_back_slope <= 0.0:
        raise ValueError("ramp_back_slope must be > 0")

    ramp_time = (1.0 - s_target) / ramp_back_slope

    initial_s = 1.0
    pattern = [[0.0, initial_s]]

    # don't add new points if s_target == 1.0
    if s_target < 1.0:
        pattern.append([round(ramp_time, 4), round(s_target, 4)])
        if hold_time != 0:
            pattern.append([round(ramp_time+hold_time, 4), round(s_target, 4)])

    # add last point
    if ramp_up_slope is not None:
        ramp_up_time = (1.0-s_target)/ramp_up_slope
        pattern.append([round(ramp_time + hold_time + ramp_up_time, 4), round(1.0, 4)])
    else:
        pattern.append([round(ramp_time + hold_time + ramp_up_time, 4), round(1.0, 4)])

    return pattern
