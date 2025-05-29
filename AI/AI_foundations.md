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

Key Points  : AI ⊃ ML ⊃ DL; align tasks with correct data & models; know real-world applications.

## Machine Learning Concepts Overview

Supervised Learning
|   Term              |   Description   |
|---------------------|-----------------|
|   Supervised Learning   | A machine learning technique where the model is trained on labeled data (input-output pairs). |
|   Regression        | Predicts continuous output. Example: House price prediction based on square footage. |
|   Classification    | Predicts categorical output. Example: Email classification as spam or not spam. |
|   Logistic Regression   | A model for binary classification using a sigmoid function to predict probabilities. |
|   Iris Dataset      | A famous dataset used for multi-class classification with flower types (Setosa, Versicolor, Virginica) based on features like sepal/petal size. |

Key Points:  
- Supervised learning learns the mapping from inputs to outputs.
- Linear regression uses a straight line to predict continuous values.
- Logistic regression uses an S-shaped curve (sigmoid) for classification.
  
Unsupervised Learning
|   Term              |   Description   |
|---------------------|-----------------|
|   Unsupervised Learning   | A machine learning technique where the model learns from unlabeled data, identifying patterns on its own. |
|   Clustering        | Groups similar data points. Common algorithms: K-Means, DBSCAN. |
|   Outlier Analysis   | Identifies unusual data points that do not belong to any cluster. |
|   Recommendation Systems   | Suggests items based on clustering of user preferences (e.g., Netflix movie recommendations). |

Examples:  
-   Market Segmentation  : Identifying groups of customers with similar purchasing behavior.
-   Fraud Detection  : Detecting outliers in financial transactions that may indicate fraud.

Process:  
1.   Data Preparation  : Preprocess and normalize the data.
2.   Similarity Metrics  : Measures such as Euclidean or Manhattan distance to quantify similarities.
3.   Clustering Algorithm  : Assigns data to clusters based on similarity.
4.   Evaluation & Iteration  : Clustering is iterative, as there are no labeled outputs to verify the results.

Reinforcement Learning
|   Term              |   Description   |
|---------------------|-----------------|
|   Reinforcement Learning   | A machine learning technique where an agent learns through interactions with the environment, receiving rewards or penalties based on actions. |
|   Agent             | The decision-maker or learner that interacts with the environment. |
|   Environment       | The external system the agent interacts with. |
|   State             | The current situation of the agent in the environment. |
|   Actions           | The set of possible moves the agent can make in a state. |
|   Policy            | The strategy used by the agent to decide which action to take. |

  Real-World Examples:  
-   Autonomous Vehicles  : Self-driving cars use reinforcement learning to make decisions based on sensor data.
-   Smart Home Devices  : Virtual assistants (Alexa, Google Assistant) learn user preferences to improve interactions.
-   Robotics in Manufacturing  : RL helps robots optimize task completion such as moving items in a warehouse.

  Training Process:  
1.   Environment Setup  : Define the agent, state space, actions, and rewards.
2.   Learning  : Agent explores different actions and receives feedback (rewards or penalties).
3.   Optimal Policy  : Over time, the agent learns the best policy to maximize rewards.

  Example - Self-Driving Car  :
-   Agent  : Car
-   Environment  : Road with obstacles
-   State  : Camera feed of the road
-   Actions  : Steer left, right, or keep straight
-   Policy  : Decision-making process based on current view to navigate safely.

  Algorithms  :
-   Q-Learning  : Learns the value of actions in states to find the optimal policy.
-   Deep Q-Learning  : Uses deep neural networks to approximate action values in complex environments.

![image](https://github.com/user-attachments/assets/9c195bd6-b3eb-487e-b394-5ec2dc308f69)

