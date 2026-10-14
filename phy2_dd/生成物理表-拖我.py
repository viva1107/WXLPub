#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 拖放生成 WXLEquipPlusPhysics.phy2
# 用法: 把 backport 套件工程文件夹拖到本脚本(或打包后的EXE)上
# 前提: 本程序旁边必须有 tools 文件夹, 里面放 equip-plus 的
#       physics_table.py 和 backport_to_equipplus.py
import os
import sys
import traceback

def main():
    try:
        if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
            print("用法: 把套件工程文件夹(work folder)拖到本程序图标上")
            print("      (kit 工程 = 包含 bp.json / build\manifest.json 的那个目录)")
            input("按回车退出...")
            return 1

        work = os.path.abspath(sys.argv[1])
        tools = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "tools")
        if not os.path.isdir(tools):
            print("找不到 tools 文件夹, 它必须和本程序放在一起:")
            print("  " + tools)
            input("按回车退出...")
            return 1

        sys.path.insert(0, tools)
        import physics_table   # 来自 equip-plus/tools

        print("工程目录:", work)
        print("生成中... (需要读取零售文件缓存, 模型多的话要等一会儿)")
        physics_table.main(["--work", work])   # 输出 <work>\out\WXLEquipPlusPhysics.phy2
        print()
        print("完成! 文件在: " + os.path.join(work, "out", "WXLEquipPlusPhysics.phy2"))
        print("把它拷到客户端 DBFilesClient\ 下即可")
    except Exception:
        print("出错了:")
        traceback.print_exc()
    input("按回车退出...")
    return 0

if __name__ == "__main__":
    sys.exit(main())
