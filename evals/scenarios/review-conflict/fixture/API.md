# Public API

`lookup(id: String): Entry` always returns an entry. Unknown identifiers produce `UnknownEntry`, which preserves the
non-null contract for existing consumers.
