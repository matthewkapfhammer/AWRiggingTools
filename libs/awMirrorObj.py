__author__ = 'Alex'
from AWGeneral import *
import pymel.core as pm

def AWMirrorObject(currentObj, tChecked, rChecked, sChecked, axis, searchText, replaceText=None):
    i = 0
    checkedAttr = []

    if not currentObj:
        pm.error('You need something in the Update Object box. Please select an object.')
    else:
        if not searchText:
            pm.error('You need to enter what you want to search for.')
        else:
            if axis == 'X':
                i = 0
            if axis == 'Y':
                i = 1
            if axis == 'Z':
                i = 2

            if tChecked:
                checkedAttr.append('translate')
            if rChecked:
                checkedAttr.append('rotate')
            if sChecked:
                checkedAttr.append('scale')

            if replaceText is None:
                replaceText = ''

            if not checkedAttr:
                pm.error('No attributes selected.')
            else:
                for eachAttr in checkedAttr:
                    objA = pm.getAttr(currentObj + '.{0}'.format(eachAttr))
                    objMirror = currentObj.replace(searchText, replaceText)
                    pm.select(objMirror)
                    e = objMirror + '.{0}'.format(eachAttr)
                    objA[i] = (objA[i] * -1)
                    pm.setAttr(e, objA)

