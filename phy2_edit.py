#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# phy2_edit.py - WXLEquipPlusPhysics.phy2 编辑器 (phy2 <-> JSON 双向转换)
#
#   解码:  python phy2_edit.py decode  xxx.phy2  xxx.json
#   编码:  python phy2_edit.py encode  xxx.json  xxx.phy2
#
# 工作流: decode 出 json -> 用记事本改数值 -> encode 回 phy2 -> 拷回客户端 -> 游戏 Reload
# 纯标准库。建议每次改动前备份原 .phy2。
import json
import struct
import sys

# ---------------- PHY2 读写 ----------------

def read_row(buf, off):
    klen, = struct.unpack_from("<H", buf, off)
    key = buf[off + 2:off + 2 + klen].decode("latin-1")
    o = off + 2 + klen
    o += -o % 4
    nb, ns, nj, nh = struct.unpack_from("<4B", buf, o)
    o += 4
    bodies = []
    for _ in range(nb):
        t, _pad, bone, px, py, pz, grav, inertia, lin, ang, carry, grp, _ = \
            struct.unpack_from("<BBH3f5fHH", buf, o)
        o += 40
        bodies.append({"type": t, "bone": bone, "pos": [px, py, pz],
                       "gravity": grav, "inertia": inertia,
                       "lin_damp": lin, "ang_damp": ang, "carry": carry, "group": grp})
    shapes = []
    for _ in range(ns):
        body, t, hull, fric, rest, dens, ax, ay, az, bx, by, bz, r = \
            struct.unpack_from("<BBH3f3f3ff", buf, o)
        o += 44
        shapes.append({"body": body, "type": t, "hull": hull,
                       "friction": fric, "restitution": rest, "density": dens,
                       "a": [ax, ay, az], "b": [bx, by, bz], "radius": r})
    joints = []
    for _ in range(nj):
        t, a, b, mode = struct.unpack_from("<BBBb", buf, o)
        v = struct.unpack_from("<3f3f9f9f6f", buf, o + 4)
        o += 124
        joints.append({"type": t, "body_a": a, "body_b": b, "mode": mode,
                       "anchor_a": list(v[0:3]), "anchor_b": list(v[3:6]),
                       "axis_a": list(v[6:15]), "axis_b": list(v[15:24]),
                       "limits": list(v[24:30])})
    hulls = []
    for _ in range(nh):
        nv, nf, ne, _ = struct.unpack_from("<4B", buf, o)
        centroid = list(struct.unpack_from("<3f", buf, o + 4))
        volume, area = struct.unpack_from("<ff", buf, o + 16)
        o += 24
        verts = [list(struct.unpack_from("<3f", buf, o + 12 * k)) for k in range(nv)]
        o += 12 * nv
        planes = [list(struct.unpack_from("<4f", buf, o + 16 * k)) for k in range(nf)]
        o += 16 * nf
        face = list(buf[o:o + nf]); o += nf
        edge = list(buf[o:o + ne * 4]); o += ne * 4
        o += -o % 4
        hulls.append({"verts": verts, "planes": planes,
                      "face": face, "edge": edge,
                      "centroid": centroid, "volume": volume, "area": area})
    return key, {"bodies": bodies, "shapes": shapes, "joints": joints, "hulls": hulls}


def write_row(key, p):
    out = bytearray()
    kb = key.encode("latin-1")
    out += struct.pack("<H", len(kb)) + kb
    while len(out) % 4:
        out.append(0)
    b, s, j, h = p["bodies"], p["shapes"], p["joints"], p["hulls"]
    out += struct.pack("<4B", len(b), len(s), len(j), len(h))
    for x in b:
        out += struct.pack("<BBH3f5fHH", int(x["type"]), 0, int(x["bone"]),
                           *map(float, x["pos"]), float(x["gravity"]), float(x["inertia"]),
                           float(x["lin_damp"]), float(x["ang_damp"]), float(x["carry"]),
                           int(x["group"]), 0)
    for x in s:
        out += struct.pack("<BBH3f3f3ff", int(x["body"]), int(x["type"]), int(x["hull"]),
                           float(x["friction"]), float(x["restitution"]), float(x["density"]),
                           *map(float, x["a"]), *map(float, x["b"]), float(x["radius"]))
    for x in j:
        out += struct.pack("<BBBb3f3f9f9f6f", int(x["type"]), int(x["body_a"]),
                           int(x["body_b"]), int(x["mode"]),
                           *map(float, x["anchor_a"]), *map(float, x["anchor_b"]),
                           *map(float, x["axis_a"]), *map(float, x["axis_b"]),
                           *map(float, x["limits"]))
    for x in h:
        v, pl = x["verts"], x["planes"]
        face, edge = bytes(x["face"]), bytes(x["edge"])
        out += struct.pack("<4B3fff", len(v), len(pl), len(edge) // 4, 0,
                           *map(float, x["centroid"]), float(x["volume"]), float(x["area"]))
        for vv in v:
            out += struct.pack("<3f", *map(float, vv))
        for pp in pl:
            out += struct.pack("<4f", *map(float, pp))
        out += face + edge
        while len(out) % 4:
            out.append(0)
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def fnv1a(s):
    h = 0x811C9DC5
    for c in s.encode("latin-1"):
        h = ((h ^ c) * 0x01000193) & 0xFFFFFFFF
    return h


def decode(phy2_path, json_path):
    buf = open(phy2_path, "rb").read()
    if buf[:4] != b"PHY2":
        raise SystemExit("不是 PHY2 文件")
    count, = struct.unpack_from("<I", buf, 4)
    rows = []
    for i in range(count):
        _h, off = struct.unpack_from("<II", buf, 8 + 8 * i)
        key, p = read_row(buf, off)
        p["key"] = key
        rows.append(p)
    doc = {"_format": "wxl-physics phy2 v1", "rows": rows}
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    print("decoded %d rows -> %s" % (count, json_path))
    print("用记事本/VSCode 编辑后, 再 encode 回 phy2")


def encode(json_path, phy2_path):
    doc = json.load(open(json_path, "r", encoding="utf-8"))
    rows = doc["rows"] if isinstance(doc, dict) and "rows" in doc else doc
    body = bytearray()
    index = []
    for p in rows:
        key = p["key"]
        blob = write_row(key, p)
        index.append((fnv1a(key), 8 + 8 * len(rows) + len(body)))
        body += blob
    index.sort(key=lambda t: (t[0],))
    out = bytearray(b"PHY2" + struct.pack("<I", len(rows)))
    for h, off in index:
        out += struct.pack("<II", h, off)
    out += body
    with open(phy2_path, "wb") as f:
        f.write(out)
    print("encoded %d rows -> %s (%d bytes)" % (len(rows), phy2_path, len(out)))


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("decode", "encode"):
        print(__doc__)
        input("按回车退出...")
        return 1
    if sys.argv[1] == "decode":
        decode(sys.argv[2], sys.argv[3])
    else:
        encode(sys.argv[2], sys.argv[3])
    input("按回车退出...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
