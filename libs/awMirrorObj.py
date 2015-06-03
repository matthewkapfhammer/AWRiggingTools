__author__ = 'Alex'
from AWGeneral import *

def update_sel():
    curSel = getCurrentSelection()
    if len(curSel) > 1:
        pm.warning('You have more than one object selected.')
    elif len(curSel) == 0:
        pm.warning('You need to select something.')
    else:
        return curSel