import sys
import logging

# critical
# error
# warning
# debug
# info

log = logging.getLogger('')

handler = logging.StreamHandler(sys)
# handler.setLevel(logging.INFO)
log.addHandler(handler)