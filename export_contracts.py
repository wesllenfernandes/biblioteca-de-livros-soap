import os
from urllib.request import urlopen
from xml.etree import ElementTree as ET

WSDL_URL = "http://127.0.0.1:8000/?wsdl"
OUTPUT_DIR = os.path.join("docs", "contratos")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    wsdl_content = urlopen(WSDL_URL).read()
    wsdl_path = os.path.join(OUTPUT_DIR, "catalogo_cursos.wsdl")
    with open(wsdl_path, "wb") as wsdl_file:
        wsdl_file.write(wsdl_content)

    root = ET.fromstring(wsdl_content)
    schema = root.find(".//{http://www.w3.org/2001/XMLSchema}schema")
    if schema is not None:
        xsd_path = os.path.join(OUTPUT_DIR, "catalogo_cursos.xsd")
        with open(xsd_path, "wb") as xsd_file:
            xsd_file.write(ET.tostring(schema, encoding="utf-8", xml_declaration=True))

    print(f"WSDL exportado para {wsdl_path}")
    if schema is not None:
        print(f"XSD exportado para {xsd_path}")


if __name__ == "__main__":
    main()
