from __future__ import annotations

from dotenv import find_dotenv, load_dotenv
load_dotenv(find_dotenv())

from service_runner import run

from document_generation_service.service import doc_service_callback

if __name__ == '__main__':
    run(doc_service_callback)
