"""v2 - sinh 2 chunk mau + 2 RuleTile cho map A_meadow, ghi thang YAML vao Assets (khong can editor script).

Dua tren tile asset user da tao: Assets/_Game/Art/TestGeneratedArt/Tiles/tilesheet_A_meadow_<N>.asset
(N = so o trong sheet 8x4, trai->phai, tren->duoi; da kiem tra khop rect cua slice).
- Prefabs/Chunks/Meadow Chunk 1.prefab, Meadow Chunk 2.prefab: nhan ban 'Terrain Chunk 1' (giu props, ChunkView),
  thay lop 'Background Tile' bang 20x20 o: co ngau nhien + mang dat kin ben trong (khong cham mep chunk).
- TestGeneratedArt/Tiles/Meadow Path.asset (RuleTile tu chon o mep/goc), Meadow Grass.asset (RuleTile random co).
Chay lai se ghi de 4 file tren (giu nguyen guid cu neu da co .meta).
Dung: python Tools/artpipe/v2/make_unity_chunks.py  (+ v2/out/chunk_preview_*.png)
"""
import os, re, uuid
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
TILES = os.path.join(ROOT, "Assets", "_Game", "Art", "Tiles", "Meadow")          # sau khi sap xep lai thu muc (unity_organize.py)
CHUNKS = os.path.join(ROOT, "Assets", "_Game", "Prefabs", "Chunks")
TEMPLATE = os.path.join(ROOT, "Assets", "_Game", "Prefabs", "_Archive", "Chunks", "Terrain Chunk 1.prefab")
SHEET = "tilesheet_A_meadow"
RULETILE_GUID = "9d1514134bc4fbd41bb739b1b9a49231"     # com.unity.2d.tilemap.extras RuleTile.cs
N = 20                                                    # chunk 20x20, o tu -10..9

# so o trong sheet (xem v2/out/tilesheet_A_meadow_labeled.png)
NW, N_, NE, W, C, E, SW, S, SE = 0, 1, 2, 8, 9, 10, 16, 17, 18
IN_NW, IN_NE, IN_SW, IN_SE, PATH_V = 3, 4, 11, 12, (19, 20)
GRASS_MAIN = 5
GRASS_COMMON = [13, 21, 6, 24, 27]                        # bui thua, hoa le, bui, soi nho, co+hoa
GRASS_RARE = [7, 14, 15, 26, 30, 22, 28, 23, 31, 25, 29]  # bui day, hoa, cum hoa, nam, mang toi/sang, da, dat trui
GRASS_BIG = {22, 23, 28, 31, 25, 29}                      # o nhieu chi tiet -> khong dat sat nhau


def meta_guid(path):
    m = path + ".meta"
    if os.path.exists(m):
        g = re.search(r"guid: ([0-9a-f]{32})", open(m, encoding="utf-8").read())
        if g: return g.group(1)
    return None


def write_meta(path, importer_block):
    g = meta_guid(path) or uuid.uuid4().hex
    open(path + ".meta", "w", encoding="utf-8", newline="\n").write(
        f"fileFormatVersion: 2\nguid: {g}\n{importer_block}")
    return g


def sprite_refs():
    png = os.path.join(TILES, SHEET + ".png")
    meta = open(png + ".meta", encoding="utf-8").read()
    g = re.search(r"guid: ([0-9a-f]{32})", meta).group(1)
    ids = {int(k): int(v) for k, v in re.findall(rf"{SHEET}_(\d+): (-?\d+)", meta)}
    return {i: f"{{fileID: {fid}, guid: {g}, type: 3}}" for i, fid in ids.items()}


def tile_refs():
    out = {}
    for i in range(32):
        g = meta_guid(os.path.join(TILES, f"{SHEET}_{i}.asset"))
        assert g, f"thieu tile asset {SHEET}_{i}.asset"
        out[i] = f"{{fileID: 11400000, guid: {g}, type: 2}}"
    return out


# ---------------- thiet ke chunk ----------------
# toa do o the gioi (x, y), y huong len. Prop spawn cua Terrain Chunk 1 o: (5,3) (5,-7) (-6,3) (-1,7) (-7,-7)
PROPS = [(5, 3), (5, -7), (-6, 3), (-1, 7), (-7, -7)]


def rect(m, x0, x1, y0, y1):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            m[(x, y)] = True


def design(kind):
    p = {}
    if kind == 1:      # duong dat chu L lon + khoang trong o goc
        rect(p, -8, 2, -1, 0)        # nhanh ngang
        rect(p, 1, 2, -5, 0)         # nhanh doc xuong
        rect(p, -2, 3, -6, -5)       # day chu L mo rong thanh khoang dat
        rect(p, -3, -1, 1, 2)        # bau dat phia tren nhanh ngang
    elif kind == 3:    # duong doc + san dat giua + nhanh ngang sang phai
        rect(p, 1, 2, -8, 5)
        rect(p, -4, 2, -3, 0)
        rect(p, 2, 7, -1, 0)
    else:              # 2 khoang dat roi rac
        rect(p, -6, -3, -3, -1)
        rect(p, -5, -4, -4, -4)
        rect(p, 1, 3, 1, 5)
        rect(p, 2, 4, -1, 1)
        rect(p, 6, 7, -3, -2)
    return p


def validate(p):
    at = lambda x, y: p.get((x, y), False)
    for (x, y) in p:
        assert -9 <= x <= 8 and -9 <= y <= 8, f"duong cham mep chunk o {(x, y)}"
        assert not (not at(x, y + 1) and not at(x, y - 1)), f"duong rong 1 o (doc) tai {(x, y)}"
        assert not (not at(x - 1, y) and not at(x + 1, y)), f"duong rong 1 o (ngang) tai {(x, y)}"
        for px, py in PROPS:
            assert abs(px - x) > 1 or abs(py - y) > 1, f"duong de len prop spawn {(px, py)}"


def pick_path(p, x, y, rng):
    at = lambda dx, dy: p.get((x + dx, y + dy), False)
    n, s, w, e = at(0, 1), at(0, -1), at(-1, 0), at(1, 0)
    col = 0 if not w else (2 if not e else 1)
    row = 0 if not n else (2 if not s else 1)
    t = [[NW, N_, NE], [W, C, E], [SW, S, SE]][row][col]
    if t == C:
        if not at(-1, 1): return IN_NW
        if not at(1, 1): return IN_NE
        if not at(-1, -1): return IN_SW
        if not at(1, -1): return IN_SE
        return [C, C, C, PATH_V[0], PATH_V[1]][int(rng.integers(0, 5))]
    return t


def fill(kind, seed):
    rng = np.random.default_rng(seed)
    p = design(kind); validate(p)
    rare_w = 0.18 if kind == 2 else 0.1
    grid = {}
    for y in range(-10, 10):
        for x in range(-10, 10):
            if p.get((x, y)):
                grid[(x, y)] = pick_path(p, x, y, rng); continue
            r = rng.random()
            if r < 1 - rare_w - 0.3: t = GRASS_MAIN
            elif r < 1 - rare_w: t = GRASS_COMMON[int(rng.integers(0, len(GRASS_COMMON)))]
            else:
                t = GRASS_RARE[int(rng.integers(0, len(GRASS_RARE)))]
                near = [grid.get((x + dx, y + dy)) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
                if t in GRASS_BIG and any(v in GRASS_BIG for v in near): t = GRASS_MAIN
            grid[(x, y)] = t
    return grid


def preview(grid, name):
    sheet = Image.open(os.path.join(TILES, SHEET + ".png")).convert("RGB")
    im = Image.new("RGB", (N * 32, N * 32))
    for (x, y), t in grid.items():
        tile = sheet.crop(((t % 8) * 32, (t // 8) * 32, (t % 8 + 1) * 32, (t // 8 + 1) * 32))
        im.paste(tile, ((x + 10) * 32, (9 - y) * 32))
    for px, py in PROPS:   # danh dau prop spawn
        cx, cy = (px + 10) * 32 + 16, (9 - py) * 32 + 16
        for d in range(-4, 5): im.putpixel((cx + d, cy), (255, 60, 60)); im.putpixel((cx, cy + d), (255, 60, 60))
    im.save(os.path.join(HERE, "out", f"chunk_preview_{name}.png"))


# ---------------- ghi YAML ----------------
def tilemap_yaml(grid, trefs, srefs):
    used = sorted(set(grid.values()))
    idx = {t: i for i, t in enumerate(used)}
    cells = []
    for y in range(-10, 10):
        for x in range(-10, 10):
            i = idx[grid[(x, y)]]
            cells.append(f"""  - first: {{x: {x}, y: {y}, z: 0}}
    second:
      serializedVersion: 2
      m_TileIndex: {i}
      m_TileSpriteIndex: {i}
      m_TileMatrixIndex: 0
      m_TileColorIndex: 0
      m_TileObjectToInstantiateIndex: 65535
      dummyAlignment: 0
      m_AllTileFlags: 1073741825""")
    cnt = {t: sum(1 for v in grid.values() if v == t) for t in used}
    assets = "\n".join(f"  - m_RefCount: {cnt[t]}\n    m_Data: {trefs[t]}" for t in used)
    sprites = "\n".join(f"  - m_RefCount: {cnt[t]}\n    m_Data: {srefs[t]}" for t in used)
    return "\n".join(cells), assets, sprites


def write_chunk(name, grid, trefs, srefs, props=None):
    t = open(TEMPLATE, encoding="utf-8").read()
    cells, assets, sprites = tilemap_yaml(grid, trefs, srefs)
    # chi sua Tilemap cua 'Background Tile' (template chi co 1 Tilemap)
    t, k1 = re.subn(r"(  m_Tiles:\n)[\s\S]*?(\n  m_AnimatedTiles:)", lambda m: m.group(1) + cells + m.group(2), t)
    t, k2 = re.subn(r"(  m_TileAssetArray:\n)[\s\S]*?(\n  m_TileSpriteArray:)", lambda m: m.group(1) + assets + m.group(2), t)
    t, k3 = re.subn(r"(  m_TileSpriteArray:\n)[\s\S]*?(\n  m_TileMatrixArray:)", lambda m: m.group(1) + sprites + m.group(2), t)
    t = re.sub(r"(m_TileMatrixArray:\n  - m_RefCount: )\d+", rf"\g<1>{N * N}", t)
    t = re.sub(r"(m_TileColorArray:\n  - m_RefCount: )\d+", rf"\g<1>{N * N}", t)
    t, k4 = re.subn(r"m_Origin: \{x: -?\d+, y: -?\d+, z: 0\}\n  m_Size: \{x: \d+, y: \d+, z: 1\}",
                    "m_Origin: {x: -10, y: -10, z: 0}\n  m_Size: {x: 20, y: 20, z: 1}", t)
    t, k5 = re.subn(r"m_Name: Terrain Chunk 1\n", f"m_Name: {name}\n", t)
    assert (k1, k2, k3, k4, k5) == (1, 1, 1, 1, 1), (k1, k2, k3, k4, k5)
    if props:          # thay danh sach propPrefabs cua ChunkView: [(fileID GameObject goc, guid prefab)]
        lst = "\n".join(f"  - {{fileID: {fid}, guid: {g}, type: 3}}" for fid, g in props)
        t, k6 = re.subn(r"(  propPrefabs:\n)(  - \{[^\n]*\n)+", lambda m: m.group(1) + lst + "\n", t)
        assert k6 == 1, k6
    path = os.path.join(CHUNKS, name + ".prefab")
    open(path, "w", encoding="utf-8", newline="\n").write(t)
    write_meta(path, "PrefabImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n")


def rule(rid, sprites, neighbors, output=0, perlin=0.5):
    """neighbors: [(dx, dy, 1=This|2=NotThis)]"""
    hexs = "".join(f"{v:02x}000000" for _, _, v in neighbors)
    pos = "\n".join(f"    - {{x: {dx}, y: {dy}, z: 0}}" for dx, dy, _ in neighbors)
    spr = "\n".join(f"    - {s}" for s in sprites)
    return f"""  - m_Id: {rid}
    m_Sprites:
{spr}
    m_GameObject: {{fileID: 0}}
    m_MinAnimationSpeed: 1
    m_MaxAnimationSpeed: 1
    m_PerlinScale: {perlin}
    m_Output: {output}
    m_ColliderType: 1
    m_RandomTransform: 0
    m_Neighbors: {hexs}
    m_NeighborPositions:{(chr(10) + pos) if pos else ' []'}
    m_RuleTransform: 0"""


def write_ruletile(name, default, rules):
    body = f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!114 &11400000
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 0}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 11500000, guid: {RULETILE_GUID}, type: 3}}
  m_Name: {name}
  m_EditorClassIdentifier:
  m_DefaultSprite: {default}
  m_DefaultGameObject: {{fileID: 0}}
  m_DefaultColliderType: 1
  m_TilingRules:
{chr(10).join(rules)}
"""
    path = os.path.join(TILES, name + ".asset")
    open(path, "w", encoding="utf-8", newline="\n").write(body)
    write_meta(path, "NativeFormatImporter:\n  externalObjects: {}\n  mainObjectFileID: 11400000\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n")


def ruletiles(srefs, prefix="Meadow"):
    T, X = 1, 2
    Nn, Ss, Ww, Ee = (0, 1), (0, -1), (-1, 0), (1, 0)
    nb = lambda **k: [(*d, v) for d, v in k["l"]]
    rules = [
        rule(0, [srefs[NW]], nb(l=[(Nn, X), (Ww, X), (Ee, T), (Ss, T)])),
        rule(1, [srefs[NE]], nb(l=[(Nn, X), (Ee, X), (Ww, T), (Ss, T)])),
        rule(2, [srefs[SW]], nb(l=[(Ss, X), (Ww, X), (Ee, T), (Nn, T)])),
        rule(3, [srefs[SE]], nb(l=[(Ss, X), (Ee, X), (Ww, T), (Nn, T)])),
        rule(4, [srefs[N_]], nb(l=[(Nn, X), (Ww, T), (Ee, T), (Ss, T)])),
        rule(5, [srefs[S]], nb(l=[(Ss, X), (Ww, T), (Ee, T), (Nn, T)])),
        rule(6, [srefs[W]], nb(l=[(Ww, X), (Nn, T), (Ss, T), (Ee, T)])),
        rule(7, [srefs[E]], nb(l=[(Ee, X), (Nn, T), (Ss, T), (Ww, T)])),
        rule(8, [srefs[IN_NW]], nb(l=[(Nn, T), (Ww, T), ((-1, 1), X)])),
        rule(9, [srefs[IN_NE]], nb(l=[(Nn, T), (Ee, T), ((1, 1), X)])),
        rule(10, [srefs[IN_SW]], nb(l=[(Ss, T), (Ww, T), ((-1, -1), X)])),
        rule(11, [srefs[IN_SE]], nb(l=[(Ss, T), (Ee, T), ((1, -1), X)])),
        rule(12, [srefs[PATH_V[0]], srefs[C], srefs[C], srefs[C], srefs[PATH_V[1]]], [], output=1, perlin=0.42),
    ]
    write_ruletile(f"{prefix} Path", srefs[C], rules)
    # co: Random theo Perlin -> gia tri tap trung giua danh sach => dat co tron o giua, bien the ra 2 dau
    grass = [srefs[t] for t in [29, 25, 22, 23] + GRASS_COMMON[:2] + [GRASS_MAIN] * 8 + GRASS_COMMON[2:] + [7, 14, 15, 26, 28, 30, 31]]
    write_ruletile(f"{prefix} Grass", srefs[GRASS_MAIN], [rule(0, grass, [], output=1, perlin=0.42)])


if __name__ == "__main__":
    srefs, trefs = sprite_refs(), tile_refs()
    for k, seed in ((1, 21), (2, 37)):
        g = fill(k, seed)
        write_chunk(f"Meadow Chunk {k}", g, trefs, srefs)
        preview(g, f"meadow_{k}")
    ruletiles(srefs)
    print("ok: Meadow Chunk 1/2 (Prefabs/Chunks), Meadow Path + Meadow Grass (TestGeneratedArt/Tiles)")
