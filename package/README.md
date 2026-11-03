# ImmuKnow Template resources

This distribution packages the authored files listed in the parent repository's
`studio-scaffold.json`. Build it from the Template Git checkout with `uv build
package`. Source archives retain the same files, hashes and provenance and can
be rebuilt independently. The Core library, maintainer tests and client inputs
are excluded. Read resources through `immuknow_template.resources`; never edit
the installed package. Downloaded projects keep their independent Core-only setup.
