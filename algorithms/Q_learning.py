import numpy as np
import pickle
from os import path

class Agent(object):
    def __init__(self, alpha, beta):
        self.alpha = alpha
        self.beta = beta

        self.TEMP_THRESHOLD = (60, 80)
        self.TEMP_SIZE = 10
        self.TEMP_STEP = int((self.TEMP_THRESHOLD[1] - self.TEMP_THRESHOLD[0])/self.TEMP_SIZE)
        self.CPU_SIZE = 10
        self.PWM_SET = [0, 50, 60, 70, 80, 90, 100]
        # self.PWM_STEP = 10

        if path.exists('algorithms/Q.pickle'):
            with open('algorithms/Q.pickle', 'rb') as pk:
                self.Q = pickle.load(pk) 
        else:
            self.Q = np.zeros((self.TEMP_SIZE,self.CPU_SIZE,len(self.PWM_SET)))

        self.post_state = [0.,0.,0.]
        self.post_i = [0,0,0]
        self.post_q = 0
    
    def state_index(self, state):
        temp = state[0]
        cpu = state[1]
        if temp > self.TEMP_THRESHOLD[0] and temp < self.TEMP_THRESHOLD[1]:
            temp_i = (temp - self.TEMP_THRESHOLD[0]) / self.TEMP_STEP
        elif temp <= self.TEMP_THRESHOLD[0]:
            temp_i = 0
        else:
            temp_i = self.TEMP_SIZE

        cpu_i = cpu/self.CPU_SIZE
        
        return int(temp_i), int(cpu_i)

    def action_index(self, action):
        # pwm = action
        pwm_i = self.PWM_SET.index(action)
        return pwm_i

    def cost(self, temp, pwm):
        # temp_i, cpu_i, pwm_i = self.state_index(state)
        print(temp*temp + self.PWM_SET[pwm])
        return temp*temp + self.PWM_SET[pwm]

    def learning(self, state, action):
        temp_i, cpu_i = self.state_index(state)
        pwm_i = self.action_index(action)
        
        self.Q[ self.post_i[0], self.post_i[1], self.post_i[2] ] = \
            self.post_q + self.beta * ( self.cost(temp_i, pwm_i) + \
            self.alpha * self.Q[temp_i, cpu_i].min() - self.post_q )

    def save_q(self):
        with open('algorithms/Q.pickle', 'wb') as pk:
            pickle.dump(self.Q, pk, protocol=pickle.HIGHEST_PROTOCOL) 
        
    def greed(self, state):
        temp_i, cpu_i = self.state_index(state)
        pwm_i = np.argmin(self.Q[temp_i, cpu_i])
        self.post_q = self.Q[temp_i, cpu_i, pwm_i]
        self.post_i = [temp_i, cpu_i, pwm_i]
        return self.PWM_SET[pwm_i]
