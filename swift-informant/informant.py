# Copyright (c) 2010-2011 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from webob import Request, Response
from swift.common.utils import split_path, get_logger
from eventlet.green import socket
from random import random
import time

class InformantMiddleware(object):
    """
    Informant Middleware used for sending events to statsd
    """

    def __init__(self, app, conf, *args, **kwargs):
        self.app = app
        self.logger = get_logger(conf, log_route='informant')
        self.statsd_host = conf.get('statsd_host', '127.0.0.1')
        self.statsd_port = int(conf.get('statsd_port', '8125'))
        self.statsd_addr = (self.statsd_host, self.statsd_port)
        self.statsd_sample_rate = float(conf.get('statsd_sample_rate', '.5'))
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_event(self, payload):
        try:
            self.udp_socket.sendto(payload, self.statsd_addr)
        except Exception as err:
            self.logger.critical("udp oops")
            raise
            #pass #udp sendto failed, but thats ok

    def statsd_counter_increment(self, stats, delta=1):
        """
        Increment multiple statsd stats counters
        """
        if self.statsd_sample_rate < 1:
            if random() <= self.statsd_sample_rate:
                for item in stats:
                    payload = "%s:%s|c|@%s" % (item, delta, self.statsd_sample_rate)
                    self.send_event(payload)
        else:
            for item in stats:
                payload = "%s:%s|c" % (item, delta)
                self.send_event(payload)


    def __call__(self, env, start_response):
        def start_response_snitch(status, headers):
            req = Request(env)
            self.statsd_counter_increment([req.method, status.split()[0]])
            return start_response(status, headers)
        
        return self.app(env, start_response_snitch)
            

def filter_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)

    def informant_filter(app):
        return InformantMiddleware(app, conf)
    return informant_filter