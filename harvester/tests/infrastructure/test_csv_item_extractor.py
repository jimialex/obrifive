from datetime import UTC, datetime
from decimal import Decimal

from expects import be_empty, equal, expect, have_len

from src.domain.models import Artifact, Source, SourceKind, Target
from src.infrastructure.extractors.csv_item_extractor import CsvItemExtractor


def _csv_artifact() -> Artifact:
    source = Source(location="inbox://lista.csv", kind=SourceKind.FILE)
    return Artifact(
        artifact_id="a" * 64,
        target=Target(source=source, location=source.location),
        content_type="text/csv",
        size_bytes=0,
        fetched_at=datetime(2026, 10, 26, tzinfo=UTC),
    )


class CsvItemExtractorTests:
    async def test_maps_spanish_headers_and_semicolon_delimiter(self):
        csv_content = "Código;Descripción;Unidad;Precio\nCL-2;Clavo 2 pulgadas;kg;Bs. 18,50\n".encode()
        csv_item_extractor = CsvItemExtractor()

        catalog_items = await csv_item_extractor.extract(_csv_artifact(), csv_content)

        expect(catalog_items).to(have_len(1))
        expect(catalog_items[0].sku).to(equal("CL-2"))
        expect(catalog_items[0].name).to(equal("Clavo 2 pulgadas"))
        expect(catalog_items[0].unit).to(equal("kg"))
        expect(catalog_items[0].price_bob).to(equal(Decimal("18.50")))
        expect(catalog_items[0].provenance.locator).to(equal("row:2"))

    async def test_skips_rows_without_name(self):
        csv_content = b"producto,precio\n,10\nCemento IP-30,62\n"
        csv_item_extractor = CsvItemExtractor()

        catalog_items = await csv_item_extractor.extract(_csv_artifact(), csv_content)

        expect([catalog_item.name for catalog_item in catalog_items]).to(equal(["Cemento IP-30"]))

    async def test_returns_nothing_without_a_name_column(self):
        csv_content = b"columna_a,columna_b\nx,y\n"
        csv_item_extractor = CsvItemExtractor()

        catalog_items = await csv_item_extractor.extract(_csv_artifact(), csv_content)

        expect(catalog_items).to(be_empty)
