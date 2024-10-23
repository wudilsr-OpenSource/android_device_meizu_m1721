#!/bin/bash
#
# SPDX-FileCopyrightText: 2016 The CyanogenMod Project
# SPDX-FileCopyrightText: 2017-2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

set -e

DEVICE=m1721
VENDOR=meizu

# Load extract_utils and do some sanity checks
MY_DIR="${BASH_SOURCE%/*}"
if [[ ! -d "${MY_DIR}" ]]; then MY_DIR="${PWD}"; fi

ANDROID_ROOT="${MY_DIR}/../../.."

export TARGET_ENABLE_CHECKELF=false

# If XML files don't have comments before the XML header, use this flag
# Can still be used with broken XML files by using blob_fixup
export TARGET_DISABLE_XML_FIXING=true

HELPER="${ANDROID_ROOT}/tools/extract-utils/extract_utils.sh"
if [ ! -f "${HELPER}" ]; then
    echo "Unable to find helper script at ${HELPER}"
    exit 1
fi
source "${HELPER}"

# Default to sanitizing the vendor folder before extraction
CLEAN_VENDOR=true

KANG=
SECTION=

while [ "${#}" -gt 0 ]; do
    case "${1}" in
        -n | --no-cleanup)
            CLEAN_VENDOR=false
            ;;
        -k | --kang)
            KANG="--kang"
            ;;
        -s | --section)
            SECTION="${2}"
            shift
            CLEAN_VENDOR=false
            ;;
        *)
            SRC="${1}"
            ;;
    esac
    shift
done

if [ -z "${SRC}" ]; then
    SRC="adb"
fi

function blob_fixup() {
    case "${1}" in
        # Camera configs
        vendor/lib/libmmcamera2_sensor_modules.so)
            [ "$2" = "" ] && return 0
            sed -i "s|/system/etc/camera|/vendor/etc/camera|g" "${2}"
            ;;
        # Camera socket
        vendor/bin/mm-qcamera-daemon)
            [ "$2" = "" ] && return 0
            sed -i "s|/data/misc/camera/cam_socket|/data/vendor/qcam/cam_socket|g" "${2}"
            ;;
        # Camera data
        vendor/lib/libmmcamera2_cpp_module.so \
        | libmmcamera2_dcrf.so \
        | libmmcamera2_iface_modules.so \
        | libmmcamera2_imglib_modules.so \
        | libmmcamera2_mct.so \
        | libmmcamera2_pproc_modules.so \
        | libmmcamera2_q3a_core.so \
        | libmmcamera2_sensor_modules.so \
        | libmmcamera2_stats_algorithm.so \
        | libmmcamera2_stats_modules.so \
        | libmmcamera_dbg.so \
        | libmmcamera_imglib.so \
        | libmmcamera_pdafcamif.so \
        | libmmcamera_pdaf.so \
        | libmmcamera_tintless_algo.so \
        | libmmcamera_tintless_bg_pca_algo.so \
        | libmmcamera_tuning.so)
            [ "$2" = "" ] && return 0
            sed -i "s|/data/misc/camera/|/data/vendor/qcam/|g" "${2}"
            ;;
        # Camera debug log file
        vendor/lib/libmmcamera_dbg.so)
            [ "$2" = "" ] && return 0
            sed -i "s|persist.camera.debug.logfile|persist.vendor.camera.dbglog|g" "${2}"
            ;;
        # Camera graphicbuffer shim
        vendor/lib/libmmcamera_ppeiscore.so)
            [ "$2" = "" ] && return 0
            "${PATCHELF}" --add-needed "libui_shim.so" "${2}"
            ;;
        # Camera VNDK support
        vendor/lib/libmmcamera2_stats_modules.so)
            [ "$2" = "" ] && return 0
            "${PATCHELF}" --remove-needed "libandroid.so" "${2}"
            "${PATCHELF}" --remove-needed "libgui.so" "${2}"
            sed -i "s|libandroid.so|libcamshim.so|g" "${2}"
            ;;
        vendor/lib/libmmcamera_ppeiscore.so)
            [ "$2" = "" ] && return 0
            "${PATCHELF}" --remove-needed "libgui.so" "${2}"
            ;;
        vendor/lib/libmpbase.so)
            [ "$2" = "" ] && return 0
            "${PATCHELF}" --remove-needed "libandroid.so" "${2}"
            ;;
        # Gnss
        vendor/etc/init/android.hardware.gnss@2.1-service-qti.rc)
            [ "$2" = "" ] && return 0
            sed -i -e '$a\\    capabilities NET_BIND_SERVICE' "${2}"
            ;;
        # Goodix
        vendor/lib64/libgf_ca.so)
            [ "$2" = "" ] && return 0
            sed -i "s|/system/etc/firmware|/vendor/firmware/gxf|g" "${2}"
            ;;
        # IMS
        system_ext/lib64/lib-imsvideocodec.so)
            [ "$2" = "" ] && return 0
            "${PATCHELF}" --add-needed "libgui_shim.so" "${2}"
            ;;
        # RIL
        vendor/lib64/libril-qc-hal-qmi.so)
            [ "$2" = "" ] && return 0
            for v in 1.{0..2}; do
                sed -i "s|android.hardware.radio.config@${v}.so|android.hardware.radio.c_shim@${v}.so|g" "${2}"
            done
            ;;
        *)
            return 1
            ;;
        # Thermal
        vendor/lib64/libthermalfeature.so)
            [ "$2" = "" ] && return 0
            sed -i "s|system/etc/|vendor/etc/|g" "${2}"
            ;;
    esac

    return 0
}

function blob_fixup_dry() {
    blob_fixup "$1" ""
}

# Initialize the helper
setup_vendor "${DEVICE}" "${VENDOR}" "${ANDROID_ROOT}" true "${CLEAN_VENDOR}"

extract "${MY_DIR}/proprietary-files.txt" "${SRC}" \
        "${KANG}" --section "${SECTION}"

"${MY_DIR}/setup-makefiles.sh"
