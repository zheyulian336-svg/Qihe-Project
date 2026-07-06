#!/usr/bin/env python3
"""
生成 QiheApp.xcodeproj/project.pbxproj
运行一次即可，无需重复运行。
"""

import uuid
import os
import sys

def hex24():
    """生成 24 位十六进制 ID（Xcode 风格）"""
    return uuid.uuid4().hex[:24].upper()

# ─── 为每个 PBX 对象预分配唯一 ID ───
IDS = {k: hex24() for k in [
    # 项目 & 组
    "project_obj",
    "main_group",
    "qihe_group",
    "products_group",
    # Target
    "native_target",
    "product_ref",
    # Build phases
    "sources_phase",
    "resources_phase",
    "frameworks_phase",
    # Swift 文件 → PBXBuildFile
    "bf_qiheapp",
    "bf_contentview",
    "bf_webview",
    # Swift 文件 → PBXFileReference
    "fr_qiheapp",
    "fr_contentview",
    "fr_webview",
    # 资源 → PBXFileReference
    "fr_infoplist",
    "fr_assets",
    "fr_www",
    # Build configurations (project ×2, target ×2)
    "cfg_proj_debug",
    "cfg_proj_release",
    "cfg_targ_debug",
    "cfg_targ_release",
    # Configuration lists (project, target)
    "cl_proj",
    "cl_targ",
    # PBXResourcesBuildPhase 里的 build files
    "bf_assets",
    "bf_www",
]}

PID  = IDS["project_obj"]
MGRP = IDS["main_group"]
QGRP = IDS["qihe_group"]
PGRP = IDS["products_group"]

TGT   = IDS["native_target"]
PRREF = IDS["product_ref"]

SPH = IDS["sources_phase"]
RPH = IDS["resources_phase"]
FPH = IDS["frameworks_phase"]

# source build files
BF_APP  = IDS["bf_qiheapp"]
BF_CV   = IDS["bf_contentview"]
BF_WV   = IDS["bf_webview"]
# source file refs
FR_APP  = IDS["fr_qiheapp"]
FR_CV   = IDS["fr_contentview"]
FR_WV   = IDS["fr_webview"]

FR_INFO   = IDS["fr_infoplist"]
FR_ASSETS = IDS["fr_assets"]
FR_WWW    = IDS["fr_www"]

BF_ASSETS = IDS["bf_assets"]
BF_WWW    = IDS["bf_www"]

CFG_PD = IDS["cfg_proj_debug"]
CFG_PR = IDS["cfg_proj_release"]
CFG_TD = IDS["cfg_targ_debug"]
CFG_TR = IDS["cfg_targ_release"]

CL_P = IDS["cl_proj"]
CL_T = IDS["cl_targ"]

# ─── 公共的 build settings ───
BASE_SETTINGS = {
    "ALWAYS_SEARCH_USER_PATHS": "NO",
    "ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS": "YES",
    "CLANG_ANALYZER_NONNULL": "YES",
    "CLANG_CXX_LANGUAGE_STANDARD": "gnu++20",
    "CLANG_ENABLE_MODULES": "YES",
    "CLANG_ENABLE_OBJC_ARC": "YES",
    "COPY_PHASE_STRIP": "NO",
    "DEBUG_INFORMATION_FORMAT": "dwarf",
    "ENABLE_STRICT_OBJC_MSGSEND": "YES",
    "ENABLE_TESTABILITY": "YES",
    "GCC_DYNAMIC_NO_PIC": "NO",
    "GCC_OPTIMIZATION_LEVEL": "0",
    "GCC_PREPROCESSOR_DEFINITIONS": ['DEBUG=1', '$(inherited)'],
    "IPHONEOS_DEPLOYMENT_TARGET": "17.0",
    "LOCALIZATION_PREFERS_STRING_CATALOGS": "YES",
    "MTL_ENABLE_DEBUG_INFO": "INCLUDE_SOURCE",
    "ONLY_ACTIVE_ARCH": "YES",
    "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG",
    "SWIFT_OPTIMIZATION_LEVEL": "-Onone",
}

RELEASE_SETTINGS = {
    "ALWAYS_SEARCH_USER_PATHS": "NO",
    "ASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS": "YES",
    "CLANG_ANALYZER_NONNULL": "YES",
    "CLANG_CXX_LANGUAGE_STANDARD": "gnu++20",
    "CLANG_ENABLE_MODULES": "YES",
    "CLANG_ENABLE_OBJC_ARC": "YES",
    "COPY_PHASE_STRIP": "NO",
    "DEBUG_INFORMATION_FORMAT": "dwarf-with-dsym",
    "ENABLE_NS_ASSERTIONS": "NO",
    "ENABLE_STRICT_OBJC_MSGSEND": "YES",
    "GCC_OPTIMIZATION_LEVEL": "s",
    "IPHONEOS_DEPLOYMENT_TARGET": "17.0",
    "LOCALIZATION_PREFERS_STRING_CATALOGS": "YES",
    "MTL_ENABLE_DEBUG_INFO": "NO",
    "SWIFT_COMPILATION_MODE": "wholemodule",
    "VALIDATE_PRODUCT": "YES",
}

TARGET_SHARED = {
    "ASSETCATALOG_COMPILER_APPICON_NAME": "AppIcon",
    "ASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME": "AccentColor",
    "CODE_SIGN_STYLE": "Automatic",
    "CURRENT_PROJECT_VERSION": "1",
    "GENERATE_INFOPLIST_FILE": "YES",
    "INFOPLIST_FILE": "QiheApp/Info.plist",
    "INFOPLIST_KEY_UIApplicationSceneManifest_Generation": "YES",
    "INFOPLIST_KEY_UIApplicationSupportsIndirectInputEvents": "YES",
    "INFOPLIST_KEY_UILaunchScreen_Generation": "YES",
    "INFOPLIST_KEY_UISupportedInterfaceOrientations": "UIInterfaceOrientationPortrait",
    "LD_RUNPATH_SEARCH_PATHS": ["$(inherited)", "@executable_path/Frameworks"],
    "MARKETING_VERSION": "1.0",
    "PRODUCT_BUNDLE_IDENTIFIER": "com.qihe.app",
    "PRODUCT_NAME": "$(TARGET_NAME)",
    "SWIFT_EMIT_LOC_STRINGS": "YES",
    "SWIFT_VERSION": "5.0",
    "TARGETED_DEVICE_FAMILY": "1",
}

def plist_value(val):
    """将 Python 值转为 pbxproj plist 格式的字符串"""
    if isinstance(val, bool):
        return "YES" if val else "NO"
    if isinstance(val, str):
        # 转义特殊字符
        escaped = val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
        return f'"{escaped}"'
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, list):
        items = ", ".join(plist_value(v) for v in val)
        return f"({items})"
    return f'"{val}"'

def dict_block(d, indent="\t\t\t"):
    lines = []
    for k, v in d.items():
        lines.append(f'{indent}{k} = {plist_value(v)};')
    return "\n".join(lines)

def build_file(file_ref_id):
    """生成 PBXBuildFile 条目"""
    return f"\t\t{hex24()} /* {file_ref_id} in Sources */ = {{isa = PBXBuildFile; fileRef = {file_ref_id}; }};"

def resource_build_file(file_ref_id):
    """生成 Resources PBXBuildFile 条目"""
    return f"\t\t{hex24()} /* {file_ref_id} in Resources */ = {{isa = PBXBuildFile; fileRef = {file_ref_id}; }};"


# ─── 生成文件内容 ───
lines = []

lines.append("// !$*UTF8*$!")
lines.append("{")
lines.append("\tarchiveVersion = 1;")
lines.append("\tclasses = {")
lines.append("\t};")
lines.append(f"\tobjectVersion = 56;")
lines.append("\tobjects = {")
lines.append("")

# ── PBXBuildFile section ──
lines.append("/* Begin PBXBuildFile section */")
for bid, rid in [(BF_APP, FR_APP), (BF_CV, FR_CV), (BF_WV, FR_WV)]:
    lines.append(f"\t\t{bid} /* {rid} in Sources */ = {{isa = PBXBuildFile; fileRef = {rid}; }};")
for bid, rid in [(BF_ASSETS, FR_ASSETS), (BF_WWW, FR_WWW)]:
    lines.append(f"\t\t{bid} /* {rid} in Resources */ = {{isa = PBXBuildFile; fileRef = {rid}; }};")
lines.append("/* End PBXBuildFile section */")
lines.append("")

# ── PBXFileReference section ──
lines.append("/* Begin PBXFileReference section */")
lines.append(f"\t\t{PRREF} /* QiheApp.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = QiheApp.app; sourceTree = BUILT_PRODUCTS_DIR; }};")
lines.append(f"\t\t{FR_APP} /* QiheApp.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = QiheApp.swift; sourceTree = \"<group>\"; }};")
lines.append(f"\t\t{FR_CV} /* ContentView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ContentView.swift; sourceTree = \"<group>\"; }};")
lines.append(f"\t\t{FR_WV} /* WebViewWrapper.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = WebViewWrapper.swift; sourceTree = \"<group>\"; }};")
lines.append(f"\t\t{FR_INFO} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = \"<group>\"; }};")
lines.append(f"\t\t{FR_ASSETS} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = \"<group>\"; }};")
lines.append(f"\t\t{FR_WWW} /* www */ = {{isa = PBXFileReference; lastKnownFileType = folder; name = www; path = www; sourceTree = \"<group>\"; }};")
lines.append("/* End PBXFileReference section */")
lines.append("")

# ── PBXFrameworksBuildPhase section ──
lines.append("/* Begin PBXFrameworksBuildPhase section */")
lines.append(f"\t\t{FPH} /* Frameworks */ = {{")
lines.append("\t\t\tisa = PBXFrameworksBuildPhase;")
lines.append("\t\t\tbuildActionMask = 2147483647;")
lines.append("\t\t\tfiles = (")
lines.append("\t\t\t);")
lines.append("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
lines.append("\t\t};")
lines.append("/* End PBXFrameworksBuildPhase section */")
lines.append("")

# ── PBXGroup section ──
lines.append("/* Begin PBXGroup section */")
lines.append(f"\t\t{MGRP} = {{")
lines.append("\t\t\tisa = PBXGroup;")
lines.append("\t\t\tchildren = (")
lines.append(f"\t\t\t\t{QGRP} /* QiheApp */,")
lines.append(f"\t\t\t\t{PGRP} /* Products */,")
lines.append("\t\t\t);")
lines.append("\t\t\tsourceTree = \"<group>\";")
lines.append("\t\t};")
lines.append(f"\t\t{QGRP} /* QiheApp */ = {{")
lines.append("\t\t\tisa = PBXGroup;")
lines.append("\t\t\tchildren = (")
lines.append(f"\t\t\t\t{FR_APP} /* QiheApp.swift */,")
lines.append(f"\t\t\t\t{FR_CV} /* ContentView.swift */,")
lines.append(f"\t\t\t\t{FR_WV} /* WebViewWrapper.swift */,")
lines.append(f"\t\t\t\t{FR_INFO} /* Info.plist */,")
lines.append(f"\t\t\t\t{FR_ASSETS} /* Assets.xcassets */,")
lines.append(f"\t\t\t\t{FR_WWW} /* www */,")
lines.append("\t\t\t);")
lines.append("\t\t\tpath = QiheApp;")
lines.append("\t\t\tsourceTree = \"<group>\";")
lines.append("\t\t};")
lines.append(f"\t\t{PGRP} /* Products */ = {{")
lines.append("\t\t\tisa = PBXGroup;")
lines.append("\t\t\tchildren = (")
lines.append(f"\t\t\t\t{PRREF} /* QiheApp.app */,")
lines.append("\t\t\t);")
lines.append("\t\t\tname = Products;")
lines.append("\t\t\tsourceTree = \"<group>\";")
lines.append("\t\t};")
lines.append("/* End PBXGroup section */")
lines.append("")

# ── PBXNativeTarget section ──
lines.append("/* Begin PBXNativeTarget section */")
lines.append(f"\t\t{TGT} /* QiheApp */ = {{")
lines.append("\t\t\tisa = PBXNativeTarget;")
lines.append(f"\t\t\tbuildConfigurationList = {CL_T} /* Build configuration list for PBXNativeTarget \"QiheApp\" */;")
lines.append("\t\t\tbuildPhases = (")
lines.append(f"\t\t\t\t{SPH} /* Sources */,")
lines.append(f"\t\t\t\t{FPH} /* Frameworks */,")
lines.append(f"\t\t\t\t{RPH} /* Resources */,")
lines.append("\t\t\t);")
lines.append("\t\t\tbuildRules = (")
lines.append("\t\t\t);")
lines.append("\t\t\tdependencies = (")
lines.append("\t\t\t);")
lines.append(f"\t\t\tname = QiheApp;")
lines.append(f"\t\t\tproductName = QiheApp;")
lines.append(f"\t\t\tproductReference = {PRREF};")
lines.append("\t\t\tproductType = \"com.apple.product-type.application\";")
lines.append("\t\t};")
lines.append("/* End PBXNativeTarget section */")
lines.append("")

# ── PBXProject section ──
lines.append("/* Begin PBXProject section */")
lines.append(f"\t\t{PID} /* Project object */ = {{")
lines.append("\t\t\tisa = PBXProject;")
lines.append("\t\t\tattributes = {")
lines.append("\t\t\t\tBuildIndependentTargetsInParallel = 1;")
lines.append("\t\t\t\tLastSwiftUpdateCheck = 1600;")
lines.append("\t\t\t\tLastUpgradeCheck = 1600;")
lines.append("\t\t\t\tTargetAttributes = {")
lines.append(f"\t\t\t\t\t{TGT} = {{")
lines.append("\t\t\t\t\t\tCreatedOnToolsVersion = 16.0;")
lines.append("\t\t\t\t\t}};")
lines.append("\t\t\t\t};")
lines.append(f"\t\t\tbuildConfigurationList = {CL_P} /* Build configuration list for PBXProject \"QiheApp\" */;")
lines.append("\t\t\tcompatibilityVersion = \"Xcode 14.0\";")
lines.append("\t\t\tdevelopmentRegion = \"zh-Hans\";")
lines.append("\t\t\thasScannedForEncodings = 0;")
lines.append("\t\t\tknownRegions = (")
lines.append("\t\t\t\ten,")
lines.append("\t\t\t\tBase,")
lines.append("\t\t\t\t\"zh-Hans\",")
lines.append("\t\t\t);")
lines.append(f"\t\t\tmainGroup = {MGRP};")
lines.append(f"\t\t\tproductRefGroup = {PGRP} /* Products */;")
lines.append("\t\t\tprojectDirPath = \"\";")
lines.append("\t\t\tprojectRoot = \"\";")
lines.append("\t\t\ttargets = (")
lines.append(f"\t\t\t\t{TGT} /* QiheApp */,")
lines.append("\t\t\t);")
lines.append("\t\t};")
lines.append("/* End PBXProject section */")
lines.append("")

# ── PBXResourcesBuildPhase section ──
lines.append("/* Begin PBXResourcesBuildPhase section */")
lines.append(f"\t\t{RPH} /* Resources */ = {{")
lines.append("\t\t\tisa = PBXResourcesBuildPhase;")
lines.append("\t\t\tbuildActionMask = 2147483647;")
lines.append("\t\t\tfiles = (")
lines.append(f"\t\t\t\t{BF_ASSETS} /* Assets.xcassets in Resources */,")
lines.append(f"\t\t\t\t{BF_WWW} /* www in Resources */,")
lines.append("\t\t\t);")
lines.append("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
lines.append("\t\t};")
lines.append("/* End PBXResourcesBuildPhase section */")
lines.append("")

# ── PBXSourcesBuildPhase section ──
lines.append("/* Begin PBXSourcesBuildPhase section */")
lines.append(f"\t\t{SPH} /* Sources */ = {{")
lines.append("\t\t\tisa = PBXSourcesBuildPhase;")
lines.append("\t\t\tbuildActionMask = 2147483647;")
lines.append("\t\t\tfiles = (")
lines.append(f"\t\t\t\t{BF_APP} /* QiheApp.swift in Sources */,")
lines.append(f"\t\t\t\t{BF_CV} /* ContentView.swift in Sources */,")
lines.append(f"\t\t\t\t{BF_WV} /* WebViewWrapper.swift in Sources */,")
lines.append("\t\t\t);")
lines.append("\t\t\trunOnlyForDeploymentPostprocessing = 0;")
lines.append("\t\t};")
lines.append("/* End PBXSourcesBuildPhase section */")
lines.append("")

# ── XCBuildConfiguration section ──
lines.append("/* Begin XCBuildConfiguration section */")
# 项目 Debug
lines.append(f"\t\t{CFG_PD} /* Debug */ = {{")
lines.append("\t\t\tisa = XCBuildConfiguration;")
lines.append("\t\t\tbuildSettings = {")
lines.append(dict_block(BASE_SETTINGS))
lines.append("\t\t\t\tSDKROOT = iphoneos;")
lines.append("\t\t\t};")
lines.append("\t\t\tname = Debug;")
lines.append("\t\t};")
# 项目 Release
lines.append(f"\t\t{CFG_PR} /* Release */ = {{")
lines.append("\t\t\tisa = XCBuildConfiguration;")
lines.append("\t\t\tbuildSettings = {")
lines.append(dict_block(RELEASE_SETTINGS))
lines.append("\t\t\t\tSDKROOT = iphoneos;")
lines.append("\t\t\t};")
lines.append("\t\t\tname = Release;")
lines.append("\t\t};")
# Target Debug
lines.append(f"\t\t{CFG_TD} /* Debug */ = {{")
lines.append("\t\t\tisa = XCBuildConfiguration;")
lines.append("\t\t\tbuildSettings = {")
lines.append(dict_block({**TARGET_SHARED, "SWIFT_ACTIVE_COMPILATION_CONDITIONS": "DEBUG", "SWIFT_OPTIMIZATION_LEVEL": "-Onone"}))
lines.append("\t\t\t};")
lines.append("\t\t\tname = Debug;")
lines.append("\t\t};")
# Target Release
lines.append(f"\t\t{CFG_TR} /* Release */ = {{")
lines.append("\t\t\tisa = XCBuildConfiguration;")
lines.append("\t\t\tbuildSettings = {")
lines.append(dict_block(TARGET_SHARED))
lines.append("\t\t\t};")
lines.append("\t\t\tname = Release;")
lines.append("\t\t};")
lines.append("/* End XCBuildConfiguration section */")
lines.append("")

# ── XCConfigurationList section ──
lines.append("/* Begin XCConfigurationList section */")
lines.append(f"\t\t{CL_P} /* Build configuration list for PBXProject \"QiheApp\" */ = {{")
lines.append("\t\t\tisa = XCConfigurationList;")
lines.append(f"\t\t\tbuildConfigurations = (")
lines.append(f"\t\t\t\t{CFG_PD} /* Debug */,")
lines.append(f"\t\t\t\t{CFG_PR} /* Release */,")
lines.append("\t\t\t);")
lines.append("\t\t\tdefaultConfigurationIsVisible = 0;")
lines.append("\t\t\tdefaultConfigurationName = Release;")
lines.append("\t\t};")
lines.append(f"\t\t{CL_T} /* Build configuration list for PBXNativeTarget \"QiheApp\" */ = {{")
lines.append("\t\t\tisa = XCConfigurationList;")
lines.append(f"\t\t\tbuildConfigurations = (")
lines.append(f"\t\t\t\t{CFG_TD} /* Debug */,")
lines.append(f"\t\t\t\t{CFG_TR} /* Release */,")
lines.append("\t\t\t);")
lines.append("\t\t\tdefaultConfigurationIsVisible = 0;")
lines.append("\t\t\tdefaultConfigurationName = Release;")
lines.append("\t\t};")
lines.append("/* End XCConfigurationList section */")
lines.append("")

# ── 结束 ──
lines.append("\t};")
lines.append(f"\trootObject = {PID} /* Project object */;")
lines.append("}")

output = "\n".join(lines)

# ─── 写入文件 ───
proj_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "QiheApp.xcodeproj")
os.makedirs(proj_dir, exist_ok=True)

pbx_path = os.path.join(proj_dir, "project.pbxproj")
with open(pbx_path, "w", encoding="utf-8") as f:
    f.write(output)

print(f"✅ 已生成 Xcode 项目: {pbx_path}")
print(f"   用 Xcode 打开 ios/QiheApp.xcodeproj 即可")
