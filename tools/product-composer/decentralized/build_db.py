from pathlib import Path
import sqlite3

from generate_permutations import generate_offer_permutations


ROOT = Path(__file__).resolve().parent
DB = ROOT / "decentralized_product_composer.sqlite"

if DB.exists():
    DB.unlink()

con = sqlite3.connect(DB)
con.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))

con.execute("BEGIN")
for seed_file in sorted((ROOT / "seed").glob("core_*.sql")):
    con.executescript(seed_file.read_text(encoding="utf-8"))
permutations, links = generate_offer_permutations(con)
con.commit()

con.executescript((ROOT / "views.sql").read_text(encoding="utf-8"))

fk_errors = con.execute("PRAGMA foreign_key_check").fetchall()
integrity = con.execute("PRAGMA integrity_check").fetchone()[0]

if fk_errors:
    raise SystemExit(f"Foreign-key errors: {fk_errors}")
if integrity != "ok":
    raise SystemExit(f"Integrity check failed: {integrity}")
if permutations != 255 or links != 1120:
    raise SystemExit(
        f"Permutation generation mismatch: permutations={permutations}, links={links}"
    )

print(DB)
print("foreign_key_check = PASS")
print("integrity_check =", integrity)
print("offer_permutations =", permutations)
print("permutation_offers =", links)
