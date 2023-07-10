# 🍵 tea_lang 
Tiny programming language implemented over Python 3.10.6

# Features
- s-expression syntax (like Lisp)
- prefix notation (weird, I know, but the machine like it)
- all the interpreter is one file (`tea.py`)
- easy to learn
- fast to type
- multiparadigm!
  - OOP (with classes)
  - Functional (lambda functions)
  - Modular
- create and import your own programs/modules on `.tea` files

```
tl> + 2 2
4
tl> [~l x [* x x]] [3] /* lambda function */
9
tl> [def [f x ] [print x]] [f 10]
```

# Requirements

|Package            |Version|
|:------------------|:-----:|
| exceptiongroup    | 1.1.1 |
| iniconfig         | 2.0.0 |
| lark              | 1.1.5 |
| libcst            | 1.0.1 |
| packaging         | 23.1  |
| pluggy            | 1.0.0 |
| pytest            | 7.3.1 |
| PyYAML            | 6.0   |
| tomli             | 2.0.1 |
| typing-inspect    | 0.9.0 |
| typing_extensions | 4.6.3 |
