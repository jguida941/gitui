from __future__ import annotations

from app.core.models import StashEntry

RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"


def parse_stash_records(payload: bytes) -> list[StashEntry]:
    """Parse structured stash list output into StashEntry objects.

    Expected format per record:
    oid<US>selector<US>summary<US>date<RS>
    """
    text = payload.decode("utf-8", errors="replace")
    stashes: list[StashEntry] = []

    # Records are separated by ASCII record separator (0x1e).
    for record in text.split(RECORD_SEP):
        if not record:
            continue

        fields = record.split(FIELD_SEP)
        if len(fields) < 4:
            # Pad missing fields so we always unpack safely.
            fields += [""] * (4 - len(fields))

        oid, selector, summary, date = fields[:4]
        stashes.append(
            StashEntry(
                oid=oid,
                selector=selector,
                summary=summary,
                date=date,
            )
        )

    return stashes
