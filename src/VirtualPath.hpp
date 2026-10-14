// wxl-physics (physics-only cut): minimal stand-in for equip-plus's VirtualPath.hpp.
// PhysicsLive.cpp only needs WxlIniGetBool to read [Physics] Enabled=1 from
// WXLExtendedEquipment.ini. Same signature and namespace as the original.
#pragma once

namespace wxl::scripts::equipextension
{
    bool WxlIniGetBool(const char* section, const char* key, bool defaultValue);
}
