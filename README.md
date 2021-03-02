# famegenerator
A generator of Fame/Famix generator for Moose

## Installation

A pipfile is available, so you can directly install from it:

```bash
$ pipenv install
```

## Usage

To use the generator of generator, you need a `.ecore` as input and express the target file:

```bash
$ python famegen.py <FILE> -o <OUTPUT_FILE>
```

If the option `-o <OUTPUT_FILE>` is not provided, the generated code is directly displayed in stdout.

The generator also supports URLs as localisation for your `.ecore`.

