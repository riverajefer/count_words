import logging
import sys
logging.basicConfig(stream=sys.stderr)

sys.path.insert(0, '/home/Flask/count_words/env/lib/python3.8/site-packages')
sys.path.insert(0, '/home/Flask/count_words')

from run import app as application
#application.secret_key = 'anything you wish'