#!/usr/bin/python
import pymel.core as pmc

from AWGeneral import *

def searchReplace(searchFor, replaceWith):
    for selected in getCurrentSelection():
        pmc.rename(selected, selected.replace(searchFor, replaceWith))

def prefix(strPrefix):
    for selected in getCurrentSelection():
        pmc.rename(selected, strPrefix + selected)

def suffix(strSuffix):
    for selected in getCurrentSelection():
        pmc.rename(selected, selected + strSuffix)

def rename(strRename, startNum, paddingNum):
    for selected in getCurrentSelection():
        pmc.rename(selected, strRename + startNum.zfill(int(paddingNum)))


