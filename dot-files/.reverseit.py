#!/usr/bin/python
# -*- coding: UTF-8 -*-

from sys import stdin, stdout

pchars = u"abcdefghijklmnopqrstuvwxyz,.?!'()[]{}"
fchars = u"ɐqɔpǝɟƃɥıɾʞlɯuodbɹsʇnʌʍxʎz'˙¿¡,)(][}{"
flipper = dict(zip(pchars, fchars))

def flip(s):
  charList = [ flipper.get(x, x) for x in s.lower() ]
  charList.reverse()
  return "".join(charList).strip('\n')

stdout.write(flip(stdin.read()).encode('utf8'))
