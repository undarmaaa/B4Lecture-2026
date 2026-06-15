# Exercise 5 Report: Training and Comparison of a Self-Trained Soccer Event Prediction Model

## 1. Training Configuration

For this experiment, I trained my own NMSTPP model using the OpenSTARLab Event package. Compared with Exercise 4, I changed the training dataset by combining **England** and **Spain** league matches instead of using a single league. The motivation was to investigate whether increasing the amount and diversity of training data would improve the model's generalization ability.

The main training settings were:

* **Model:** NMSTPP
* **Training data:** England + Spain
* **Epochs:** 2
* **Sequence length:** 40
* **use_other_features:** True
* **Batch size:** 256

All other major hyperparameters were kept at their default values so that the effect of changing the training data could be evaluated more fairly.

---

## 2. Evaluation Match

To enable a fair comparison with Exercise 4, I evaluated the self-trained model on the **same match**:

* **Match ID:** 2565858

Using the identical evaluation match makes it easier to compare the behavior of the pretrained model and the self-trained model.

---

## 3. Quantitative Comparison

| Metric        | Pretrained Model | Self-trained Model |
| ------------- | ---------------: | -----------------: |
| Train Loss    |       **4.9958** |             7.9355 |
| CEL Action    |       **1.0343** |             1.2095 |
| RMSE ΔT       |       **0.2461** |             0.3848 |
| RMSE Location |       **0.2731** |             0.4802 |
| ACC Action    |       **0.6564** |             0.6187 |
| F1 Action     |       **0.1659** |             0.0849 |
| MAE ΔT        |           3.3013 |         **3.2417** |
| MAE X         |       **8.3570** |            20.7552 |
| MAE Y         |      **16.7950** |            26.6871 |

Overall, the pretrained model achieved better performance on most evaluation metrics. However, the self-trained model slightly outperformed the pretrained model in MAE for time prediction (ΔT), indicating that it learned temporal information reasonably well despite its limited training.

---

## 4. Visual Analysis

Three types of visualizations were generated for the selected match:

* Prediction vs. Actual Event Distribution
* HPUS
* HPUS+

The HPUS and HPUS+ visualizations successfully illustrated the predicted attacking potential throughout the match. The event distribution comparison showed that the self-trained model predicted the **short_pass** action much more frequently than other action types.

---

## 5. Discussion

Although the self-trained model was trained using a larger dataset containing both England and Spain matches, its overall performance remained below that of the provided pretrained model. A likely reason is that the model was trained for only two epochs, which is insufficient for full convergence. In contrast, the pretrained model was likely trained for substantially longer and with more extensive hyperparameter tuning.

The prediction results also revealed a strong bias toward the **short_pass** action. This behavior is consistent with the relatively low F1 score and suggests that the model had not yet learned to distinguish less frequent event types effectively. Additional training epochs, improved class balancing, or further hyperparameter optimization could help reduce this bias.

Despite the lower overall accuracy, this experiment successfully demonstrated the complete pipeline of preprocessing, training, inference, and quantitative evaluation using a customized multi-league dataset. It also highlighted the importance of sufficient training time and balanced learning when developing event prediction models.
