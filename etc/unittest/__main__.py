import unittest

import gptc.debug

gptc.debug.version_check = False

from .asyncio import *
from .backend import *
from .client import *
from .config_provider import *
from .image_client import *
from .include import *
from .main import *
from .mcp import *
from .model import *
from .models import *
from .retry_provider import *
from .test_auth_retry import *
from .test_deepseek_chunk_log import *

# from .test_deepseek_stream import *
from .test_deepseek_upload import *
from .test_gemini import *
from .thinking import *
from .tool_support_provider import *
from .web_search import *

# from .test_cdp_parallel import *

unittest.main()
