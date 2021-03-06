import os
import re
import subprocess
import sys
from enum import auto
from enum import Enum

RCE_RULE_FLAG = "--dangerously-allow-arbitrary-code-execution-from-rules"
RULES_KEY = "rules"
SEMGREP_USER_AGENT = "semgrep-give-me-yaml"
ID_KEY = "id"
SEMGREP_URL = "https://semgrep.dev/"
PLEASE_FILE_ISSUE_TEXT = "An error occurred while invoking the semgrep engine; please help us fix this by creating an issue at https://semgrep.dev"

DEFAULT_SEMGREP_CONFIG_NAME = "semgrep"
DEFAULT_CONFIG_FILE = f".{DEFAULT_SEMGREP_CONFIG_NAME}.yml"
DEFAULT_CONFIG_FOLDER = f".{DEFAULT_SEMGREP_CONFIG_NAME}"

YML_EXTENSIONS = {".yml", ".yaml"}

__VERSION__ = "0.11.0"


def compute_semgrep_path() -> str:
    exec_name = "semgrep-core"
    if subprocess.run(["which", exec_name], stdout=subprocess.DEVNULL).returncode != 0:
        # look for something in the same dir as the Python interpreter
        relative_path = os.path.join(os.path.dirname(sys.executable), exec_name)
        if os.path.exists(relative_path):
            exec_name = relative_path
    return exec_name


SEMGREP_PATH = compute_semgrep_path()


class OutputFormat(Enum):
    TEXT = auto()
    JSON = auto()
    JSON_DEBUG = auto()
    SARIF = auto()

    def is_json(self) -> bool:
        return self == OutputFormat.JSON or self == OutputFormat.JSON_DEBUG


# Inline 'noqa' implementation modified from flake8:
# https://github.com/PyCQA/flake8/blob/master/src/flake8/defaults.py
NOSEM_INLINE_RE = re.compile(
    # We're looking for items that look like this:
    # ' nosem'
    # ' nosem: example-pattern-id'
    # ' nosem: pattern-id1,pattern-id2'
    # ' NOSEM:pattern-id1,pattern-id2'
    #
    # * We do not want to capture the ': ' that follows 'nosem'
    # * We do not care about the casing of 'nosem'
    # * We want a comma-separated list of ids
    # * We want multi-language support, so we cannot strictly look for
    #   Python comments that begin with '# '
    #
    r" nosem(?::[\s]?(?P<ids>([^,\s](?:[,\s]+)?)+))?",
    re.IGNORECASE,
)
COMMA_SEPARATED_LIST_RE = re.compile(r"[,\s]")
