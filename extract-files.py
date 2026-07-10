#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_remove,
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/meizu/m1721',
    'hardware/qcom-caf/msm8953',
    'vendor/qcom/opensource/dataservices',
    'vendor/qcom/opensource/commonsys/display',
    'vendor/qcom/opensource/display',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'com.qualcomm.qti.dpm.api@1.0',
        'libmmosal',
        'vendor.qti.imsrtpservice@3.0',
    ): lib_fixup_vendor_suffix,
    ('libwpa_client'): lib_fixup_remove,
}

# Define the blob fixups
blob_fixups: blob_fixups_user_type = {
    # Camera - Path fixups
    'vendor/bin/mm-qcamera-daemon': blob_fixup()
        .regex_replace(r'/data/misc/camera/cam_socket', r'/data/vendor/qcam/cam_socket'),
    'vendor/lib/libmmcamera2_sensor_modules.so': blob_fixup()
        .regex_replace(r'/system/etc/camera', r'/vendor/etc/camera'),
    ('vendor/lib/libmmcamera2_cpp_module.so', 'vendor/lib/libmmcamera2_dcrf.so', 'vendor/lib/libmmcamera2_iface_modules.so', 'vendor/lib/libmmcamera2_imglib_modules.so', 'vendor/lib/libmmcamera2_mct.so', 'vendor/lib/libmmcamera2_pproc_modules.so', 'vendor/lib/libmmcamera2_q3a_core.so', 'vendor/lib/libmmcamera2_sensor_modules.so', 'vendor/lib/libmmcamera2_stats_algorithm.so', 'vendor/lib/libmmcamera2_stats_modules.so', 'vendor/lib/libmmcamera_dbg.so', 'vendor/lib/libmmcamera_imglib.so', 'vendor/lib/libmmcamera_pdafcamif.so', 'vendor/lib/libmmcamera_pdaf.so', 'vendor/lib/libmmcamera_tintless_algo.so', 'vendor/lib/libmmcamera_tintless_bg_pca_algo.so', 'vendor/lib/libmmcamera_tuning.so'): blob_fixup()
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/'),
    # Camera - Property fixup
    'vendor/lib/libmmcamera_dbg.so': blob_fixup()
        .regex_replace(r'persist.camera.debug.logfile', r'persist.vendor.camera.dbglog'),
    # Camera - libstdc++.so -> libstdc++_vendor.so
    ('vendor/lib/libmmcamera_hdr_gb_lib.so', 'vendor/lib/liboptizoom.so', 'vendor/lib/libtrueportrait.so', 'vendor/lib/libubifocus.so', 'vendor/lib/libchromaflash.so'): blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    # Camera - shims, uneeded & VNDK fixups
    'vendor/lib/libmmcamera_ppeiscore.so': blob_fixup()
        .add_needed('libui_shim.so')
        .remove_needed('libgui.so'),
    'vendor/lib/libmmcamera_tuning.so': blob_fixup()
        .remove_needed('libmm-qcamera.so'),
    'vendor/lib/libmmcamera2_stats_modules.so': blob_fixup()
        .remove_needed('libandroid.so')
        .remove_needed('libgui.so')
        .regex_replace(r'libandroid.so', r'libcamshim.so'),
    'vendor/lib/libmpbase.so': blob_fixup()
        .remove_needed('libandroid.so')
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    # Camera - liblog dep.
    ('vendor/lib/libmmcamera_dbg.so', 'vendor/lib/libmmcamera_pdafcamif.so', 'vendor/lib/libmmcamera_pdaf.so', 'vendor/lib/libmmcamera_imx258_mono.so', 'vendor/lib/libjpegehw.so', 'vendor/lib/libjpegdhw.so', 'vendor/lib/libmmcamera_hdr_gb_lib', 'vendor/lib/libmmcamera2_sensor_modules.so', 'vendor/lib/libjpegdmahw.so', 'vendor/lib/libmmcamera_imx258.so', 'vendor/lib/libmmcamera_le2464c_master_eeprom', 'vendor/lib/libmmcamera_tintless_bg_pca_algo.so', 'vendor/lib/libqomx_jpegenc.so', 'vendor/lib/libqomx_jpegdec.so', 'vendor/lib/libqomx_jpegenc_pipe.so'): blob_fixup()
        .add_needed('liblog.so'),
    # Goodix
    'vendor/lib64/libgf_ca.so': blob_fixup()
        .regex_replace(r'/system/etc/firmware', r'/vendor/firmware/gxf'),
    # Gnss
    'vendor/etc/init/android.hardware.gnss@2.1-service-qti.rc': blob_fixup()
        .regex_replace(r'\n$', '\n    capabilities NET_BIND_SERVICE\n'),
    # IMS
    'system_ext/lib64/lib-imscamera.so': blob_fixup()
        .add_needed('libgui_shim.so'),
    'system_ext/lib64/lib-imsvideocodec.so': blob_fixup()
        .add_needed('libgui_shim.so')
        .replace_needed('libqdMetaData.so', 'libqdMetaData.system.so'),
    # Thermal
    'vendor/lib64/libthermalfeature.so': blob_fixup()
        .regex_replace(r'system/etc/', r'vendor/etc/'),
    # Camera - Override: combined fixups for conflicting entries
    'vendor/lib/libmmcamera2_sensor_modules.so': blob_fixup()
        .regex_replace(r'/system/etc/camera', r'/vendor/etc/camera')
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/')
        .add_needed('liblog.so'),
    'vendor/lib/libmmcamera_dbg.so': blob_fixup()
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/')
        .regex_replace(r'persist.camera.debug.logfile', r'persist.vendor.camera.dbglog')
        .add_needed('liblog.so'),
    'vendor/lib/libmmcamera_tuning.so': blob_fixup()
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/')
        .remove_needed('libmm-qcamera.so'),
    'vendor/lib/libmmcamera_pdafcamif.so': blob_fixup()
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/')
        .add_needed('liblog.so'),
    'vendor/lib/libmmcamera_pdaf.so': blob_fixup()
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/')
        .add_needed('liblog.so'),
    'vendor/lib/libmmcamera_tintless_bg_pca_algo.so': blob_fixup()
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/')
        .add_needed('liblog.so'),
    'vendor/lib/libmmcamera2_stats_modules.so': blob_fixup()
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/')
        .remove_needed('libandroid.so')
        .remove_needed('libgui.so')
        .regex_replace(r'libandroid.so', r'libcamshim.so'),
}  # fmt: skip

# Define the module
module = ExtractUtilsModule(
    'm1721',
    'meizu',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
