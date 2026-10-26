from typing import Any


async def loader_from_excel(*args: Any, **kwargs: Any) -> None:
    """Reserved port for the future structured Excel catalog loader."""
    pass


async def loader_from_pdf(*args: Any, **kwargs: Any) -> None:
    """Reserved port for PDF extraction into catalog staging."""
    pass


async def loader_from_url(*args: Any, **kwargs: Any) -> None:
    """Reserved port for a site-specific catalog loader."""
    pass
