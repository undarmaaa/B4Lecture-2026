# What

Implemented soccer tracking data visualization using Deep-EIoU output as per ex2 requirements.

This pull request includes:
1. Drawing player trajectories based on Deep-EIoU output.
1. Plotting speed and acceleration for a specified player.
1. Plotting "corrected" speed and acceleration for the same player.

This work use uv as python project manager. Please make sure uv is installed and configured in your environment. You can run following commands to set up the environment and run the code:

```bash
uv sync
uv run main.py
```

This will run both ex2 problem solutions.

# Results

1. Player Trajectory Visualization:
   - Created Player trajectory visualization based on Deep-EIoU output for first 20 seconds of the match.
   - The visualization includes 6 samples of player trajectories, with each player represented by a unique color.
   - The trajectory is saved as "player_trajectories.png".

   Analysis:
   - The trajectories of the players with ID (3, 5, 6) show almost smooth paths, indicating consistent movement patterns.
   - The trajectories of the players with ID (12, 15, 29) show a "jump" in the middle of the trajectory, which may indicate a tracking error or a sudden change in movement.

2. Speed and Acceleration Plot:
   - Calculated speed and acceleration for player with track_id (3, 5, 6, 12, 15, 29).
   - Plotted speed and acceleration over frames.
   - Do interpolation to fix the "jump" in the speed and acceleration for player with ID (12, 15, 29).
   - The resulting graph is saved as "player_speed_acceleration_no_smoothing.png" and "player_speed_acceleration_interpolated.png".

   Analysis:
   - The speed and acceleration plots for players with ID (3, 5, 6) show while not perfectly smooth with many jitters, they do not have any significant jumps, indicating consistent tracking.
   - The speed and acceleration plots for players with ID (12, 15, 29) show significant jumps, which may indicate tracking errors or sudden changes in movement. After interpolation, the speed and acceleration plots for these players show smoother curves, suggesting that the interpolation successfully mitigated the tracking errors.

# References

- [OpenSTARLab](https://openstarlab.readthedocs.io/en/latest/index.html) (_for plot pitch code_)