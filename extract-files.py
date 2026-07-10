#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

# Define the blob fixups
blob_fixups: blob_fixups_user_type = {
    'vendor/lib/libmmcamera2_sensor_modules.so': blob_fixup()
        .regex_replace(r'/system/etc/camera', r'/vendor/etc/camera'),
    'vendor/bin/mm-qcamera-daemon': blob_fixup()
        .regex_replace(r'/data/misc/camera/cam_socket', r'/data/vendor/qcam/cam_socket'),
    ('vendor/lib/libmmcamera2_cpp_module.so', 'libmmcamera2_dcrf.so', 'libmmcamera2_iface_modules.so', 'libmmcamera2_imglib_modules.so', 'libmmcamera2_mct.so', 'libmmcamera2_pproc_modules.so', 'libmmcamera2_q3a_core.so', 'libmmcamera2_sensor_modules.so', 'libmmcamera2_stats_algorithm.so', 'libmmcamera2_stats_modules.so', 'libmmcamera_dbg.so', 'libmmcamera_imglib.so', 'libmmcamera_pdafcamif.so', 'libmmcamera_pdaf.so', 'libmmcamera_tintless_algo.so', 'libmmcamera_tintless_bg_pca_algo.so', 'libmmcamera_tuning.so'): blob_fixup()
        .regex_replace(r'/data/misc/camera/', r'/data/vendor/qcam/'),
    'vendor/lib/libmmcamera_dbg.so': blob_fixup()
        .regex_replace(r'persist.camera.debug.logfile', r'persist.vendor.camera.dbglog'),
    'vendor/lib/libmmcamera2_stats_modules.so': blob_fixup()
        .remove_needed('libandroid.so')
        .remove_needed('libgui.so')
        .regex_replace(r'libandroid.so', r'libcamshim.so'),
    'vendor/lib/libmpbase.so': blob_fixup()
        .remove_needed('libandroid.so'),
    'vendor/lib/libmmcamera_ppeiscore.so': blob_fixup()
        .add_needed('libui_shim.so')
        .remove_needed('libgui.so'),
    'vendor/etc/init/android.hardware.gnss@2.1-service-qti.rc': blob_fixup()
        .regex_replace(r'\n$', '\n    capabilities NET_BIND_SERVICE\n'),
    'vendor/lib64/libgf_ca.so': blob_fixup()
        .regex_replace(r'/system/etc/firmware', r'/vendor/firmware/gxf'),
    'system_ext/lib64/lib-imsvideocodec.so': blob_fixup()
        .add_needed('libgui_shim.so'),
    'vendor/lib64/libril-qc-hal-qmi.so': blob_fixup()
        .regex_replace(r'android.hardware.radio.config@1.0.so', r'android.hardware.radio.c_shim@1.0.so')
        .regex_replace(r'android.hardware.radio.config@1.1.so', r'android.hardware.radio.c_shim@1.1.so')
        .regex_replace(r'android.hardware.radio.config@1.2.so', r'android.hardware.radio.c_shim@1.2.so'),
    'vendor/lib64/libthermalfeature.so': blob_fixup()
        .regex_replace(r'system/etc/', r'vendor/etc/')
}  # fmt: skip

# Define the module
module = ExtractUtilsModule(
    'm1721',
    'meizu',
    blob_fixups=blob_fixups,
    check_elf=False,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
