#!/usr/bin/python

import pymel.core as pmc

from awSettings import *


def getCurrentSelection():
    return pmc.ls(sl=1)


def breakAttrs(node, channels):
    """
    Wrote for batch breaking of attributes instead of doing them one by one.
    :param node: The node upon which to sever an attribute connection.
    :param nodeAttr: List or string. If list, operate on the node for each attr.
    """
    if not isinstance(channels, list):
        pmc.displayError(eINCORRECTTYPE)
        return

    for c in channels:
        pmc.disconnectAttr(node + '.' + c)


def unlockAttrs(node, channels):
    """
    Wrote for batch unlocking of attributes instead of doing them one by one.
    :param node: The node upon which to unlock an attribute connection.
    :param channels: List of channels to unlock.
    """
    if not isinstance(channels, list):
        pmc.displayError(eINCORRECTTYPE)
        return

    for c in channels:
        pmc.setAttr(str(node) + '.' + c, lock=False, keyable=True)

