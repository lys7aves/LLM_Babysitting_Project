# Formula Recognition

## Goal

  We want GPT to solve the formula in images well



## Problems

- ChatGPT doesn't accurately recognize positional information like subscripts or superscripts in mathematical equation images.



## Idea

- Drawing a grid on the image might help ChatGPT recognize positional information more accurately.



## Requirements

- python package
  - sympy
  - pillow

- latex program
  - https://www.latex-project.org/get/



## Codes

### random_expression_generator.py

This is code that generates complex mathematical equations and saves them as images.

#### Functions

- generate_random_expression

  A recursive function that generates a random LaTeX equation and saves it as an image.

  - parameters
    - level: Not used. To indicate the difficulty of the formula.
    - length: Length of the formula. (0: a constant number, 1: x)
    - problem_path: Path of the problem image.
    - solution_path: Path of the solution image.
    - evalf_path: Path of the evaluation image.
    - save: boolean variable, save or not



### image_grid_drawer.py

This is code that draws a grid on an image file.
