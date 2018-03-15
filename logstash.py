#!/usr/bin/env python

import protobix
import argparse
import socket
import sys
import simplejson
import requests

class LogstashServer(protobix.SampleProbe):
    __version__="0.0.1"


    def _init_probe(self):
        if self.options.host == 'localhost':
            self.hostname = socket.gethostname()
        else:
            self.hostname = self.options.host
        self.discovery_key = 'logstash.node.discovery'

    def _parse_probe_args(self, parser):
        es_probe_options = parser.add_argument_group('Logstash Configuration')
        es_probe_options.add_argument(
            '-H',  default='localhost', dest='host',
            help='Logstash server hostname.\nDefault: localhost'
        )
        es_probe_options.add_argument(
            '-P',  default=9600, dest='lgport',
            help='Logstash server port.\nDefault: 9600'
        )
        return parser

    def _do_get_rawdata(self,url):
        try:
            resp = requests.get(
                'http://' + self.options.host + ':' + str(self.options.lgport) + url,
                timeout=5
            )
            resp.raise_for_status()
        except Exception as e:
            self.logger.error('Step 2 - failed to open: ' + url)
            raise
        return resp

    def _process_items(self, zbx_key, raw_data):
        data = {}
        try:
            for key, value in raw_data.items():
                real_key = zbx_key.format(key)
                if isinstance(value, dict):
                    real_keys = real_key + '.{0}'
                    data.update(self._process_items(real_keys, value))
                else:
                    data[real_key] = value
        except TypeError as t:
            self.logger.error('Step 2 - failed to process items: ' + str(t))
        return data
    
    def _nodes_stats(self, url):
        data = {}
        nodes_stats = self._do_get_rawdata(url)
        try:
            nodes_stats = nodes_stats.json()
        except TypeError:
            nodes_stats = nodes_stats.json
        # Process metrics list
        # Process JVM metrics
        zbx_key = 'logstash.jvm.{0}'
        for jvm_section in nodes_stats['jvm']:
            if not isinstance(nodes_stats['jvm'][jvm_section], dict):
                data[zbx_key.format(jvm_section)] = nodes_stats['jvm'][jvm_section]
            else:
                real_key = zbx_key.format(jvm_section) + '.{0}'
                data.update(
                    self._process_items(real_key, nodes_stats['jvm'][jvm_section])
                )
        # Process Process metrics
        zbx_key = 'logstash.process.{0}'
        for process_section in nodes_stats['process']:
            if not isinstance(nodes_stats['process'][process_section], dict):
                data[zbx_key.format(process_section)] = nodes_stats['process'][process_section]
            else:
                real_key = zbx_key.format(process_section) + '.{0}'
                data.update(
                    self._process_items(real_key, nodes_stats['process'][process_section])
                )
        # Process Pipeline global events metrics
        zbx_key = 'logstash.pipeline.events.{0}'
        for pipeline_events_section in nodes_stats['pipeline']['events']:
            if not isinstance(nodes_stats['pipeline']['events'][pipeline_events_section], dict):
                data[zbx_key.format(pipeline_events_section)] = nodes_stats['pipeline']['events'][pipeline_events_section]
            else:
                real_key = zbx_key.format(pipeline_events_section) + '.{0}'
                data.update(
                    self._process_items(real_key, nodes_stats['pipeline']['events'][pipeline_events_section])
                )
        return data

    def _get_discovery(self):
        data = { self.discovery_key:[] }
        return { self.hostname: data }

    def _get_metrics(self):
        data = { self.hostname: {} }
        # Get node stats
        nodes_data = self._nodes_stats('/_node/stats/')
        data[self.hostname].update(nodes_data)
        data[self.hostname]['logstash.zbx_version'] = self.__version__
        return data

if __name__ == '__main__':
    ret = LogstashServer().run()
    print((ret))
    sys.exit(ret)
