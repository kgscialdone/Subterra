# Subterra Changelog

### v1.3
- Rewrote most of the code from scratch to reduce mess
  - The resulting program should be _almost_ noticeably faster
  - The code is much nicer to look at (because that matters -_-)
- Changed import system drastically
  - Importing now requires an ID to be bound, rather than auto-incrementing. Example: `"print"0m`
  - Calling imported subroutines now pops from the stack rather than using lookaheads. Example: `0;0.`
    - The lower number on the stack is the import id, the higher is the subroutine id
    - Can be updated just by moving the `.` to the other side of the call definition
  - Now supports importing Python files with the extension `.stpy`
    - Can only be imported, not run as Subterra code
    - Expects a global-scope dict `data` mapping subroutine ids to functions
    - Take precedence over `.sbtr` files in the case of a name conflict
    - See `lib/math.stpy` for an example
    - Error logging may be _slightly_ broken on subroutines imported this way, not sure
  - Now supports importing from the `lib` folder in the Subterra root
    - Read as: yay, standard library!
    - Will attempt to import the given path relative to the main file first, then default to `lib`
    - Current standard library includes `print` and `math`
  - Dots in import paths are now internally replaced with slashes, so you can use either
- Adding `-p` to the command line call will keep the command window open after the program execution
  - The inverse was true in v1.2, but I forgot to document it; `-np` would remove the pause
- Running the interpreter on a relative filepath will no longer break it
- Changed how `w` conditions are handled
  - `{` subs now pop the top of the stack each time they are used as a `w` condition, rather than peeking at it
    - This is to avoid making a stupid exception to how the system works for that _one_ case
  - `[` and `(` subs work differently internally, but should not act any differently
- Added a wiki!

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
