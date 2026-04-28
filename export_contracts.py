import os
from urllib.request import urlopen

PORT = os.environ.get("PORT", "8010")
WSDL_URL = f"http://127.0.0.1:{PORT}/?wsdl"
OUTPUT_DIR = os.path.join("docs", "contratos")
WSDL_PATH = os.path.join(OUTPUT_DIR, "catalogo_cursos.wsdl")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    wsdl_content = urlopen(WSDL_URL).read()
    with open(WSDL_PATH, "wb") as wsdl_file:
        wsdl_file.write(wsdl_content)
    print(f"WSDL exportado para {WSDL_PATH}")


if __name__ == "__main__":
    main()
