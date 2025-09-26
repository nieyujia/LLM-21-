import random
from maingame import card_handler

cards = ['A',2,3,4,5,6,7,8,9,10,'J','Q','K']

def judgement(main_p, player_p):
    if main_p > 21:
        main_p = -1
    if player_p > 21:
        player_p = -1
    if main_p > player_p:
        return 1,-1
    elif main_p == player_p:
        return 0,0
    else:
        return -1,1


if __name__ == '__main__':
    ###预设部分
    import json
    from openai import OpenAI

    carder = card_handler()  #荷官
    client = OpenAI(
        api_key="your_api_key",
        base_url="https://api.deepseek.com",
    )
    times = 100
    win = 0
    equal = 0
    lose = 0
    gets = 0
    #发牌
    for t in range(times):
        print(t)
        main_c,player_c = carder.init_card()

        main_p, player_p = carder.calculate(main_c, player_c)


        system_prompt = """
        你现在正在玩21点游戏，你的角色是玩家，规则如下：
        扑克牌的种类为cards = ['A',2,3,4,5,6,7,8,9,10,'J','Q','K']
        游戏开始时会分给庄家和玩家各发2张牌，玩家只能看到庄家的一张明牌和自己的两张牌，庄家不知道玩家的手牌。
        玩家先进行回合，根据场上信息选择是否要牌，如果选择要牌则会随机发给一张，直到玩家选择不要牌则玩家回合结束。
        然后庄家进行回合，庄家的策略：庄家点数低于某个点数则一直要牌，直到手牌到达某个点数或者爆牌则停止。
        最后进行结算点数，规则如下：玩家和庄家的手牌组成不超过21的最大的点数，其中'A'即可以当作1也可以当做10，'J','Q','K'均当做10点。
        如果有人超过21点，则称为爆牌。如果两家均爆牌则平局，仅一家爆牌则另一家胜利，均未爆牌则比较点数大小，大者胜利。
        我将会提供给你场上目前的信息，包括你的手牌和庄家的明牌，请你选择是否要牌，动作空间{0,1}，其中1表示要牌，0表示不要牌结束回合。并使用json的形式返回结果，下面是示例
    
        示例输入:
        庄家明牌：5 玩家当前手牌：['A',6]
    
        示例json输出:
        {
            "场况": "庄家明牌：5，玩家当前手牌：['A',6]",
            "玩家选择": 1
        }
        """

        messages = [{"role": "system", "content": system_prompt},]


        player_choice = 1
        while player_choice!=0:
            user_prompt = "庄家明牌：" + str(main_c[0]) + " 玩家当前手牌：" + str(player_c)
            messages.append({"role": "user", "content": user_prompt})
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True,
                response_format={
                'type': 'json_object'
                }
            )

            collected_chunks = []
            for chunk in response:
                if chunk.choices[0].delta.content:
                    collected_chunks.append(chunk.choices[0].delta.content)

            # 合并所有块内容
            full_response = "".join(collected_chunks)


            # 解析JSON
            response_json = json.loads(full_response)

            # 提取玩家选择
            player_choice = response_json.get("玩家选择")

            if player_choice==-1:
                print('模型未输出结果！')
                exit(0)
            if player_choice==1:
                gets+=1
                new_card = carder.give_a_card()
                player_c.append(new_card)
                del messages[1]


        main_done = 0
        while not main_done:
            if main_p < 17:
                new_card = carder.give_a_card()
                main_c.append(new_card)
                main_p, player_p = carder.calculate(main_c, player_c)
            else:
                main_done = 1




        main_p,player_p = carder.calculate(main_c, player_c)

        main_reward, player_reward = judgement(main_p, player_p)

        if main_reward == 1:
            lose += 1
        elif main_reward == 0:
            equal += 1
        else:
            win += 1

    print('大模型方法->共100局：玩家胜利' + str(win) + '局', '，平' + str(equal) + '局' + ',输' + str(lose) + '局')
    print('总要牌次数：' + str(gets))