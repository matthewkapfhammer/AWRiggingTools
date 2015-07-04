#!/usr/bin/python
import pymel.core as pmc


def getCurrentSelection():
    return pmc.ls(sl=1)


def breakAttrs(node, nodeAttr):
    """
    :param node: The node upon which to sever an attribute connection.
    :param nodeAttr: List or string. If list, operate on the node for each attr.
    """
    if isinstance(nodeAttr, list):
        for a in nodeAttr:
            pmc.disconnectAttr(node + '.' + a)
    else:
        pmc.disconnectAttr(node + '.' + nodeAttr)


def unlockXForms(node):
    """
    :param node:
    :return:
    """
    xforms = ['.rotate', '.translate', '.scale']
    axes = ['X', 'Y', 'Z']

    map(pmc.setAttr(node + xforms + axes, lock=False, keyable=True))

# Goddammit