def serialize_waterbutler_settings(configured_storage_addon):
    """An ugly compatibility layer between GravyValet and WaterButler."""
    return {"folder": configured_storage_addon.root_folder}
