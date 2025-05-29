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

Machine Learning Concepts Overview

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

![image](https://github.com/user-attachments/assets/644bd9d7-c7c5-4bbd-81f8-ef09d7baba69)

![image](https://github.com/user-attachments/assets/7982317a-fa20-4579-b436-f8928cf35eed)

# Transformer Architecture 

Transformer architecture has two main parts:

Encoder: Processes input text and creates embeddings.
Decoder: Uses embeddings to generate output text.

Key Concepts:

Tokens and Tokenization:
Tokens are units of text that can be whole words, subwords, or punctuation.
Simple texts have about 1 token per word; complex texts have 2–3 tokens per word.

Embeddings:
Embeddings are vector representations of text.
They are produced by encoder models and used in classification, semantic search, and vector databases.

Retrieval-Augmented Generation (RAG):
Uses vector databases and LLMs to answer queries.
Steps include encoding documents and queries, retrieving similar ones, and generating responses with LLMs.

Decoder Models:
These models generate one token at a time based on input sequences.
Used for tasks like text generation.

Encoder-Decoder Models:
Combine encoder and decoder components for sequence-to-sequence tasks like translation.
Encoder processes the input, decoder generates the output step-by-step.

Model Types and Use Cases:

| Model Type      | Function                  | Use Case                        |
| --------------- | ------------------------- | ------------------------------- |
| Encoder-only    | Understand input          | Search, classification, RAG     |
| Decoder-only    | Generate text             | Storytelling, summarization     |
| Encoder-decoder | Translate input to output | Translation, question answering |

Next topic will cover prompts and prompt engineering.

# Prompt Engineering 

Definition:
Prompt: Input text to the LLM.
Prompt Engineering: Iteratively refining the prompt to elicit a desired response.

LLMs trained for text completion predict next words, not necessarily follow instructions.

Instruction Tuning:
Fine-tunes LLMs to follow instructions by using prompt-response examples.
Involves Reinforcement Learning from Human Feedback (RLHF).
RLHF uses human preferences to train a reward model that aligns LLM behavior.

Prompting Techniques:

In-Context Learning:
Model uses context/examples provided in the prompt.
No model weights are updated.

Few-Shot Prompting:
Providing few examples (0-shot, 1-shot, k-shot) to guide model behavior.
Few-shot prompts generally perform better than zero-shot.

Chain-of-Thought Prompting:
Model is prompted to solve problems step-by-step.
Includes intermediate reasoning before final answer.
Useful for complex reasoning tasks.

Hallucination:
Model generates fluent but incorrect or ungrounded content.
Hard to detect; mitigated with retrieval-augmented methods.

Summary:
Covers importance of prompts, challenges in engineering them, instruction tuning (including RLHF), and techniques like few-shot and chain-of-thought prompting. Ends with addressing hallucination issues.

# Customizing LLMs with Your Own Data 

Framework:

* Two axes:

  * Horizontal axis: **Context Optimization** – Adding specific, detailed information such as user order history.
  * Vertical axis: **LLM Optimization** – Adapting LLMs for specific domains (e.g., legal) using fine-tuning.

## Key Method Definitions

**Retrieval-Augmented Generation (RAG)**
RAG combines a retrieval system (like a vector database) with a language model. At query time, relevant documents are retrieved based on the query and passed into the LLM as additional context. This allows the model to generate responses grounded in up-to-date or private data **without retraining the model**.

* **Key Idea:** Retrieve → Augment → Generate
* **Benefit:** Reduces hallucination, uses real-time data
* **Example:** A chatbot looks up company policy from a document database before answering a return request.

**Fine-Tuning**
Fine-tuning is the process of continuing training a pre-trained LLM on a smaller, **labeled**, domain-specific dataset. This adapts the model to perform better on tasks or in styles it wasn’t originally optimized for.

* **Key Idea:** Customize model weights with domain-specific data
* **Benefit:** Improves performance and relevance for specialized tasks
* **Example:** Training an LLM on legal case documents to generate legal summaries in specific formats.

## Comparison of Approaches:

| Method             | Description                                              | When to Use                                         | Advantages                                      | Disadvantages                              |
| ------------------ | -------------------------------------------------------- | --------------------------------------------------- | ----------------------------------------------- | ------------------------------------------ |
| Prompt Engineering | Crafting and iterating prompts to guide output           | LLM already understands the domain                  | No training cost, fast iteration                | Limited control, may not generalize        |
| RAG                | Augments prompts with context from private data sources  | When data changes often or to reduce hallucinations | Uses fresh/grounded data, no fine-tuning needed | Complex setup, needs good retrieval system |
| Fine-Tuning        | Adapting model weights with domain-specific labeled data | When LLM underperforms on domain-specific tasks     | High performance, custom style/tone             | Costly, requires labeled data and compute  |

Iterative Application:

* Start with prompt engineering and evaluation.
* Add few-shot examples if needed.
* Move to RAG if external/private knowledge is required.
* Fine-tune the model if style, format, or performance isn't sufficient.
* Optimize RAG system and iterate further.

This framework helps choose and combine methods to customize LLMs effectively for your own data.
