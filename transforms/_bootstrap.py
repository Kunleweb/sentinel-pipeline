"""
Adds transforms/ and extractors/ to sys.path.
Must be the first import in every transforms module.
"""
import sys
import os

_transforms = os.path.dirname(os.path.abspath(__file__))
_extractors = os.path.normpath(os.path.join(_transforms, "..", "extractors"))

for _p in [_transforms, _extractors]:
    if _p not in sys.path:
        sys.path.insert(0, _p)
