# 🍵 tea
Minimal/Simple/Tiny programming language implemented over Python 3.10.6.

You can find the executable `tea` on the `dist` folder (for linux).

# Features
- Uses **S-expression syntax** (like Lisp) but with square brackets (faster to type)
- Easy to learn
- Prefix notation (weird, I know, but the machine like it)
- The whole interpreter is one file (`tea.py`)
- Multiparadigm!
  - OOP (with classes)
  - Functional (lambda functions)
  - Modular
- Create and import your own programs/modules on `.tea` files (check the modules folder for examples)

```
$ ./dist/tea
tea version 0.0.2 2023-07-11

tea> [+ 1 2]
3
tea> [var i 10]
10
tea> i
10
tea> [ [lambda [x] [* x x]] 2 ]
4
tea> ^C
No more tea for now. Goodbye...
```

Check the tests folder for more examples

# Requirements
Nothing. Pure Python Standard Library magic!.

Although, you can unse `pytest 7.3+` in case you want to run the tests.

