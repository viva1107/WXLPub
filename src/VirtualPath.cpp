// wxl-physics (physics-only cut): WxlIniGetBool, replicating equip-plus's own ini resolution:
// the ini lives next to THIS DLL (i.e. Extensions\wxl-physics\WXLExtendedEquipment.ini),
// not in the game folder. Same code path as the original ResolveIniPath.
#include "VirtualPath.hpp"
#define WIN32_LEAN_AND_MEAN
#include <windows.h>

#include <cstddef>
#include <cstring>

namespace wxl::scripts::equipextension
{
    namespace
    {
        bool ResolveIniPath(char* outIniPath, size_t outIniPathSz)
        {
            HMODULE hMod = nullptr;
            if (!GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
                                     GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                     reinterpret_cast<LPCSTR>(&ResolveIniPath), &hMod) || !hMod)
                return false;

            char dllPath[MAX_PATH] = {};
            const DWORD n = GetModuleFileNameA(hMod, dllPath, sizeof(dllPath));
            if (n == 0 || n >= sizeof(dllPath)) return false;

            const char* lastSlash = std::strrchr(dllPath, '\\');
            const char* kIniName = "WXLExtendedEquipment.ini";
            if (lastSlash)
            {
                const size_t dirLen = static_cast<size_t>(lastSlash - dllPath) + 1;
                if (dirLen + std::strlen(kIniName) >= outIniPathSz) return false;
                std::memcpy(outIniPath, dllPath, dirLen);
                std::strcpy(outIniPath + dirLen, kIniName);
            }
            else
            {
                if (std::strlen(kIniName) >= outIniPathSz) return false;
                std::strcpy(outIniPath, kIniName);
            }
            return true;
        }
    }

    bool WxlIniGetBool(const char* section, const char* key, bool defaultValue)
    {
        if (!section || !key) return defaultValue;

        char iniPath[MAX_PATH] = {};
        if (!ResolveIniPath(iniPath, sizeof(iniPath))) return defaultValue;

        return GetPrivateProfileIntA(section, key, defaultValue ? 1 : 0, iniPath) != 0;
    }
}
