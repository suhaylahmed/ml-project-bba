"""Every estimator owns a complete preprocessing pipeline."""

from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from complaints.features import CATEGORICAL, NUMERIC, TEXT


def make_pipeline(estimator) -> Pipeline:
    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median", keep_empty_features=True)),
        ("scale", StandardScaler()),
    ])
    categorical = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("encode", OneHotEncoder(handle_unknown="ignore")),
    ])
    inputs = ColumnTransformer([
        ("numeric", numeric, NUMERIC),
        ("category", categorical, CATEGORICAL),
        ("text", TfidfVectorizer(ngram_range=(1, 2), max_features=600, min_df=2, sublinear_tf=True), TEXT),
    ])
    return Pipeline([("inputs", inputs), ("model", estimator)])


def candidates(seed: int = 42) -> dict[str, Pipeline]:
    return {
        "Dummy baseline": make_pipeline(DummyClassifier(strategy="prior")),
        "Logistic Regression": make_pipeline(LogisticRegression(C=2, max_iter=1000, random_state=seed)),
        "kNN": make_pipeline(KNeighborsClassifier(n_neighbors=5, n_jobs=1)),
        "Random Forest": make_pipeline(RandomForestClassifier(
            n_estimators=100, min_samples_leaf=4, class_weight="balanced", random_state=seed, n_jobs=1)),
        "AdaBoost": make_pipeline(AdaBoostClassifier(n_estimators=50, learning_rate=0.8, random_state=seed)),
    }
