from __future__ import annotations

import sqlite3


TIER_NAMES = ["Diagnostic", "Architecture Sprint", "PoC", "Implementation", "Assurance"]


def generate_offer_permutations(con: sqlite3.Connection) -> tuple[int, int]:
    """Materialize all commercially coherent contiguous-ladder configurations."""
    offers = {
        (product_id, tier_id): config_id
        for product_id, tier_id, config_id in con.execute(
            "SELECT product_id, tier_id, config_id FROM offers"
        )
    }

    intervals = [None] + [(i, j) for i in range(1, 6) for j in range(i, 6)]
    permutation_count = 0
    link_count = 0

    for ds_interval in intervals:
        for dc_interval in intervals:
            if ds_interval is None and dc_interval is None:
                continue

            chosen: list[tuple[int, int, str]] = []
            if ds_interval:
                chosen.extend(
                    (1, stage, offers[(1, stage)])
                    for stage in range(ds_interval[0], ds_interval[1] + 1)
                )
            if dc_interval:
                chosen.extend(
                    (2, stage, offers[(2, stage)])
                    for stage in range(dc_interval[0], dc_interval[1] + 1)
                )
            chosen.sort(key=lambda row: (row[0], row[1]))

            permutation_count += 1
            permutation_id = f"PERM-{permutation_count:03d}"

            def interval_text(interval):
                if interval is None:
                    return None
                start, end = interval
                if start == end:
                    return TIER_NAMES[start - 1]
                return f"{TIER_NAMES[start - 1]} → {TIER_NAMES[end - 1]}"

            label_parts = []
            if ds_interval:
                label_parts.append(f"DeSci [{interval_text(ds_interval)}]")
            if dc_interval:
                label_parts.append(f"Compute [{interval_text(dc_interval)}]")

            canonical_key = (
                f"DS:{'0' if ds_interval is None else f'{ds_interval[0]}-{ds_interval[1]}'}"
                f"|DC:{'0' if dc_interval is None else f'{dc_interval[0]}-{dc_interval[1]}'}"
            )

            con.execute(
                """
                INSERT INTO offer_permutations (
                    permutation_id, canonical_key, label, scope,
                    ds_start_stage, ds_end_stage, dc_start_stage, dc_end_stage,
                    product_count, offer_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    permutation_id,
                    canonical_key,
                    " + ".join(label_parts),
                    "cross_product" if ds_interval and dc_interval else "single_product",
                    ds_interval[0] if ds_interval else None,
                    ds_interval[1] if ds_interval else None,
                    dc_interval[0] if dc_interval else None,
                    dc_interval[1] if dc_interval else None,
                    int(bool(ds_interval)) + int(bool(dc_interval)),
                    len(chosen),
                ),
            )

            for sequence_no, (_, _, config_id) in enumerate(chosen, 1):
                con.execute(
                    """
                    INSERT INTO permutation_offers
                    (permutation_id, config_id, sequence_no)
                    VALUES (?, ?, ?)
                    """,
                    (permutation_id, config_id, sequence_no),
                )
                link_count += 1

    return permutation_count, link_count
