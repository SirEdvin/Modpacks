StartupEvents.registry('item', event => {
    event.create("hollow_brass_chunk_loader")
    .displayName("Hollow brass chunk loader")
    .modelJson({
        "parent": "create_power_loader:block/empty_brass_chunk_loader/item"
    })
})