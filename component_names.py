from bidict import frozenbidict

# Bidirectional map of informal component names to their NX classes
component_names = frozenbidict(
    {
        "Detector": "NXdetector",
        "Monitor": "NXmonitor",
        "Chopper": "NXdisk_chopper",
        "Source": "NXsource",
        "Slit": "NXslit",
        "Mirror": "NXmirror",
        "Monochromator": "NXmonochromator",
        "Sample": "NXsample",
        "X-ray lens": "NXxraylens",
        "Attenuator": "NXattenuator",
        "Bending Magnet": "NXbending_magnet",
        "Capillary lens": "NXcapillary",
        "Beam stop": "NXbeam_stop",
        "Collimator": "NXcollimator",
        "Crystal": "NXcrystal",
        "Spin flipper": "NXflipper",
        "Fermi Chopper": "NXfermi_chopper",
        "Filter": "NXfilter",
        "Fresnel zone plate": "NXfresnel_zone_plate",
        "Diffraction Grating": "NXgrating",
        "Guide": "NXguide",
        "Insertion Device": "NXinsertion_device",
        "Pinhole": "NXpinhole",
        "Polarizer": "NXpolarizer",
        "Positioner": "NXpositioner",
        "Sensor": "NXsensor",
        "Velocity Selector": "NXvelocity_sensor",
    }
)
