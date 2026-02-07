from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import json
import requests
from pystac_client import Client

try:
    import planetary_computer as pc
except Exception:
    pc = None

from fpts.config.settings import Settings


@dataclass(frozen=True)
class Mod13Q1AssetRef:
    item_id: str
    dt: str  # ISO datetime string
    doy: int
    asset_key: str
    href: str  # signed href (Planetary Computer)


@dataclass(frozen=True)
class Mod13Q1Plan:
    collection: str
    year: int
    bbox: tuple[float, float, float, float]  # (min_lon, min_lat, max_lon, max_lat)
    assets: list[Mod13Q1AssetRef]


def _doy_from_iso(dt: str) -> int:
    # dt is typically like "2020-01-01T00:00:00Z"
    d = datetime.fromisoformat(dt.replace("Z", "+00:00")).date()
    return int(d.strftime("%j"))


class Mod13Q1IngestionService:

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def build_plan(
        self, *, year: int, bbox: tuple[float, float, float, float]
    ) -> Mod13Q1Plan:
        if pc is None:
            raise RuntimeError("planetary-computer package not available")

        catalog = Client.open(self._settings.pc_stac_url)
        dt_range = f"{year}-01-01/{year}-12-31"

        search = catalog.search(
            collections=[self._settings.mod13q1_collection],
            bbox=list(bbox),
            datetime=dt_range,
        )
        items = list(search.items())

        assets: list[Mod13Q1AssetRef] = []
        for item in items:
            signed = pc.sign(item).to_dict()  # sign each item to get SAS URLs
            props = signed.get("properties", {})
            dt = props.get("datetime")
            if not dt:
                # fallback if datetime missing
                dt = props.get("start_datetime") or props.get("end_datetime")
            if not dt:
                raise ValueError(
                    f"STAC item missing datetime fields: {signed.get('id')}"
                )

            # pick NDVI asset
            item_assets: dict[str, Any] = signed.get("assets", {})
            if "ndvi" not in item_assets:
                # fail fast so we learn the exact asset key early
                raise ValueError(
                    f"Expected 'ndvi' asset not found in item {signed.get('id')}; keys={list(item_assets)}"
                )

            href = item_assets["ndvi"]["href"]
            assets.append(
                Mod13Q1AssetRef(
                    item_id=str(signed.get("id")),
                    dt=str(dt),
                    doy=_doy_from_iso(str(dt)),
                    asset_key="ndvi",
                    href=str(href),
                )
            )

        assets.sort(
            key=lambda a: (a.doy, a.item_id)
        )  # stable ordering for deterministic manifests
        return Mod13Q1Plan(
            collection=self._settings.mod13q1_collection,
            year=year,
            bbox=bbox,
            assets=assets,
        )

    def write_manifest(self, plan: Mod13Q1Plan, out_path: Path) -> None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(plan)
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True))


def verify_href_reachable(href: str, timeout_s: float = 20.0) -> None:
    r = requests.head(href, timeout=timeout_s, allow_redirects=True)
    r.raise_for_status()
