// wxl-physics: physics-only extension cut from wxl-equip-plus.
// Keeps PhysicsLive + physics_domino; drops equip/creature/weapon/virtual-path machinery.

#include "PhysicsLive.hpp"
#include "WxlOffsets.hpp"
#include "wxl/PluginApi.h"

#include <windows.h>
#include <cstdint>
#include <cstdio>

namespace wxl::scripts::equipextension
{
    static const WXL_Api* g_api = nullptr;
    static offsets::m2hooks::BuildBonePaletteFn g_origBuildBonePalette = nullptr;

    void __fastcall BuildBonePaletteDetour(void* renderCtx, void* edx,
        void* sa1, void* sa2, void* sa3, uint32_t sa4, uint32_t sa5)
    {
        g_origBuildBonePalette(renderCtx, edx, sa1, sa2, sa3, sa4, sa5);
        physics_live::AfterBonePalette(renderCtx);
    }

    static void PhysicsLogLine(const char* text)
    {
        if (g_api && text) g_api->Log(WXL_LOG_INFO, "wxl-physics", text);
    }

    static void __cdecl PhysicsPanel(void* user)
    {
        const WXL_Api* api = static_cast<const WXL_Api*>(user);
        int on = physics_live::Enabled() ? 1 : 0;
        if (api->UiCheckbox("Live physics (plumes, ribbons, chains)", &on))
            physics_live::SetEnabled(on != 0);

        const physics_live::Stats ps = physics_live::GetStats();
        char line[160];
        std::snprintf(line, sizeof line, "Table: %u pieces; simulating %u now", ps.tableRows, ps.live);
        api->UiText(line);
        std::snprintf(line, sizeof line, "Steps: %u | faults: %u | dropped: %u", ps.steps, ps.faults, ps.dropped);
        api->UiText(line);
        std::snprintf(line, sizeof line, "Frame: %.3f ms (worst %.3f ms)", ps.lastFrameMs, ps.worstFrameMs);
        api->UiText(line);

        if (api->UiButton("Reload physics table"))
            physics_live::ReloadTable();
    }
}

extern "C"
{
    const WXL_PluginInfo* __cdecl WXL_Query(void)
    {
        static const WXL_PluginInfo info = {
            sizeof(WXL_PluginInfo), WXL_API_VERSION, "wxl-physics", 1, WXL_CLIENT_BUILD,
        };
        return &info;
    }

    int __cdecl WXL_Load(const WXL_Api* api)
    {
        if (!api || api->apiVersion != WXL_API_VERSION)
            return 0;

        using namespace wxl::scripts::equipextension;
        g_api = api;

        if (!api->HookAttach("wxl-physics:BuildBonePalette",
                             offsets::m2hooks::kBuildBonePalette,
                             reinterpret_cast<void*>(&BuildBonePaletteDetour),
                             reinterpret_cast<void**>(&g_origBuildBonePalette),
                             WXL_HOOK_DEFAULT_PRIORITY))
        {
            api->Log(WXL_LOG_ERROR, "wxl-physics", "BuildBonePalette hook failed");
            return 0;
        }

        physics_live::SetLogger(&PhysicsLogLine);
        physics_live::Init();
        physics_live::LoadTable();

        api->UiAddPanel("Physics", &PhysicsPanel, const_cast<WXL_Api*>(api));
        api->Log(WXL_LOG_INFO, "wxl-physics", "loaded (physics only)");
        return 1;
    }
}
