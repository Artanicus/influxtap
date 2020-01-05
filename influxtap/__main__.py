#!/usr/bin/env python3
import signal, time
from absl import flags, logging, app

import influxtap

FLAGS = flags.FLAGS
logging.set_verbosity(logging.WARNING)

flags.DEFINE_string('config', None, 'Path to YAML formatted config file.')
flags.DEFINE_integer('interval', 60, 'Global interval for data collection in seconds.')

flags.mark_flag_as_required('config')
    

def real_main(argv = None):
    tap = influxtap.Tappery(FLAGS.config)
    
    # Handle cache dumping if killed.
    def sigterm_handler(signal, frame):
        tap.cache.dump()
        logging.fatal('SIGTERM, going down')

    # Handle config reload on HUP.
    def sighup_handler(signal, frame):
        logging.warning('SIGHUP, reloading config')
        tap.reload_config(FLAGS.config)
    
    signal.signal(signal.SIGTERM, sigterm_handler)
    signal.signal(signal.SIGHUP, sighup_handler)
    
    while True:
        tap.probe()
        tap.store()
        time.sleep(FLAGS.interval)


def main(argv = None):
    app.run(real_main)

if __name__ == "__main__":
    app.run(real_main)
