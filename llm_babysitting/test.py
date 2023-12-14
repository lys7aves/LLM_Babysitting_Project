

from PIL import Image, ImageOps
import os



def test1():
    base_path = 'C:/Users/SAMSUNG/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/llm_babysitting/data/task_1/tasks/'

    # 이미지를 10x10 그리드로 배치하기 위해 이미지 크기 계산
    width, height = Image.open(base_path + 'problem3.png').size
    border_size = 1

    new_width = width * 10 + border_size * 11
    new_height = height * 10 + border_size * 11
    new_image = Image.new('RGB', (new_width, new_height), (0, 0, 0))

    # 이미지를 10x10 그리드에 배치
    for i in range(10):
        for j in range(10):
            image_path = base_path + f'problem3_{i+1}_{j+1}.png'
            img = Image.open(image_path)
            img_with_border = ImageOps.expand(img, border=border_size, fill='black')
            new_image.paste(img_with_border, (j * (width + border_size), i * (height + border_size)))

    new_image.show()

    new_image.save(base_path+'lattice_augmentation_1.png')



def find_files_with_string(directory, search_string):
    matching_files = []

    # 디렉토리의 모든 파일 탐색
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # 파일인 경우에만 처리
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    # 파일 내용에서 검색 문자열 찾기
                    file_content = file.read()
                    if search_string in file_content:
                        matching_files.append(filepath)
            except Exception as e:
                print(f"Error reading file {filepath}: {e}")

    return matching_files


def test2():
    # 디렉토리 경로와 검색할 문자열 설정
    directory_path = 'C:/Users/SAMSUNG/OneDrive/바탕 화면/Lecture/2023-2/2023-2 Natural Language Processing (001)/project/LLM_Babysitting_Project/llm_babysitting/data/task_1/have_url_but_not_recent_prompt/'
    search_string = "OCR"

    # 검색 실행
    result = find_files_with_string(directory_path, search_string)

    # 결과 출력
    if result:
        print("Files with the specified string:")
        for file_path in result:
            print(file_path)
    else:
        print("No files found with the specified string.")



if __name__ == "__main__":
    #test1()
    test2()