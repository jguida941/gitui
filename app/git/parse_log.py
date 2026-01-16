from __future__ import annotations

from app.core.models import Commit

RECORD_SEP = "\x1e"
FIELD_SEP = "\x1f"


def parse_log_records(payload: bytes) -> list[Commit]:
    """Parse structured git log records into Commit objects.

    Expected format per record:
    oid<US>parents<US>author_name<US>author_email<US>author_date<US>subject<RS>
    """
    text = payload.decode("utf-8", errors="replace")
    commits: list[Commit] = []

    # Records are separated by ASCII record separator (0x1e).
    for record in text.split(RECORD_SEP):
        if not record:
            continue

        fields = record.split(FIELD_SEP)
        if len(fields) < 6:
            # Pad missing fields to keep parsing predictable.
            fields += [""] * (6 - len(fields))

        oid, parents_raw, author_name, author_email, author_date, subject = fields[:6]
        parents = parents_raw.split() if parents_raw else []

        commits.append(
            Commit(
                oid=oid,
                parents=parents,
                author_name=author_name,
                author_email=author_email,
                author_date=author_date,
                subject=subject,
            )
        )

    return commits
