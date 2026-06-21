# Exercise 6 Report: Soccer Trajectory Prediction Challenge 2025

## Overview

In this exercise, I used the baseline RNN trajectory prediction model provided in the Soccer Trajectory Prediction Challenge 2025 notebook. The objective was to investigate how the length of the observation window (`burn_in`) influences trajectory prediction performance. The model was evaluated using the official evaluation metrics, and an extended evaluation was performed to analyze prediction errors separately for the ball, left team, and right team.

---

## Experimental Settings

The baseline configuration was:

* Model: RNN
* Number of epochs: 10
* Prediction horizon (`t_step`): 60
* Challenge dataset: `test_old/input`

To analyze the influence of temporal context, three different observation lengths were evaluated:

| Experiment   | Burn-in |
| ------------ | ------- |
| Experiment 1 | 20      |
| Baseline     | 30      |
| Experiment 2 | 40      |

All other parameters remained unchanged to ensure a fair comparison.

---

## Evaluation Results

### Overall Evaluation

| Burn-in | Average Error ↓ | Endpoint Error ↓ |
| ------: | --------------: | ---------------: |
|      20 |          8.8174 |          23.3158 |
|      30 |          5.3027 |           9.2168 |
|      40 |      **3.7217** |       **7.0088** |

The results show a clear improvement as the observation window increased. Using only 20 observed frames resulted in the largest prediction errors, while increasing the observation window to 40 frames achieved the best overall performance.

---

### Group-wise Evaluation

To better understand the model's behavior, I extended the official evaluation script to compute prediction errors separately for the ball, left team, and right team.

| Burn-in |     Ball ↓ | Left Team ↓ | Right Team ↓ |
| ------: | ---------: | ----------: | -----------: |
|      20 |    13.3134 |      8.4087 |       9.5854 |
|      30 |    10.8601 |      4.7975 |       5.2385 |
|      40 | **7.6165** |  **3.3676** |   **3.7617** |

The ball consistently exhibited the highest prediction error, while player trajectories were predicted more accurately. Increasing the observation window reduced prediction errors for all object groups.

---

## Trajectory Visualization

The input trajectories, ground truth trajectories, and predicted trajectories were visualized for three challenge sequences (01.csv, 02.csv, and 03.csv).

The visualizations showed that increasing the observation window improved the alignment between predicted trajectories and the ground truth, especially during longer continuous movements. In contrast, predictions generated using only 20 observed frames deviated more noticeably from the ground truth.

---

## Discussion

The experimental results indicate that increasing the observation window provides the RNN with richer temporal information, allowing it to estimate future trajectories more accurately. Both the Average Error and Endpoint Error decreased consistently as the burn-in increased from 20 to 40 frames.

The group-wise evaluation revealed that the ball was consistently the most difficult object to predict. This is expected because the ball moves faster than players, frequently changes direction, and is strongly influenced by player interactions such as passes and kicks. In contrast, player movements are generally smoother and more constrained by tactical positioning, making them easier for the model to predict.

Overall, the experiment demonstrates that extending the observation window significantly improves trajectory prediction performance. Among the evaluated settings, a burn-in of 40 frames achieved the best performance across all evaluation metrics, suggesting that additional temporal context helps the RNN better capture motion patterns in soccer trajectories.
