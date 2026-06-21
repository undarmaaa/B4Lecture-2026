import glob, os
import argparse

import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--n_roles', type=int, default=23)
parser.add_argument('--burn_in', type=int, default=0)
parser.add_argument('--submit', type=str, required=True)
parser.add_argument('--gt', type=str, required=True)
parser.add_argument('--input', type=str, required=True)
args, _ = parser.parse_known_args()


def get_csv_files(folder):
    return sorted(glob.glob(os.path.join(folder, '*.csv')))


def compute_errors(submit_df, gt_df, agents_list, burn_in):
    errors = []
    endpoint_errors = []

    for agent in agents_list:
        if not 'r' in agent:  # official metric: left agents + ball
            x_pred = submit_df[f'{agent}_x'].values
            y_pred = submit_df[f'{agent}_y'].values
            x_gt = gt_df[f'{agent}_x'].values
            y_gt = gt_df[f'{agent}_y'].values

            distances = np.sqrt(
                (x_pred[burn_in:] - x_gt[burn_in:]) ** 2 +
                (y_pred[burn_in:] - y_gt[burn_in:]) ** 2
            )
            errors.append(distances)

            end_distance = np.sqrt(
                (x_pred[-1] - x_gt[-1]) ** 2 +
                (y_pred[-1] - y_gt[-1]) ** 2
            )
            endpoint_errors.append(end_distance)

    return np.mean(np.concatenate(errors)), np.mean(endpoint_errors)


def compute_group_errors(submit_df, gt_df, agents_list, burn_in):
    group_errors = {
        "ball": [],
        "left": [],
        "right": []
    }

    for agent in agents_list:
        x_pred = submit_df[f'{agent}_x'].values
        y_pred = submit_df[f'{agent}_y'].values
        x_gt = gt_df[f'{agent}_x'].values
        y_gt = gt_df[f'{agent}_y'].values

        distances = np.sqrt(
            (x_pred[burn_in:] - x_gt[burn_in:]) ** 2 +
            (y_pred[burn_in:] - y_gt[burn_in:]) ** 2
        )

        if agent == "b":
            group_errors["ball"].append(distances)
        elif agent.startswith("l"):
            group_errors["left"].append(distances)
        elif agent.startswith("r"):
            group_errors["right"].append(distances)

    return {
        group: np.mean(np.concatenate(values))
        for group, values in group_errors.items()
    }


def main():
    submit_folder = args.submit
    gt_folder = args.gt
    input_folder = args.input
    burn_in = args.burn_in

    submit_files = get_csv_files(submit_folder)
    gt_files = get_csv_files(gt_folder)
    input_files = get_csv_files(input_folder)

    submit_filenames = [os.path.basename(f) for f in submit_files]
    gt_filenames = [os.path.basename(f) for f in gt_files]

    common_files = set(submit_filenames).intersection(set(gt_filenames))

    if not common_files:
        print("No matching CSV files found between submission and ground truth folders.")
        return

    all_average_errors = []
    all_endpoint_errors = []

    all_ball_errors = []
    all_left_errors = []
    all_right_errors = []

    agents_list = [f'l{i}' for i in range(1, 12)] + [f'r{i}' for i in range(1, 12)] + ['b']

    for filename in sorted(common_files):
        submit_path = os.path.join(submit_folder, filename)
        gt_path = os.path.join(gt_folder, filename)
        input_path = os.path.join(input_folder, filename)

        try:
            submit_df = pd.read_csv(submit_path, index_col='#')
            gt_df = pd.read_csv(gt_path, index_col='#')
            input_df = pd.read_csv(input_path, index_col='#')
        except Exception as e:
            print(f"Error reading files {filename}: {e}")
            continue

        assert input_df.index[-1] + 1 == submit_df.index[0], \
            "The last cycle of input_df does not match the first cycle of submit_df"

        common_cycles = submit_df.index.intersection(gt_df.index)
        gt_df2 = gt_df.loc[common_cycles]

        expected_columns = [f'{agent}_x' for agent in agents_list] + [f'{agent}_y' for agent in agents_list]
        assert all(col in submit_df.columns for col in expected_columns), \
            "Submission file is missing required columns"

        avg_error, end_error = compute_errors(submit_df, gt_df2, agents_list, burn_in)
        group_error = compute_group_errors(submit_df, gt_df2, agents_list, burn_in)

        all_average_errors.append(avg_error)
        all_endpoint_errors.append(end_error)

        all_ball_errors.append(group_error["ball"])
        all_left_errors.append(group_error["left"])
        all_right_errors.append(group_error["right"])

    if not all_average_errors:
        print("No errors were computed. Please check the input files.")
        return

    overall_average_error = np.mean(all_average_errors)
    overall_endpoint_error = np.mean(all_endpoint_errors)

    print("Trajectory Prediction Evaluation Results:")
    print(f"Burn-in Steps: {burn_in}")
    print(f"Number of Evaluated Sequences: {len(all_average_errors)}")
    print(f"Average Error (after burn-in): {overall_average_error:.4f}")
    print(f"Endpoint Error: {overall_endpoint_error:.4f}")

    print("\nGroup-wise Mean Error:")
    print(f"Ball Mean Error: {np.mean(all_ball_errors):.4f}")
    print(f"Left Team Mean Error: {np.mean(all_left_errors):.4f}")
    print(f"Right Team Mean Error: {np.mean(all_right_errors):.4f}")


if __name__ == "__main__":
    main()