import crawler as Crawler
import agent as Agent

import pkg_resources
import time
import threading


def print_all_module_versions():
    print("Installed Packages:")
    print("===================")
    installed_packages = pkg_resources.working_set
    for package in installed_packages:
        print(f"{package.key} : {package.version}")
    print()



def main() -> int:
    #print_all_module_versions()

    model = 'gpt-3.5'
    gpt4_tabs = [
        'F634AA33A771E0B357AB34456D632A51',
        '503CF570207676C37CA2147F76A5C955',
        '3C48605445BF58A6DB186249AAFC21FC',
        '799D9EFB9D69C473688CD64135C93D42',
        '69539F4F2B3D522C56564BA0744F3D49'
    ]
    gpt3_tabs = [
        '1B4DF690BC13AB0DE7DE6BEC0CF47056',
        'A55BA2FEFE22D6D7A66B2F465165A6D3',
        '908A929A40B6355A0378D9124D068882',
        '7BACE35FE8FA29B4060B1C2F0D1A6AB8',
        'FF7A3BA01EB2D47ACDF0045DFD9C8B80'
    ]
    lock = threading.RLock()

    print('!')

    gpt_crawler = Crawler.GptCrawler(tabs=gpt3_tabs, lock=lock, debug_mode=False)
    
    print('!')
    gpt_crawler.print_window_handles()

    num_agents = 5
    agents = []
    for i in range(5):
        agents.append(Agent.GptAgent(gpt_crawler=gpt_crawler, tab_index=i, model=model, name=str(i)))
    
    while True:
        Agent.print_agents(agents=agents)

        agent = Agent.find_free_agent(agents=agents)
        if agent is not None:
            print('find free agent!')
            thread = threading.Thread(target=Agent.do_task, args=(agent, 'tell me some story.', [], lock))
            thread.start()

        time.sleep(1)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())