import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.vectorstore import BaseElasticSearch

BaseElasticSearch().create_index()
