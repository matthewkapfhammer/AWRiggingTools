#!/usr/bin/python
import pymel.core as pmc


def getCurrentSelection():
    return pmc.ls(sl=1)