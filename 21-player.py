import random
from maingame import card_handler
import numpy as np
import torch
import math

cards = ['A',2,3,4,5,6,7,8,9,10,'J','Q','K']


def judgement(main_p, player_p):
    m = main_p
    p = player_p
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

carder = card_handler()  #荷官

learning_rate = 0.1
discount_factor = 1
epsilon = 0.2
num_episodes = 500000

player_q = torch.zeros((32, 11, 10, 2, 2))        #状态空间：（玩家点数，庄家明牌点数，玩家A数量，庄家A数量，是否要牌） 创建时点数需要+1

#发牌
for e in range(num_episodes):

    main_c,player_c = carder.init_card()
    if e == 200 or e == 1000:
        print('庄家的初始明牌是：'+ str(main_c[0]) + ' 暗牌是' + str(main_c[1]))
        print('玩家的初始手牌是：'+ str(player_c))

    main_p, player_p = carder.calculate(main_c,player_c)

    main_A = 0
    player_A = 0

    for i in player_c:
        if i == 'A':
            player_A+=1

    ob_card = main_c[0]
    if ob_card == 'A':
        main_op = 10
        main_A +=1
    elif ob_card=='J' or ob_card=='Q' or ob_card=='K':
        main_op = 10
    else:
        main_op = ob_card

    choose_reward = 0
    main_done = 0
    player_done = 0
    while not player_done:
        player_action = 0
        epsilon = max(0.05, 0.5 * (1 - e / num_episodes))
        if np.random.rand() < epsilon:
            player_action = np.random.randint(0, 2)
        else:
            player_action = torch.argmax(player_q[player_p, main_op,player_A,main_A]).item()
        if player_p <= main_op or player_p < 11:
            player_action = 1

        p = player_p
        if player_action == 1:
            new_card = carder.give_a_card()
            choose_reward +=1
            if new_card == 'A':
                player_A +=1
            player_c.append(new_card)
            main_p, player_p = carder.calculate(main_c, player_c)

            if player_p > 21:
                # 玩家爆21
                player_done = True
                main_done = True
                main_action = 0
        else:
            player_done = True

        # 单步进行奖励##
        old_value = player_q[p,main_op,player_A,main_A, player_action]
        next_max = torch.max(player_q[player_p,main_op,player_A,main_A, player_action])
        new_value = (1 - learning_rate) * old_value + learning_rate * (discount_factor * next_max + choose_reward * 0.1)
        player_q[p,main_op,player_A,main_A, player_action] = new_value

    while not main_done:
        if main_p < 17:
            new_card = carder.give_a_card()
            main_c.append(new_card)
            main_p, player_p = carder.calculate(main_c, player_c)
        else:
            main_done = 1

    main_p,player_p = carder.calculate(main_c, player_c)
    main_reward, player_reward = judgement(main_p, player_p)
    if player_reward > 0:
        player_reward += choose_reward *0.1
            # 玩家奖励
    old_value = player_q[player_p, main_op, player_A, main_A, player_action]
    new_value = (1 - learning_rate) * old_value + learning_rate * player_reward
    player_q[player_p, main_op, player_A, main_A, player_action] = new_value


    if e == 200 or e == 1000:
        print('庄家的手牌是：' + str(main_c) + '点数是' + str(main_p))
        print('玩家的手牌是：' + str(player_c) + '点数是' + str(player_p))
        if main_reward == 1:
            print('庄家胜利！')
        elif main_reward == 0:
            print('平局')
        else:
            print('玩家胜利!')

torch.save(player_q, 'player-q.pt')

