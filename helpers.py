
#    Copyright 2018 D-Wave Systems Inc.

#    Licensed under the Apache License, Version 2.0 (the "License")
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http: // www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import matplotlib.pyplot as plt

# Coupler pairs for the 16-bit problem: (0, 5), (1, 5), etc 
u0 = [0, 1, 1, 1, 2, 2, 2, 3, 5,  6,  8,  9,  9,  9,  10, 10, 10, 11]
v0 = [5, 5, 7, 6, 4, 5, 6, 6, 13, 14, 13, 13, 14, 15, 12, 13, 14, 14]

def direct_embedding(nodelist, edgelist, cn=16):
    """cn refers to a Chimera graph consisting of an NxN grid of unit cells """
    if cn != 16:
        raise ValueError("Currently enabled only on D-Wave 2000Q systems.")    
    for row in range(cn):
        for column in range(cn-1):
            offset = 8*cn*row + 8*column
            u = [offset + val for val in u0]
            v = [offset + val for val in v0]
            edges = set(zip(u, v))
            nodes = set(range(offset, offset+16))
            if not edges.issubset(edgelist) or not nodes.issubset(nodelist):
                print("Missing qubits in row {}, column {}. Trying next Chimera unit cells".format(row, column))
            else:
                print("Valid minor-embedding found for row {}, column {}.".format(row, column))
                return(nodes, edges)


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

def e_h_plot(pdf):
    """Plot energy and Hamming distances of consecutive samples."""
    columns = list(pdf.columns.values)
    rows = list(pdf.index.values)
    from matplotlib.gridspec import GridSpec    
    figures = ['fig_energy', 'fig_hamming']
    gs = GridSpec(2, 2)
    for idx_fig, fig in enumerate(figures):
        fig = plt.figure(idx_fig, figsize=(6, 6.5))
        fig.text(0.5, 0.04,'Sample')
        fig.text(0.04, 0.5,columns[idx_fig+1], rotation='vertical')
        fig.suptitle(columns[idx_fig+1]+' Time Series')
        for idx_anneal, anneal in enumerate(rows):
            if idx_anneal//2==1:
                f_ax = plt.subplot(gs[1, :])
            else:
                f_ax = plt.subplot(gs[idx_anneal//2, idx_anneal%2])
            plt.title(rows[idx_anneal])
            dots = f_ax.plot(pdf.loc[anneal,columns[idx_fig+1]], '.') 
            mean = f_ax.axhline(y=pdf.loc[anneal,columns[idx_fig+5]], color='r')
        fig.legend([mean],['Average '+ columns[idx_fig+1]], loc=4)



