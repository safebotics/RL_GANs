import rl_gans.model.modules as m
import torch
import torch.nn as nn

class SAC_Model(nn.Module):
    def __init__(self, obs_shape, action_shape, hidden_dim, encoder_feature_dim, log_std_min, log_std_max, num_layers, num_filters, device):
        super().__init__()

        if len(obs_shape) == 3:
            shared_cnn = m.SharedCNN(obs_shape = obs_shape,
                                    num_layers = num_layers,
                                    num_filters = num_filters)

            actor_encoder = m.Encoder(cnn = shared_cnn,
                                    projection= m.RLProjection(shared_cnn.out_dim, encoder_feature_dim))
            
            critic_encoder = m.Encoder(cnn = shared_cnn,
                                    projection = m.RLProjection(shared_cnn.out_dim, encoder_feature_dim))

            critic_encoder_target = m.Encoder(cnn = m.SharedCNN(obs_shape = obs_shape, num_layers = num_layers, num_filters = num_filters),
                                            projection = m.RLProjection(shared_cnn.out_dim, encoder_feature_dim))

        else:
            actor_encoder = None 
            critic_encoder = None
            critic_encoder_target = None

        self.actor = m.Actor(encoder = actor_encoder,
                             obs_dim    = obs_shape[0],
                             action_dim = action_shape[0],
                             hidden_dim = hidden_dim,
                             log_std_min = log_std_min,
                             log_std_max = log_std_max).to(device)
        
        self.critic = m.Critic(encoder = critic_encoder,
                               obs_dim    = obs_shape[0],
                               action_dim = action_shape[0],
                               hidden_dim = hidden_dim).to(device)
        
        self.critic_target = m.Critic(encoder = critic_encoder_target,
                                      obs_dim    = obs_shape[0],
                                      action_dim = action_shape[0],
                                      hidden_dim = hidden_dim).to(device)
        self.critic_target.load_state_dict(self.critic.state_dict())


    def soft_update_params(self, critic_tau, encoder_tau):
        for param, target_param in zip(self.critic.Q1.parameters(), self.critic_target.Q1.parameters()):
            target_param.data.copy_(critic_tau * param.data + (1 - critic_tau) * target_param.data) 
            
        for param, target_param in zip(self.critic.Q2.parameters(), self.critic_target.Q2.parameters()):
            target_param.data.copy_(critic_tau * param.data + (1 - critic_tau) * target_param.data)   

        if self.critic.encoder is not None:
            for param, target_param in zip(self.critic.encoder.parameters(), self.critic_target.encoder.parameters()):
                target_param.data.copy_(encoder_tau * param.data + (1 - encoder_tau) * target_param.data)   
    