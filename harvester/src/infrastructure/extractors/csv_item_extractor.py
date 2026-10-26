import csv
import io
import unicodedata
from collections.abc import Sequence

from src.domain.models import Artifact, CatalogItem, ExtractionMethod, ItemProvenance
from src.domain.normalization import parse_bob_price

COLUMN_ALIASES = {
    "name": {"nombre", "producto", "descripcion", "detalle", "articulo", "item"},
    "sku": {"sku", "codigo", "cod", "code", "referencia", "ref"},
    "price": {"precio", "precio unitario", "pu", "p/u", "p.u.", "precio bs", "precio venta", "importe"},
    "unit": {"unidad", "und", "u/m", "um", "medida", "presentacion"},
}
SUPPORTED_ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")
HEURISTIC_CONFIDENCE = 0.9


def _normalize_header(header: str) -> str:
    decomposed_header = unicodedata.normalize("NFKD", header)
    return (
        "".join(character for character in decomposed_header if not unicodedata.combining(character)).strip().lower()
    )


class CsvItemExtractor:
    def can_extract(self, artifact: Artifact) -> bool:
        return artifact.content_type == "text/csv"

    async def extract(self, artifact: Artifact, content: bytes) -> list[CatalogItem]:
        csv_text = self._decode(content)
        csv_reader = csv.DictReader(io.StringIO(csv_text), dialect=self._sniff_dialect(csv_text))
        column_mapping = self._map_columns(csv_reader.fieldnames or [])
        if "name" not in column_mapping:
            return []
        catalog_items: list[CatalogItem] = []
        for row_number, csv_row in enumerate(csv_reader, start=2):
            product_name = (csv_row.get(column_mapping["name"]) or "").strip()
            if not product_name:
                continue
            raw_price = self._cell(csv_row, column_mapping.get("price"))
            catalog_items.append(
                CatalogItem(
                    name=product_name,
                    sku=self._cell(csv_row, column_mapping.get("sku")),
                    raw_price=raw_price,
                    price_bob=parse_bob_price(raw_price),
                    unit=self._cell(csv_row, column_mapping.get("unit")),
                    provenance=ItemProvenance(
                        artifact_id=artifact.artifact_id,
                        source_location=artifact.target.location,
                        locator=f"row:{row_number}",
                    ),
                    method=ExtractionMethod.HEURISTIC,
                    confidence=HEURISTIC_CONFIDENCE,
                )
            )
        return catalog_items

    @staticmethod
    def _decode(content: bytes) -> str:
        for encoding in SUPPORTED_ENCODINGS:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")

    @staticmethod
    def _sniff_dialect(csv_text: str) -> type[csv.Dialect]:
        header_line = csv_text.splitlines()[0] if csv_text else ""
        try:
            return csv.Sniffer().sniff(header_line, delimiters=",;\t|")
        except csv.Error:
            return csv.excel

    @staticmethod
    def _map_columns(fieldnames: Sequence[str]) -> dict[str, str]:
        column_mapping: dict[str, str] = {}
        for fieldname in fieldnames:
            normalized_fieldname = _normalize_header(fieldname)
            for field_key, aliases in COLUMN_ALIASES.items():
                if field_key not in column_mapping and normalized_fieldname in aliases:
                    column_mapping[field_key] = fieldname
        return column_mapping

    @staticmethod
    def _cell(csv_row: dict[str, str | None], column_name: str | None) -> str | None:
        if column_name is None:
            return None
        cell_value = (csv_row.get(column_name) or "").strip()
        return cell_value or None
