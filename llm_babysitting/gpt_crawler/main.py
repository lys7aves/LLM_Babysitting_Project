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
        '3F049EE98ADB613066652F61AD79200E',
        '3D897ACC0E634348A31B9299A0BE431E',
        '676187D98B32EB6A19A648C50E1562B2',
        'CEACA1BD56CED3DE648F7C0D9E2047EB',
        'FB27AE25BC446E90BFC27D518E79680B'
    ]

    gpt_crawler = Crawler.GptCrawler(tabs=gpt3_tabs, debug_mode=True)
    #gpt_crawler.print_window_handles()

    num_agents = 5
    agents = []
    for i in range(5):
        agents.append(Agent.GptAgent(gpt_crawler=gpt_crawler, tab_index=i, model=model, name=str(i)))
    
    while True:
        Agent.print_agents(agents=agents)

        agent = Agent.find_free_agent(agents=agents)
        if agent is not None:
            print('find free agent!')
            thread = threading.Thread(target=Agent.do_task, args=(agent, 'tell me some story.'))
            thread.start()

        time.sleep(10)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())