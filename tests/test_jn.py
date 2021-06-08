# Copyright 2021 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import unittest

def run_jn(jn, timeout):

    open_jn = open(jn, "r", encoding='utf-8')
    notebook = nbformat.read(open_jn, nbformat.current_nbformat)
    open_jn.close()

    preprocessor = ExecutePreprocessor(timeout=timeout, kernel_name='python3')
    preprocessor.allow_errors = True
    preprocessor.preprocess(notebook, {'metadata': {'path': os.path.dirname(jn)}})

    return notebook

def collect_jn_errors(nb):

    errors = []
    for cell in nb.cells:
        if 'outputs' in cell:
            for output in cell['outputs']:
                if output.output_type == 'error':
                    errors.append(output)

    return errors

def embedding_fail(error_list):
    return error_list and error_list[0].evalue == 'no embedding found'

def robust_run_jn(jn, timeout, retries):

    run_num = 1
    notebook = run_jn(jn, timeout)
    errors = collect_jn_errors(notebook)

    while embedding_fail(errors) and run_num < retries:
        run_num += 1
        notebook = run_jn(jn, timeout)
        errors = collect_jn_errors(notebook)

    return notebook, errors

def cell_text(nb, cell):
    return nb["cells"][cell]["outputs"][0]["text"]

def cell_output(nb, cell, part, data_type):
    return nb["cells"][cell]["outputs"][part][data_type]

jn_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
jn_file = os.path.join(jn_dir, '01-reverse-annealing.ipynb')

class TestJupyterNotebook(unittest.TestCase):

    def test_jn(self):
        # Smoketest
        MAX_EMBEDDING_RETRIES = 3
        MAX_RUN_TIME = 200                 # Ran on my laptop in < 50 secs

        nb, errors = robust_run_jn(jn_file, MAX_RUN_TIME, MAX_EMBEDDING_RETRIES)

        self.assertEqual(errors, [])

        # Section Feature Availability, code cell 1
        self.assertIn("Connected to sampler", cell_text(nb, 4))

        # Section Feature Availability, code cell 2
        self.assertIn("Maximum anneal-schedule points", cell_text(nb, 5))

        # Section Generating a Random Problem, code cell 1
        self.assertIn("Bias 0 assigned to", cell_text(nb, 8))

        # Section Defining the Anneal Schedule, code cell 1
        self.assertIn("Total anneal-schedule time", cell_text(nb, 10))

        # Section Defining the Anneal Schedule, code cell 2
        self.assertIn("image/png", cell_output(nb, 11, 0, "data"))

        # Section Setting the Initial State, code cell 1
        self.assertIn("Lowest energy found", cell_text(nb, 13))

        # Section Running Reverse Anneal, code cell 1
        self.assertIn("Lowest energy found", cell_text(nb, 15))

        # Section Generating the 16-Bit Problem, code cell 3
        self.assertIn("Energy of the global minimum", cell_text(nb, 22))

        # Section Sampling Methods and Configuration, Subsection Pause Schedule, code cell 1
        self.assertIn("image/png", cell_output(nb, 26, 0, "data"))

        # Section Initial State for Reverse Anneal, code cell 1
        self.assertIn("Energy of initial state", cell_text(nb, 28))

        # Section Sampling, code cell 2
        self.assertIn("samples from standard forward annealing", cell_text(nb, 37))

        # Section Analysis, code cell 2
        self.assertIn("Lowest energy found for each method", cell_text(nb, 42))

        # Section Analysis, code cell 3
        self.assertIn("image/png", cell_output(nb, 44, 0, "data"))

        # Section Modulating the Reverse-Annealing Parameters, code cell 1
        self.assertIn("Running reverse anneals with", cell_text(nb, 46))

        # Section Modulating the Reverse-Annealing Parameters, code cell 2
        self.assertIn("image/png", cell_output(nb, 48, 0, "data"))

        # Section Exercise: Reverse Anneal for Various Parameters, code cell 1
        self.assertIn("image/png", cell_output(nb, 52, 1, "data"))
