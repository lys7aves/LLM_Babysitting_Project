from PIL import Image, ImageDraw

def draw_grid(image_path, output_path, rows=1, cols=1):
    # 이미지 열기
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)

    width, height = img.size

    # 격자 그리기
    for i in range(1, cols+1):
        x = width*i/cols
        draw.line([(x, 0), (x, height)], fill="red", width=1)
    for i in range(1, rows+1):
        y = height*i/rows
        draw.line([(0, y), (width, y)], fill="red", width=1)

    # 그려진 격자가 있는 이미지 저장
    img.save(output_path, "PNG")
    print(f"격자가 그려진 이미지를 {output_path}에 저장했습니다.")



if __name__ == "__main__":
    # 이미지 파일 경로와 저장할 경로, 격자 크기 지정
    rows = 7
    cols = 11
    image_path = "./formula_recognition/data/random_problem1.png"  # 이미지 파일 경로 설정
    output_path = f"./formula_recognition/data/random_problem1_{rows}by{cols}.png"  # 저장할 이미지 경로 설정

    # 격자를 그려서 저장하는 함수 호출
    draw_grid(image_path, output_path, rows=rows, cols=cols)