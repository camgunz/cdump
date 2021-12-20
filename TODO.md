# To Do

## Features

- Nested anonymous types
- Variadic functions
- Volatile types

## Broadly

Without running the preprocessor before parsing, a lot of info is lost.  It's
not just definition changes, it's that `#include` doesn't run so a lot of files
just aren't read.  We should come up w/ some way of doing this.
