# -*- coding: utf-8 -*-
"""
Copyright 2018 Google Inc.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-------------------------------------------------------------------------------

A dataflow pipeline to clean MediaWiki formats in comments and convert nested array type to acceptable type in BigQuery.

Run with:

  python dataflow_content_clean.py --setup_file ./setup.py --input=InputStorage --output=OutputStorage --jobname=YourJobName

"""
from __future__ import absolute_import
import argparse
import logging
import subprocess
import json
from os import path
import urllib2
import traceback
import sys
import multiprocessing
from construct_utils.utils.third_party.clean import content_clean

import apache_beam as beam
from apache_beam.metrics.metric import Metrics
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

TIMEOUT = 2

def run(known_args, pipeline_args):
  """Main entry point; defines and runs the sharding pipeline."""

  pipeline_args.extend([
    '--runner=DataflowRunner',
    '--project=wikidetox-viz',
    '--staging_location=gs://wikidetox-viz-dataflow/staging',
    '--temp_location=gs://wikidetox-viz-dataflow/tmp',
    '--job_name=resultformatting-{}'.format(known_args.jobname),
    '--max_num_workers=80'])
  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = True

  # Queries extracting the data
  with beam.Pipeline(options=pipeline_options) as p:
       p = (p | beam.io.ReadFromText(known_args.input)
            | beam.Map(lambda x: json.dumps(eval(x)))
            | "WriteResult" >> beam.io.WriteToText(known_args.output))

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  parser = argparse.ArgumentParser()
  # Input/Output parameters
  parser.add_argument('--input',
                      dest='input',
                      help='Input storage.')
  parser.add_argument('--output',
                      dest='output',
                      help='Output storage.')
  parser.add_argument('--jobname',
                      dest='jobname',
                      help='The dataflow jobname.')


  known_args, pipeline_args = parser.parse_known_args()
  run(known_args, pipeline_args)
