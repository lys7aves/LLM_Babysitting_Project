import sympy as sp
from sympy import latex, nan
import random
from pdf2image import convert_from_path
import os
import multiprocessing
import time


# Generate random equations recursively.
def generate_random_expression(level=1, length=None, problem_path='./random_problem', save=True):
    if length == None: length = random.randint(3,10)

    x = sp.symbols('x')
    operations = [sp.Add, sp.Mul, sp.Pow]  # 덧셈, 곱셈, 거듭제곱 중 랜덤 선택
    #functions = [sp.sin, sp.cos, sp.exp, sp.log]  # 삼각함수, 지수함수, 로그함수 등을 추가할 수 있음
    functions = [sp.sin, sp.cos]

    if save == True:
        while True:
            expr = generate_random_expression(level=level, length=length, problem_path=problem_path, save=False)
            series = sp.Sum(expr, (x, 1, 10))
            solution = series.doit()
            evalf = solution.evalf()

            if solution is not nan:
                break

        save_expression(expr=series, file_path=problem_path)
        with open(problem_path+'.txt', 'w') as file:
            file.write("#problem: " + latex(series) + '\n')
            file.write("#solution: " + latex(solution) + '\n')
            file.write("#evalf_avlue: " + latex(evalf) + '\n')
        
        return expr

    if length == 0:
        expr = random.randint(-10, 10)
    elif length == 1:
        expr = x
    else:
        r = random.randint(1, 5)
        if r <= 3:
            op = random.choice(operations)
            l1 = random.randint(0, length-1)
            l2 = length - l1 - 1

            expr1 = generate_random_expression(level=level, length=l1, save=False)
            expr2 = generate_random_expression(level=level, length=l2, save=False)

            expr = op(expr1, expr2)
            
        elif r <= 5:
            func = random.choice(functions)

            expr = generate_random_expression(level=level, length=length-1, save=False)
            expr = func(expr * sp.pi / 2)

    return expr


def save_expression(expr, file_path):
    # LaTeX 스타일로 수식 렌더링
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory {directory} created")
    
    # I don't know why it doesn't work when output='png'
    # So I save the formula as pdf first, then I read it and resave it as png file.
    pdf_path = './tmp/tmp.pdf'
    if not os.path.exists('./tmp'): os.makedirs('./tmp')
    sp.preview(expr, output='pdf', viewer='file', filename=pdf_path, euler=False)

    images = convert_from_path(pdf_path, first_page=1, last_page=1)
    images[0].save(file_path+'.png', 'PNG')

    print(f"'{file_path}' has been saved as '{expr}'")


def generate_random_expressions(dir_path='./random_problems/', number=10):
    for num in range(1, number+1):
        problem_path = dir_path + f'problem{num}'

        print(problem_path)
        
        complete = False
        while not complete:
            p = multiprocessing.Process(target=generate_random_expression(problem_path=problem_path, save=True))
            p.start()

            p.join(timeout=10)

            if p.is_alive():
                print("Function taking too long. Terminating...")
                p.terminate()
                p.join()
            
            else:
                complete = True



if __name__ == "__main__":
    dir_path = './formula_recognition/data/random_problems_v4/'
    generate_random_expressions(dir_path=dir_path, number=30)