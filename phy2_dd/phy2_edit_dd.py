#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# phy2_edit_dd.py - 拖放版 phy2 编辑器 (EXE 打包用)
# 拖 .phy2 到本程序 -> 在同目录生成 .json
# 拖 .json 到本程序 -> 在同目录生成 .phy2
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[0])))
from phy2_edit import decode, encode


def main():
    if len(sys.argv) < 2:
        print("用法: 把 .phy2 或 .json 文件拖到本程序上")
        input("按回车退出...")
        return 1
    path = sys.argv[1]
    base, ext = os.path.splitext(path)
    ext = ext.lower()
    try:
        if ext == ".phy2":
            out = base + ".json"
            decode(path, out)
            print("已生成 %s - 用记事本改完数值后, 再把它拖回本程序" % out)
        elif ext == ".json":
            out = base + ".phy2"
            encode(path, out)
            print("已生成 %s - 拷到客户端 Data\\DBFilesClient\\ 后游戏内 Reload" % out)
        else:
            print("只认识 .phy2 和 .json 文件")
    except Exception as e:
        print("出错了: %s" % e)
    input("按回车退出...")
    return 0


if __name__ == "__main__":
    sys.exit(main())
