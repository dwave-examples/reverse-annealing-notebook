# coding: utf-8
# Copyright 2020 D-Wave Systems Inc.
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
#
# =============================================================================

import matplotlib.pyplot as plt

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


