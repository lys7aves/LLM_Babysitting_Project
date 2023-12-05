from gpt_crawler.crawler import GptCrawler
from gpt_crawler.agent import GptAgent

# experiment에 어떤 task를 어떤 method로 해볼지만 정하면 실험을 진행해주는 함수를 만드는게 개인적인 최종 목표

# data_generators 말고 task_generators를 만드는게 더 좋을거 같기도 하네요
# Before
#   /data_generators
#   /data_augmentors
# After
#   /task_generators > task와 solution 제작
#   /methos > task_generators에서 만든 task에 추가로 덧붙여서 task 제작 (data augment도 method에 맞게 augment)
#     ex, /methods/step_by_step_method.py > task에 "step by step" 만 덧붙여서 task 제작

# 큰 파이프라인인 experiment를 제작해주시면 제가 거기에 맞춰서 필요한 함수를 만들어도 될거 같기도 하고,
# 아래와 같은 파이프라인이라고 생각하고 task_generator나 method를 짜주셔도 될거 같아요.
# 프로젝트를 많이 진행해보지 않아서 설계가 엉성한데 의견 있으면 언제든 말씀해주시거나 반영해주셔도 될 것 같습니다.
# gpt_crawler를 안정적으로 만들어야 다른 모든게 될텐데.... 최대한 빨리 정확히 만들어보겠습니다

def experiment(task_generator='calculate_expression', method='step_by_step', num_agents=5, num_data=30):

    gpt_crawler = GptCrawler()
    agents = []
    for i in range(num_agents):
        agents.append(GptAgent(gpt_crawler=gpt_crawler))


    # generate task
    # - data/task_{}/tasks/...
    # - dtat/task_{}/solutions/...


    # regenerate task by the method
    # - data/task_{}/tasks_by_{method}/...
    # or
    # - data/task_{}/tasks/..._by_{method}
    # - data/taks_{}/solutions/..._by_{method}


    # do task
    # - data/taks_{}/results/...


    # check accuracy
    # - data/task_{}/result.csv


    return


if __name__ == "__main__":
    experiment()