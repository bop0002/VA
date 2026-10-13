"""v2 - sap xep lai Assets/_Game/Art + Prefabs, dua asset moi vao Unity, tao prefab prop + 3 Graveyard Chunk + Tile Palette.

Chi chay khi Unity DONG. Moi file di kem .meta -> guid giu nguyen, reference trong scene/prefab khong gay.
Chay lai an toan: buoc nao da xong thi bo qua (file nguon khong con), asset moi giu guid cu neu da co .meta.

Cau truc dich:
  Art/Characters (+Animation)  Art/Enemies  Art/Projectiles  Art/Props/Graveyard  Art/FX/Shadows
  Art/Tiles/Graveyard (sheet, 32 tile, RuleTile, Graveyard Palette)  Art/Tiles/Meadow  Art/_Archive (do cu)
  Prefabs/Props/Graveyard (15 prop)  Prefabs/Chunks (Graveyard Chunk 1..3)  Prefabs/_Archive (chunk/prop cu)
Dung: python Tools/artpipe/v2/unity_organize.py
"""
import os, re, shutil, uuid, random
import numpy as np
from PIL import Image

import make_unity_chunks as mu

HERE = mu.HERE
GAME = os.path.join(mu.ROOT, "Assets", "_Game")
ART, PREF = os.path.join(GAME, "Art"), os.path.join(GAME, "Prefabs")
TGA = os.path.join(ART, "TestGeneratedArt")
SOFT = os.path.join(HERE, "export_soft")
log = []


# ---------------- tien ich ----------------
def folder(path):
    """Tao thu muc + .meta thu muc (guid on dinh) neu chua co."""
    parent = os.path.dirname(path)
    if parent != GAME and not os.path.isdir(parent):
        folder(parent)                                      # tao ca cac cap cha (kem .meta)
    os.makedirs(path, exist_ok=True)
    if not os.path.exists(path + ".meta"):
        open(path + ".meta", "w", encoding="utf-8", newline="\n").write(
            f"fileFormatVersion: 2\nguid: {uuid.uuid4().hex}\nfolderAsset: yes\nDefaultImporter:\n"
            "  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n")


def move(src, dst_dir):
    """Chuyen file/thu muc + .meta vao dst_dir (bo qua neu nguon khong con)."""
    if not os.path.exists(src): return
    folder(dst_dir)
    dst = os.path.join(dst_dir, os.path.basename(src))
    assert not os.path.exists(dst), f"da co {dst}"
    shutil.move(src, dst)
    if os.path.exists(src + ".meta"): shutil.move(src + ".meta", dst + ".meta")
    log.append(f"move {os.path.relpath(src, GAME)} -> {os.path.relpath(dst_dir, GAME)}")


def move_glob(src_dir, dst_dir, pred):
    if not os.path.isdir(src_dir): return
    for f in sorted(os.listdir(src_dir)):
        if f.endswith(".meta"): continue
        if pred(f): move(os.path.join(src_dir, f), dst_dir)


def rm_empty(path):
    """Xoa thu muc rong (chi con .meta cua chinh no) + .meta."""
    if os.path.isdir(path):
        for d in os.listdir(path):
            if os.path.isdir(os.path.join(path, d)): rm_empty(os.path.join(path, d))
        if not [f for f in os.listdir(path)]:
            os.rmdir(path)
            if os.path.exists(path + ".meta"): os.remove(path + ".meta")
            log.append(f"xoa thu muc rong {os.path.relpath(path, GAME)}")


def rid(*key):
    """fileID on dinh theo ten (chay lai khong doi)."""
    return random.Random("/".join(map(str, key))).randint(10 ** 17, 9 * 10 ** 18)


# ---------------- 1. sap xep ----------------
def organize():
    move_glob(os.path.join(TGA, "Characters"), os.path.join(ART, "Characters"), lambda f: True)
    move(os.path.join(TGA, "Animation"), os.path.join(ART, "Characters"))
    move_glob(os.path.join(TGA, "Enemies"), os.path.join(ART, "Enemies"), lambda f: True)
    move_glob(os.path.join(TGA, "Projectiles"), os.path.join(ART, "Projectiles"), lambda f: True)
    tiles = os.path.join(TGA, "Tiles")
    move_glob(tiles, os.path.join(ART, "Tiles", "Graveyard"), lambda f: "graveyard" in f.lower())
    move_glob(tiles, os.path.join(ART, "Tiles", "Meadow"), lambda f: "meadow" in f.lower())
    arch = os.path.join(ART, "_Archive")
    move(os.path.join(TGA, "Decor"), os.path.join(arch, "TestGeneratedArt"))
    move(os.path.join(TGA, "Props"), os.path.join(arch, "TestGeneratedArt"))
    move(os.path.join(ART, "Sprites"), arch)
    move(os.path.join(ART, "Animations"), arch)
    parch = os.path.join(PREF, "_Archive")
    move_glob(os.path.join(PREF, "Chunks"), os.path.join(parch, "Chunks"),
              lambda f: f.startswith(("Terrain Chunk", "Meadow Chunk")))
    move(os.path.join(PREF, "Props", "terrain_10.prefab"), os.path.join(parch, "Props"))
    rm_empty(TGA)


# ---------------- 2. anh moi + import setting ----------------
def sprite_meta(png, pivot):
    """Meta sprite don (Single), PPU 32, Point, khong nen. pivot: 'bottom' | 'center'. Tham chieu: fileID 21300000."""
    tpl = open(os.path.join(ART, "Projectiles", "proj_wand.png.meta"), encoding="utf-8").read()
    g = mu.meta_guid(png) or uuid.uuid4().hex
    t = re.sub(r"guid: [0-9a-f]{32}", f"guid: {g}", tpl, count=1)
    t = re.sub(r"  internalIDToNameTable:\n(  - first:\n      213: -?\d+\n    second: .*\n)+", "  internalIDToNameTable: []\n", t)
    t = re.sub(r"(  spriteSheet:\n    serializedVersion: 2\n    sprites:)\n[\s\S]*?\n(    outline: \[\])", r"\1 []\n\2", t)
    t = re.sub(r"    nameFileIdTable:\n(      .*\n)+", "    nameFileIdTable: {}\n", t)
    al, pv = (7, "{x: 0.5, y: 0}") if pivot == "bottom" else (0, "{x: 0.5, y: 0.5}")
    t = re.sub(r"\n  alignment: \d+\n  spritePivot: \{[^}]*\}", f"\n  alignment: {al}\n  spritePivot: {pv}", t)
    assert "sprites: []" in t and "nameFileIdTable: {}" in t
    open(png + ".meta", "w", encoding="utf-8", newline="\n").write(t)
    return g


def import_pngs():
    out = {}
    pdir = os.path.join(ART, "Props", "Graveyard"); folder(pdir)
    for f in sorted(os.listdir(os.path.join(SOFT, "Props_Graveyard"))):
        dst = os.path.join(pdir, f)
        shutil.copyfile(os.path.join(SOFT, "Props_Graveyard", f), dst)
        out[f[:-4]] = sprite_meta(dst, "bottom")
    sdir = os.path.join(ART, "FX", "Shadows"); folder(sdir)
    for f in sorted(os.listdir(os.path.join(SOFT, "Shadows"))):
        dst = os.path.join(sdir, f)
        shutil.copyfile(os.path.join(SOFT, "Shadows", f), dst)
        sprite_meta(dst, "center")
    log.append(f"import {len(out)} prop png + shadows")
    return out


# ---------------- 3. prefab prop ----------------
# ten prefab -> (anh, collider: None | (rong px, cao px))  ; collider o chan (pivot day)
PROPS = {
    "tomb_round": ("tomb_round", (18, 6)), "tomb_tall": ("tomb_tall", (16, 6)), "tomb_broken": ("tomb_broken", (18, 6)),
    "cross_stone": ("cross_stone", (12, 5)), "cross_wood": ("cross_wood", (6, 4)),
    "fence": ("fence", (32, 5)), "fence_post": ("fence_post", (6, 5)),
    "torch": ("torch_0", (6, 4)), "lantern": ("lantern", (8, 4)),
    "tree_dead": ("tree_dead", (14, 7)), "tree_face": ("tree_face", (14, 7)),
    "rock_big": ("rock_big", (24, 10)), "rock_small": ("rock_small", (14, 7)),
    "bush_dead": ("bush_dead", None), "skull_pile": ("skull_pile", None),
}
# danh sach ngau nhien cho ChunkView (lap lai = hay gap hon); khong co rao (rao dat tay)
CHUNK_PROPS = ["tomb_round", "tomb_round", "tomb_tall", "tomb_tall", "tomb_broken", "cross_stone", "cross_wood",
               "tree_dead", "tree_face", "rock_big", "rock_small", "bush_dead", "skull_pile", "torch", "lantern"]


def make_prefabs(sprites):
    tpl = open(os.path.join(PREF, "_Archive", "Props", "terrain_10.prefab"), encoding="utf-8").read()
    old = {"go": "8437162951004939857", "tr": "7247966013942417563", "sr": "8568401674341350798", "bc": "8383087403750647349"}
    d = os.path.join(PREF, "Props", "Graveyard"); folder(d)
    refs = {}
    for name, (img, col) in PROPS.items():
        ids = {k: str(rid("prop", name, k)) for k in old}
        t = tpl
        for k, v in old.items(): t = t.replace(v, ids[k])
        t = t.replace("m_Name: terrain_10", f"m_Name: {name}")
        t = re.sub(r"m_Sprite: \{[^}]*\}", f"m_Sprite: {{fileID: 21300000, guid: {sprites[img]}, type: 3}}", t)
        t = t.replace("m_SpriteSortPoint: 0", "m_SpriteSortPoint: 1")          # sap xep theo chan (pivot)
        if col:
            w, h = col[0] / 32, col[1] / 32
            t = re.sub(r"  m_Offset: \{x: 0, y: 0\}", f"  m_Offset: {{x: 0, y: {h / 2:.4f}}}", t)
            t = re.sub(r"  m_Size: \{x: 1, y: 1\}\n  m_EdgeRadius", f"  m_Size: {{x: {w:.4f}, y: {h:.4f}}}\n  m_EdgeRadius", t)
        else:                                                                 # vat trang tri di xuyen qua
            t = re.sub(r"(BoxCollider2D:\n(?:  .*\n)*?  m_Enabled: )1", r"\g<1>0", t)
        path = os.path.join(d, name + ".prefab")
        open(path, "w", encoding="utf-8", newline="\n").write(t)
        g = mu.write_meta(path, "PrefabImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n")
        refs[name] = (ids["go"], g)
    log.append(f"tao {len(refs)} prefab prop")
    return refs


# ---------------- 4. tile palette ----------------
def palette(srefs, trefs):
    gdir = os.path.join(ART, "Tiles", "Graveyard")
    tpl = open(os.path.join(ART, "_Archive", "Sprites", "Pallets", "Background Pallet.prefab"), encoding="utf-8").read()
    cells = [((i % 8, 3 - i // 8), trefs[i], srefs[i]) for i in range(32)]
    for x, (rt, spr) in enumerate((("Graveyard Path", srefs[9]), ("Graveyard Grass", srefs[5]))):
        g = mu.meta_guid(os.path.join(gdir, rt + ".asset"))
        cells.append(((x, -2), f"{{fileID: 11400000, guid: {g}, type: 2}}", spr))
    tiles, sprs = [], []
    for _, t, s in cells:
        if t not in tiles: tiles.append(t)
        if s not in sprs: sprs.append(s)
    body = "\n".join(f"""  - first: {{x: {x}, y: {y}, z: 0}}
    second:
      serializedVersion: 2
      m_TileIndex: {tiles.index(t)}
      m_TileSpriteIndex: {sprs.index(s)}
      m_TileMatrixIndex: 0
      m_TileColorIndex: 0
      m_TileObjectToInstantiateIndex: 65535
      dummyAlignment: 0
      m_AllTileFlags: 1073741825""" for (x, y), t, s in cells)
    ta = "\n".join(f"  - m_RefCount: {sum(c[1] == t for c in cells)}\n    m_Data: {t}" for t in tiles)
    sa = "\n".join(f"  - m_RefCount: {sum(c[2] == s for c in cells)}\n    m_Data: {s}" for s in sprs)
    n = len(cells)
    t = tpl
    t, k1 = re.subn(r"(  m_Tiles:\n)[\s\S]*?(\n  m_AnimatedTiles:)", lambda m: m.group(1) + body + m.group(2), t)
    t, k2 = re.subn(r"(  m_TileAssetArray:\n)[\s\S]*?(\n  m_TileSpriteArray:)", lambda m: m.group(1) + ta + m.group(2), t)
    t, k3 = re.subn(r"(  m_TileSpriteArray:\n)[\s\S]*?(\n  m_TileMatrixArray:)", lambda m: m.group(1) + sa + m.group(2), t)
    t = re.sub(r"(m_TileMatrixArray:\n  - m_RefCount: )\d+", rf"\g<1>{n}", t)
    t = re.sub(r"(m_TileColorArray:\n  - m_RefCount: )\d+", rf"\g<1>{n}", t)
    t = t.replace("m_Origin: {x: 0, y: 0, z: 0}\n  m_Size: {x: 3, y: 1, z: 1}", "m_Origin: {x: 0, y: -2, z: 0}\n  m_Size: {x: 8, y: 6, z: 1}")
    t = t.replace("m_Name: Background Pallet", "m_Name: Graveyard Palette")
    assert (k1, k2, k3) == (1, 1, 1) and "m_Size: {x: 8, y: 6" in t
    path = os.path.join(gdir, "Graveyard Palette.prefab")
    open(path, "w", encoding="utf-8", newline="\n").write(t)
    mu.write_meta(path, "PrefabImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n")
    log.append("tao Graveyard Palette")


if __name__ == "__main__":
    organize()
    sprites = import_pngs()
    refs = make_prefabs(sprites)
    import make_unity_graveyard as mg
    srefs, trefs = mg.run([refs[k] for k in CHUNK_PROPS])
    log.append("ghi Graveyard Chunk 1/2/3 + RuleTile + 32 tile")
    palette(srefs, trefs)
    print("\n".join(log))
