# Exercise 4 Report

## Problem 1: Change in Preprocessing

In this exercise, the default England Wyscout dataset was replaced with the Spain (La Liga) dataset. To achieve this, the preprocessing script was modified so that the England event and match files were removed while the Spain files were retained.

The following files were used during preprocessing:

* `events_Spain.json`
* `matches_Spain.json`

After preprocessing with the UIED pipeline, the reprocessed dataset `data.csv` was successfully generated.

### Summary of Reprocessed Data

| Item                         |           Value |
| ---------------------------- | --------------: |
| League                       | Spain (La Liga) |
| Number of matches            |             380 |
| Number of rows in `data.csv` |         558,092 |

---

## Problems 2 & 3: Match Selection and Inference

### Selected Match

For qualitative analysis, Match ID `2565858` was selected from the test dataset because it contained one of the largest numbers of event sequences among the available matches.

### Inference Settings

The pretrained NMSTPP model provided in the notebook was used for inference. Additional model training and Optuna optimization were not performed in this exercise.

### Inference Results (`loss_df`)

| Metric        |  Value |
| ------------- | -----: |
| train_loss    | 4.9958 |
| CEL_action    | 1.0343 |
| RMSE_deltaT   | 0.2461 |
| RMSE_location | 0.2731 |
| ACC_action    | 0.6564 |
| F1_action     | 0.1659 |
| MAE_deltaT    | 3.3013 |
| MAE_x         |  8.357 |
| MAE_y         | 16.795 |

The results indicate that the pretrained model achieved relatively stable action and spatial prediction performance on the Spain dataset.

---

## Problem 4: Visual Analysis

### Generated Visualizations

The following visualizations were generated:

1. HPUS plot (`HPUS.png`)
2. HPUS+ plot (`HPUS_plus.png`)
3. Prediction vs. actual event distribution comparison (`event_comparison.png`)

### HPUS Analysis

The HPUS visualization showed that the home team generated larger offensive momentum peaks than the away team, especially around the 10th and 80th minutes. In contrast, the away team produced more moderate but relatively stable offensive sequences throughout the match.

### HPUS+ Analysis

The HPUS+ visualization emphasized only highly dangerous attacking situations. Compared to HPUS, many intervals became zero, indicating that only a limited number of possessions were considered highly threatening. The home team still exhibited stronger attacking peaks overall.

### Prediction vs. Actual Event Comparison

The comparison between actual and predicted event distributions showed that the pretrained NMSTPP model successfully captured the dominance of short-pass actions in the selected match. The predicted distribution generally followed the overall tendency of the ground-truth events.

However, discrepancies were also observed. In particular, the model predicted cross actions more frequently than they appeared in the actual data, while actions such as dribble, high pass, and long pass were underrepresented in the predictions. These results suggest that the model was able to learn broad event occurrence patterns, but distinguishing less frequent or more complex action types remained challenging.
