import random
from maingame import card_handler
import numpy as np
import torch


win = 0
equal = 0
lose = 0
times = 0
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

carder = card_handler()  #荷官

player_q = torch.load('player-q.pt',weights_only=True)

for e in range(10000):

    main_c,player_c = carder.init_card()

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

    player_done = 0
    main_done = 0

    while not player_done:

        player_action = torch.argmax(player_q[player_p, main_op,player_A,main_A]).item()
        if player_p <= main_op or player_p < 11:
            player_action = 1
        p = player_p
        if player_action == 1:
            times +=1
            new_card = carder.give_a_card()

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

    while not main_done:
        if main_p < 17:
            new_card = carder.give_a_card()

            main_c.append(new_card)
            main_p, player_p = carder.calculate(main_c, player_c)
        else:
            main_done = 1



    main_p,player_p = carder.calculate(main_c, player_c)
    main_reward, player_reward = judgement(main_p, player_p)



    if main_reward==1:
        lose +=1
    elif main_reward==0:
        equal +=1
    else:
        win +=1

print('强化学习方法->共10000局：玩家胜利' + str(win) + '局','，平' + str(equal)+ '局' + ',输' + str(lose) + '局')
print('总要牌次数' + str(times))