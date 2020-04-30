#File contains class to train NN using MCTS
from .configs import *
from .mcts import *

class Train(object):

    def __init__(self, gas_network, nnet):
        self.gas_network = gas_network
        self.net = nnet

    def start(self):
        #Main training function

        training_data = []

        for i in range(CFG.num_self_plays):

            gas_network = self.gas_network.clone()
            self.self_play(gas_network, training_data)

        self.net.save_model()

        #self.net.train(training_data)

    def self_play(self, gas_network, training_data):

        mcts = MCTS(self.net)
        self_play_data = []

        node = TreeNode()

        count = 0
        iteration_over = False

        while not iteration_over: #Infinite loop

            if count < CFG.temp_threshold:
                best_child = mcts.search(gas_network, node, CFG.temp_initial)
            else:
                best_child = mcts.search(gas_network, node, CFG.temp_final)

            self_play_data.append([deepcopy(gas_network.state), deepcopy(best_child.parent.child_psas), 0])

            action = best_child.action

            gas_network.take_action(action)
            count += 1

            iteration_over, value = gas_network.get_reward()

            best_child.parent = None
            node = best_child    #Make the child node the root node

        # Update v as the value of the game result
        for state_value in self_play_data:
            value = -value
            state_value[2] =  value
            state = deepcopy(state_value[0])
            psa_vector = deepcopy(state_value[1])
            training_data.append([state, psa_vector, state_value[2]])
