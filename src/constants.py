from pathlib import Path


BASE_DIR = Path('__file__').parent
OUTPUT_DEFAULT = None
OUTPUT_FILE = 'file'
OUTPUT_PRETTY = 'pretty'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DOWNLOAD_DIR = 'downloads'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
LOG_DIR = BASE_DIR / 'logs'
LOG_FORMAT = '%(asctime)s - [%(levelname)s] - %(message)s'
MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
PEP_LIST_URL = 'https://peps.python.org/numerical/'
RESULTS_DIR = 'results'
