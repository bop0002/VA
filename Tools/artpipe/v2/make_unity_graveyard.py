"""v2 - dua map C_graveyard vao Unity: sheet da slice san + 32 Tile asset + RuleTile + 3 chunk mau.

Khac Meadow (user tu slice/tao tile trong editor): o day ghi thang .meta slice 8x4 (ten _0.._31 trai->phai,
tren->duoi, PPU 32, Point, khong nen) va Tile asset, roi dung lai make_unity_chunks cho RuleTile + chunk.
Chay lai giu nguyen guid/fileID cu (doc lai .meta neu co) -> khong lam gay reference trong scene.
Dung: python Tools/artpipe/v2/graveyard.py flat && python Tools/artpipe/v2/unity_organize.py (goi run() kem prop prefab)
"""
import os, re, shutil, uuid, random

import make_unity_chunks as mu

HERE = mu.HERE
SHEET = "tilesheet_C_graveyard"
SRC = os.path.join(HERE, "out", SHEET + ".png")
TEMPLATE_META = os.path.join(mu.TILES, "tilesheet_A_meadow.png.meta")      # mu.TILES = Art/Tiles/Meadow
TEMPLATE_TILE = os.path.join(mu.TILES, "tilesheet_A_meadow_0.asset")
GTILES = os.path.join(mu.ROOT, "Assets", "_Game", "Art", "Tiles", "Graveyard")


def old_ids(meta_path):
    if not os.path.exists(meta_path): return {}
    return {int(k): int(v) for k, v in re.findall(rf"{SHEET}_(\d+): (-?\d+)", open(meta_path, encoding="utf-8").read())}


def write_sheet_meta():
    png = os.path.join(GTILES, SHEET + ".png")
    shutil.copyfile(SRC, png)
    guid = mu.meta_guid(png) or uuid.uuid4().hex
    keep = old_ids(png + ".meta")
    rnd = random.Random(SHEET)
    ids = {i: keep.get(i) or rnd.randint(-2**31, 2**31 - 1) for i in range(32)}
    t = open(TEMPLATE_META, encoding="utf-8").read()
    t = re.sub(r"guid: [0-9a-f]{32}", f"guid: {guid}", t, count=1)
    # internalID + spriteID cua tung sprite: thay theo ten
    def fix_sprite(m):
        i = int(m.group(1))
        blk = m.group(0)
        blk = re.sub(r"internalID: -?\d+", f"internalID: {ids[i]}", blk)
        blk = re.sub(r"spriteID: [0-9a-f]{32}", f"spriteID: {uuid.UUID(int=rnd.getrandbits(128)).hex}", blk)
        return blk
    t = re.sub(r"name: tilesheet_A_meadow_(\d+)\n[\s\S]*?weights: \[\]", fix_sprite, t)
    t = re.sub(r"(internalIDToNameTable:\n  - first:\n      213: )-?\d+", rf"\g<1>{ids[0]}", t)
    t = re.sub(r"tilesheet_A_meadow_(\d+): -?\d+", lambda m: f"tilesheet_A_meadow_{m.group(1)}: {ids[int(m.group(1))]}", t)
    t = t.replace("tilesheet_A_meadow", SHEET)
    open(png + ".meta", "w", encoding="utf-8", newline="\n").write(t)
    return guid, ids


def write_tiles(guid, ids):
    tpl = open(TEMPLATE_TILE, encoding="utf-8").read()
    for i in range(32):
        name = f"{SHEET}_{i}"
        body = re.sub(r"m_Name: .*", f"m_Name: {name}", tpl)
        body = re.sub(r"m_Sprite: \{[^}]*\}", f"m_Sprite: {{fileID: {ids[i]}, guid: {guid}, type: 3}}", body)
        path = os.path.join(GTILES, name + ".asset")
        open(path, "w", encoding="utf-8", newline="\n").write(body)
        mu.write_meta(path, "NativeFormatImporter:\n  externalObjects: {}\n  mainObjectFileID: 11400000\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n")


def run(props=None):
    """props: [(fileID, guid)] prop prefab cho ChunkView (None = giu cua template)."""
    guid, ids = write_sheet_meta()
    write_tiles(guid, ids)
    mu.SHEET = SHEET
    mu.TILES = GTILES                      # tu day sprite_refs/tile_refs/ruletiles/preview lam viec o thu muc Graveyard
    srefs, trefs = mu.sprite_refs(), mu.tile_refs()
    for k, seed in ((1, 51), (2, 67), (3, 83)):
        g = mu.fill(k, seed)
        mu.write_chunk(f"Graveyard Chunk {k}", g, trefs, srefs, props)
        mu.preview(g, f"graveyard_{k}")
    mu.ruletiles(srefs, "Graveyard")
    return srefs, trefs


if __name__ == "__main__":
    run()
    print("ok: tilesheet_C_graveyard (+32 tile), Graveyard Path/Grass, Graveyard Chunk 1/2/3")
