import numpy as np
import xgboost as xgb

from features import FEATURE_META


def shap_contributions(model, feature_vector, feature_names):
    """Compute per-feature SHAP contributions for a single prediction.

    Uses XGBoost's native TreeSHAP (``pred_contribs``) so no extra dependency
    is required. Returns ``(base_value, contributions)`` where each
    contribution is a dict with the feature name, its raw value, and the
    SHAP impact in logit space.
    """
    dmatrix = xgb.DMatrix(
        np.asarray([feature_vector], dtype=float),
        feature_names=list(feature_names),
    )
    contribs = model.get_booster().predict(dmatrix, pred_contribs=True)

    if contribs.ndim == 2:
        # Binary model: shape (1, n_features + 1). Contributions are for the
        # positive class (the risk class).
        values = contribs[0]
    else:
        # Multiclass model: shape (1, n_features + 1, n_classes). Use the
        # slice belonging to the predicted class.
        target_class = int(np.argmax(model.predict_proba(np.asarray([feature_vector]))[0]))
        values = contribs[0, :, target_class]

    base_value = float(values[-1])
    contributions = [
        {
            'feature': name,
            'value': float(feature_vector[index]),
            'impact': float(values[index]),
        }
        for index, name in enumerate(feature_names)
    ]
    return base_value, contributions


def _build_summary(category, confidence, factors, risk_direction, top_n=3):
    evidence_for = [f for f in factors if (f['impact'] >= 0) == risk_direction]
    evidence_against = [f for f in factors if (f['impact'] >= 0) != risk_direction]

    def _names(items):
        return ', '.join(item['label'] for item in items)

    parts = [
        f'This URL was classified as {category} with '
        f'{confidence * 100:.1f}% confidence.'
    ]

    if evidence_for:
        top_evidence = sorted(
            evidence_for, key=lambda f: abs(f['impact']), reverse=True
        )[:top_n]
        parts.append(
            f'The strongest signals supporting this prediction are '
            f'{_names(top_evidence)}.'
        )

    if evidence_against:
        top_against = sorted(
            evidence_against, key=lambda f: abs(f['impact']), reverse=True
        )[:top_n]
        parts.append(
            f'The factors that pushed against it are {_names(top_against)}.'
        )

    return ' '.join(parts)


def build_explanation(model, feature_vector, feature_names, category, confidence):
    """Build a human-readable explanation object for a prediction."""
    base_value, contributions = shap_contributions(model, feature_vector, feature_names)

    factors = []
    for contribution in contributions:
        meta = FEATURE_META.get(contribution['feature'], {})
        factors.append({
            'feature': contribution['feature'],
            'label': meta.get(
                'label',
                contribution['feature'].replace('_', ' ').title(),
            ),
            'value': contribution['value'],
            'impact': contribution['impact'],
            'description': meta.get('description', ''),
        })

    factors.sort(key=lambda f: abs(f['impact']), reverse=True)

    prediction_value = base_value + sum(f['impact'] for f in factors)
    risk_direction = 1 if category != 'Legitimate' else 0

    summary = _build_summary(category, confidence, factors, risk_direction)

    return {
        'method': 'SHAP (TreeSHAP)',
        'base_value': base_value,
        'prediction_value': prediction_value,
        'summary': summary,
        'factors': factors,
    }
