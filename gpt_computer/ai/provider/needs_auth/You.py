from __future__ import annotations

from ..template import OpenaiTemplate


class You(OpenaiTemplate):
    label = "You.com"
    url = "https://you.com"
    backend_url = "https://gptc.space/api/you.com"
    working = True
