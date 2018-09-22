# -*- coding: utf-8 -*-
# Copyright: (C) 2018 Lovac42
# Support: https://github.com/lovac42/ReflectOnMee
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
# Version: 0.0.1


from aqt import mw
from anki.hooks import wrap
from aqt.reviewer import Reviewer
# from aqt.utils import showWarning, showText

from anki import version
ANKI21 = version.startswith("2.1.")
if ANKI21:
    from PyQt5 import QtCore, QtGui, QtWidgets
else:
    from PyQt4 import QtCore, QtGui as QtWidgets



ROMee_State = False

#JS Timer won't affect log stats, for display only.
BT_JS="""
maxTime=%d
time=0
btn=document.querySelectorAll('table table button');
for(i=0;i<btn.length;i++){
 btn[i].disabled=true;
 btn[i].setAttribute('style','visibility:hidden');
}
window.setTimeout(function(){
 for(i=0;i<btn.length;i++){
  btn[i].disabled=false;
  btn[i].setAttribute('style','');
 }
},maxTime*1000);
"""


def keys_off(boo):
    global ROMee_State
    ROMee_State=boo

def eval(delay):
    keys_off(True)

    if ANKI21:
        mw.reviewer.bottom.web.page().runJavaScript(BT_JS%delay)
    else:
        mw.reviewer.bottom.web.eval(BT_JS%delay)

    #timer to re-enable keybind
    QTimer.singleShot(delay*1000, lambda: keys_off(False))


def showEaseButtons(self):
    conf=mw.col.decks.confForDid(self.card.did)
    limit=conf.get("rgs_limit", 0)
    if limit<1: return

    delay=conf.get("rgs_pause", 5)
    if (self.card.timeTaken()//1000)>limit:
        eval(delay)
    elif self.card.queue==1:
        eval(3)

Reviewer._showEaseButtons = wrap(Reviewer._showEaseButtons, showEaseButtons, 'after')


#Prevent key bypass
def answerCard(self, ease, _old):
    if ROMee_State: return
    _old(self, ease)
Reviewer._answerCard = wrap(Reviewer._answerCard, answerCard, 'around')



##################################################
#
#  GUI stuff, adds deck menu options to enable/disable
#  this addon for specific decks
#
#################################################
import aqt
import aqt.deckconf
from aqt.qt import *


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

def dconfsetupUi(self, Dialog):
    r=self.gridLayout_3.rowCount()

    #ShowAnswer Timeout limit
    self.rgs_limit_label = QtWidgets.QLabel(self.tab_3)
    self.rgs_limit_label.setObjectName(_fromUtf8("rgs_limit_label"))
    self.rgs_limit_label.setText(_("RefxGrade Ans Limit:"))
    self.gridLayout_3.addWidget(self.rgs_limit_label, r, 0, 1, 1)
    self.rgs_limit = QtWidgets.QSpinBox(self.tab_3)
    self.rgs_limit.setMinimum(0)
    self.rgs_limit.setMaximum(120)
    self.rgs_limit.setSingleStep(5)
    self.rgs_limit.setObjectName(_fromUtf8("rgs_limit"))
    self.gridLayout_3.addWidget(self.rgs_limit, r, 1, 1, 1)
    self.label_sec = QtWidgets.QLabel(self.tab_3)
    self.label_sec.setObjectName(_fromUtf8("label_sec"))
    self.label_sec.setText(_("secs (0 = disabled)"))
    self.gridLayout_3.addWidget(self.label_sec, r, 2, 1, 1)

    #Pause limit
    r+=1
    self.rgs_pause_label = QtWidgets.QLabel(self.tab_3)
    self.rgs_pause_label.setObjectName(_fromUtf8("rgs_pause_label"))
    self.rgs_pause_label.setText(_("RefxGrade Pause:"))
    self.gridLayout_3.addWidget(self.rgs_pause_label, r, 0, 1, 1)
    self.rgs_pause = QtWidgets.QSpinBox(self.tab_3)
    self.rgs_pause.setMinimum(2)
    self.rgs_pause.setMaximum(60)
    self.rgs_pause.setSingleStep(5)
    self.rgs_pause.setObjectName(_fromUtf8("rgs_pause"))
    self.gridLayout_3.addWidget(self.rgs_pause, r, 1, 1, 1)
    self.label_sec2 = QtWidgets.QLabel(self.tab_3)
    self.label_sec2.setObjectName(_fromUtf8("label_sec2"))
    self.label_sec2.setText(_("secs"))
    self.gridLayout_3.addWidget(self.label_sec2, r, 2, 1, 1)


def loadConf(self):
    lim=self.conf.get("rgs_limit", 0)
    self.form.rgs_limit.setValue(lim)
    lim=self.conf.get("rgs_pause", 10)
    self.form.rgs_pause.setValue(lim)

def saveConf(self):
    self.conf['rgs_limit']=self.form.rgs_limit.value()
    self.conf['rgs_pause']=self.form.rgs_pause.value()

aqt.forms.dconf.Ui_Dialog.setupUi = wrap(aqt.forms.dconf.Ui_Dialog.setupUi, dconfsetupUi, pos="after")
aqt.deckconf.DeckConf.loadConf = wrap(aqt.deckconf.DeckConf.loadConf, loadConf, pos="after")
aqt.deckconf.DeckConf.saveConf = wrap(aqt.deckconf.DeckConf.saveConf, saveConf, pos="before")
