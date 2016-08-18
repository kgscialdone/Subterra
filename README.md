# Subterra
Official Python interpreter for the programming language Subterra

Most recent changelog entry: https://github.com/tripl3dogdare/Subterra/blob/v1.1/CHANGELOG.md#v11

## What is Subterra?
Subterra is an esoteric programming language designed to be simple yet powerful. Every instruction in Subterra consists of only one character, it uses a single stack for data storage, and the only datatype it handles is integers (a typical "tarpit language").

What sets Subterra apart from other languages like it is the **subroutine system**. This allows for basic pseudo-functions that can be called at any time, making Subterra feel more like an imperative programming language than a typical tarpit. Subterra also features an import system, allowing for multiple-file abstraction.

## Non-Integer Datatypes

I mentioned before that Subterra only handles integers, and that is true. Anything that appears to use a boolean is actually using `0` as `false` and `not 0` as `true`, and strings are syntactic sugar for a bunch of decimal Unicode values and a length value. This allows for (relatively) convienent use of booleans and strings, but to the language, they're just integers.

Example:
```
"Hello world!" ~> Resulting stack: [72,101,108,108,111,32,119,111,114,108,100,33,12]
                                                                                ~ ^ the length of the string

~ A simple print function
0 { w [0>] {bct1-} $ }

"Hello world!"0# ~> prints "Hello world!"
```

## Understanding subroutines
Subroutines, at their core, are pieces of code that can be read and executed at any time, as many times as you want. They can call themselves (recursion), be defined anonymously in certain contexts, and be imported from other files. They basically serve the same function as, well, functions, but are slightly simpler in their design.

Subroutines are defined as anything between paired brackets (`{}`, `[]`, `()`). Each type of brackets creates a slightly different effect on the subroutine's function:
* `{}` will use the calling context's stack in place.
* `[]` will copy the calling context's stack, allowing them to use values from it without modifying the original.
* `()` will use a fresh, empty stack.

Subroutines will also push the top of their stack to the calling context's stack when they finish executing (unless they're defined using `{}`).

When defining a subroutine normally, it will pop from the stack and use that number as it's ID. It can then be called using that same ID. In certain contexts, subroutines can be defined anonymously; these will not be registered and will be inaccessible from elsewhere in the program. However, you can also use a predefined or imported subroutine anywhere you can use an anonymous one. Subroutine IDs do not need to be sequential.

The really cool thing is that in Subterra, _everything is a subroutine_. This includes the entire program itself - it's technically a subroutine registered as ID -1. While it's not recommended that you call said subroutine, it's left as an option. When defining your own subroutines, however, only positive integers are considered valid IDs.

Defined subroutines will go out of scope when their calling context closes, which means you can define a subroutine inside another subroutine, but you can't access the inner from anywhere but inside the outer.

## Import System
Subterra also features an import system that allows you to use subroutines defined in other files. This is achieved by running the code in the file, then saving the module's subroutines under an import ID (this will start at 0 and automatically increment). The subroutines can then be accessed using both the corresponding import ID and the subroutine ID under which it is defined in the other file.

Example:
```
"import"m ~Import "import.sbtr" under id 0
"import2"m ~Import "import2.sbtr" under id 1

.0;0 ~Call subroutine 0 from import 0
.1;77 ~Call subroutine 77 from import 1
```

You can also import from inside a subroutine - the import will go out of scope when the subroutine finishes. Since everything happens sequentially, you won't have any issues with orphaned import IDs, though your program may slow down as it has to import every time the subroutine is called. This also allows for imported files to have their own imports - the calling context will have no access to anything imported in the called/imported context.

## Language Reference
| Command | Effect | Version Added |
| --- | --- | ---: |
| `~` | Turns everything after it until the end of a line into a comment. |
| `0-9` | Pushes an integer to the stack. (Note that `15` will push `[15]`, not `[1,5]`) |
| `+-*/%` | Pops two integers off the stack and pushes the result of the corresponding math operation (using `-`, `[6,2]` -> `[4]`). |
| `r` | Pops an integer from the stack and pushes a random number between `0` (inclusive) and that number (exclusive). | v1.1 |
| `$` | Pops the top of the stack and deletes it. |
| `&` | Duplicates the top of the stack. |
| `b` | Moves the top of the stack to the bottom. |
| `t` | Moves the bottom of the stack to the top. |
| `@` | Reverses the entire stack. |
| `s` | Pushes the size of the stack (`[3,2,1]` -> `[3,2,1,3]`). |
| `e` | Empties the stack. |
| `=` | Pops two elements and pushes whether they are equal. |
| `!` | Pops two elements and pushes whether they are not equal. |
| `<` | Pops two elements and pushes whether the lower is less than the upper. |
| `>` | Pops two elements and pushes whether the lower is greater than the upper. |
| `?` | Pops the top of the stack and executes the following subroutine if the resulting value is not `0`. |
| `:` | Can only be used after a ?; executes the following subroutine if the value was `0`. |
| `w` | Calls the following subroutine, then if it's return value is not `0` executes the second. Repeats until the first subroutine returns `0`. |
| `p` | Pops the top of the stack and prints it as an integer. |
| `c` | Pops the top of the stack and prints it as a Unicode character. |
| `i` | Waits for user input, then pushes it as a string (see Non-Integer Datatypes). |
| `"` | Pushes everything between itself and the next `"` as a string (see Non-Integer Datatypes). Respects valid escape sequences prefixed with `\` as standard ASCII characters. |
| `'` | The same as `"`; can be used to avoid incessant escaping. |
| `\` | Pushes the Unicode value of the following character to the stack rather than executing it. |
| `{[(` | Begins a subroutine definition (see Understanding Subroutines). |
| `}])` | Ends a subroutine definition (see Understanding Subroutines). |
| `#` | Pops the top of the stack and calls the corresponding subroutine. |
| `d` | Pushes the program's current recursion depth. Useful for preventing code from running when a module is imported (can be used analagously to Python's `if __name__ == '__main__'` by checking it against `0`). |
| `m` | Pops a string from the stack and imports the file at that path. See Import System for details. |
| `.` | Calls an imported subroutine using the next two integers (respectively import ID and subroutine ID). See Import System for details. |
| Space, Tab, Newline, `|;` | Token seperators (i.e. `15` will push `[15]`, where `1;5` will push `[1,5]`. Will be otherwise ignored. |
