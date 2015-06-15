__author__ = 'Alex'
from AWGeneral import *
import pymel.core as pm

class AWMirrorObject:
    def __init__(self):
        pass
    def updateSelection(self):
        curSel = getCurrentSelection()
        if len(curSel) > 1:
            pm.warning('You have more than one object selected.')
        elif len(curSel) == 0:
            pm.warning('You need to select something.')
        else:
            self.mirrorObj_selObj_text.text = curSel[0]

    def mirror_object(self):
        ## THIS DOESN'T EXIST YET THIS IS WHAT I'M TRYING TO FIGURE OUT.
        i = 0
        checkedattr = []

        obj = self.sel_obj_text.text()
        searchtext = self.search_text.text()
        replacetext = self.replace_text.text()

        if not obj:
            pm.error("You need something in the Update Object box")
        else:
            if not searchtext or not replacetext:
                pm.error("You need to enter something to search or replace")
            else:
                if self.x_rb.isChecked():
                    i = 0
                if self.y_rb.isChecked():
                    i = 1
                if self.z_rb.isChecked():
                    i = 2
                if  self.check_trans.checkState():
                    checkedattr.append('translate')
                if self.check_rotate.checkState():
                    checkedattr.append('rotate')
                if self.check_scale.checkState():
                    checkedattr.append('scale')

                if not checkedattr:
                    pm.error("No attributes selected")
                else:
                    for eachattr in checkedattr:
                        objA = pm.getAttr(obj + '.{0}'.format(eachattr))
                        objMirror = obj.replace(searchtext, replacetext)
                        pm.select(objMirror)
                        e = objMirror + '.{0}'.format(eachattr)

                        objA[i] = objA[i] * -1

                        pm.setAttr(e, objA)



