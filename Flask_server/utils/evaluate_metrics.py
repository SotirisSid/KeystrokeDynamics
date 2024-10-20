import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix
y_true =[3]
def calculate_frr_far(y_true, y_pred):
    # Check if confusion matrix can be computed properly
    if len(set(y_true)) > 1 or len(set(y_pred)) > 1:
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        frr = fn / (fn + tp) if (fn + tp) > 0 else 0.0  # False Rejection Rate (FRR)
        far = fp / (fp + tn) if (fp + tn) > 0 else 0.0  # False Acceptance Rate (FAR)
    else:
        # If there's no variation in predictions or ground truth, return default values
        frr = 0.0
        far = 0.0

    return frr, far

def evaluate_model(y_true, y_pred, user_id):  # Accept user_id as a parameter
    # Ensure y_pred is a list or array-like
    if isinstance(y_pred, (list, np.ndarray)):
        y_pred = list(y_pred)  # Convert y_pred to a list if it's an array
    else:
        y_pred = [y_pred]  # Convert y_pred to a list if it's a single value

    # Use the provided user_id as the positive class
    positive_class = user_id

    # Calculate precision, recall, and F1 score with pos_label adjustment
    precision = precision_score(y_true, y_pred, pos_label=positive_class, zero_division=1)
    recall = recall_score(y_true, y_pred, pos_label=positive_class, zero_division=1)
    f1 = f1_score(y_true, y_pred, pos_label=positive_class, zero_division=1)

    # Calculate FRR and FAR
    frr, far = calculate_frr_far(y_true, y_pred)

    # Return the metrics as a dictionary
    metrics = {
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1,
        "FRR": frr,
        "FAR": far
    }

    return metrics
