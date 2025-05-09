AI vs ML vs DL
| Category          | Description                    | Examples                     |
| ----------------- | ------------------------------ | ---------------------------- |
| AI                | Machines mimic human abilities | Self-driving cars, chatbots  |
| ML (subset of AI) | Learn from data                | Spam filters, credit scoring |
| DL (subset of ML) | Deep neural networks           | Image recognition, ChatGPT   |

Types of Machine Learning
| Type          | How It Works                    | Examples                    |
| ------------- | ------------------------------- | --------------------------- |
| Supervised    | Learn from labeled data         | Fraud detection, approvals  |
| Unsupervised  | Find patterns in unlabeled data | Customer clusters, trends   |
| Reinforcement | Learn via trial & error         | Game AI, autonomous driving |

AI Domains & Tasks
| Domain       | Tasks                            | Models                        |
| ------------ | -------------------------------- | ----------------------------- |
| Language     | Translation, Q\&A, summarization | RNN, LSTM, Transformers       |
| Audio/Speech | Speech-to-text, synthesis        | RNN, LSTM, VAEs, Transformers |
| Vision       | Image classification, detection  | CNN, YOLO, GAN                |

Core Data Concepts
| Data Type | Details                           |
| --------- | --------------------------------- |
| Text      | Tokenization, embeddings, padding |
| Audio     | Sample rate, bit depth            |
| Images    | Pixels, grayscale/color, features |

Special Applications
| Task              | Use Case                      |
| ----------------- | ----------------------------- |
| Anomaly Detection | Fraud, machine failures       |
| Recommendations   | Product/content suggestions   |
| Forecasting       | Weather, stock predictions    |
| Generative AI     | Text, image, music generation |

Model Summary
| Model        | Purpose                        |
| ------------ | ------------------------------ |
| RNN          | Sequential data (text, audio)  |
| LSTM         | Long-term sequence retention   |
| Transformers | Contextual parallel processing |
| CNN          | Visual pattern recognition     |
| YOLO         | Real-time object detection     |
| GAN          | Realistic data generation      |

**Key Points  : AI ⊃ ML ⊃ DL; align tasks with correct data & models; know real-world applications.

Reinforcement Learning Overview
|   Term                |   Description                                                                                |
| --------------------- | -------------------------------------------------------------------------------------------- |
|   Agent               | Learner/decision-maker interacting with the environment.                                     |
|   Environment         | External system the agent interacts with (e.g., road for self-driving car).                  |
|   State               | Current situation or configuration of the environment.                                       |
|   Actions             | Possible decisions or moves the agent can take in a state.                                   |
|   Policy              | Strategy or mapping that tells the agent which action to take in a given state.              |
|   Rewards/Penalties   | Feedback from the environment, rewarding desirable outcomes and penalizing undesirable ones. |

Real-World Examples:
|   Application              |   Description                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------ |
|   Autonomous Vehicles      | RL helps self-driving cars make real-time decisions based on sensor data and traffic conditions. |
|   Smart Home Devices       | RL adapts virtual assistants like Alexa, Google Assistant, and Siri to users' preferences.       |
|   Industrial Automation    | RL optimizes robots and control systems in manufacturing, enhancing efficiency.                  |
|   Gaming & Entertainment   | RL creates intelligent NPCs that learn from player behavior to increase game difficulty.         |

Key Concepts:
*   Exploration vs. Exploitation  : Balancing new actions (exploration) vs. known rewarding actions (exploitation).
*   Discount Factor  : Future rewards are discounted to prioritize immediate rewards.

Example of Training a Self-Driving Car:
|   Component     |   Description                                        |
| --------------- | ---------------------------------------------------- |
|   Agent         | Self-driving car                                     |
|   Environment   | Road and surroundings                                |
|   State         | Camera images of the road                            |
|   Actions       | Steer left, right, or keep straight                  |
|   Policy        | Strategy the car learns to follow for driving safely |

RL in Robotics Example:
|   Component           |   Description                                      |
| --------------------- | -------------------------------------------------- |
|   Agent               | Robotic arm                                        |
|   Environment         | Warehouse with items to place                      |
|   State               | Arm’s position, item location                      |
|   Actions             | Move the arm to pick up or place items             |
|   Rewards/Penalties   | Reward for correct placement, penalty for mistakes |

Algorithms:
|   Algorithm         |   Description                                                              |
| ------------------- | -------------------------------------------------------------------------- |
|   Q-Learning        | Learns values of actions in states to find the optimal policy.             |
|   Deep Q-Learning   | Uses deep neural networks to approximate the values in large state spaces. |

