# Subterra Changelog

### v1.2
- Refactored code:
  - Exceptions and their utilities are now in their own module
  - The parsing functions are now in their own module
  - The runtime helpers are now in their own module
  - The only thing left in the main `subterra.py` is the entry point and the execute function that runs a subroutine
  - The interpreter code is no longer in the root directory; it has been moved to `bin` to be more out of the user's way
  - Subroutines and imports now have helper classes that make them easier to use and modify
    - This also makes the code more readable by removing a ridiculous amount of "magic numbers"
  - Attempted to create a similar such class for the main stack... and failed. It still works the same as before.
- Changed how working directories are handled; imports are now relative to the executing program, not the interpreter.
- Created a batch file opener (allows for file association; bash equivalent will come later)

Note: outside the path changes, the actual code execution should not be affected by this update! If it is, please report it as a bug.

### v1.1
- Added `r` command (random integer)
- Fixed bug with `{}` subroutines and `@`/`e` causing stack to not be updated when subroutine quits

### v1.0
- Initial version
