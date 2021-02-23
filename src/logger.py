import sys
import logging

# critical
# error
# warning
# debug
# info

log = logging.getLogger('')

handler = logging.StreamHandler(sys)
handler.setLevel(logging.WARNING)
log.addHandler(handler)