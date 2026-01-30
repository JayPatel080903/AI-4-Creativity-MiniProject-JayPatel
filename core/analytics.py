import pandas as pd


def dataset_overview(df):
    return {
        "rows": len(df),
        "columns": df.shape[1],
        "column_names": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
    }


def preview_data(df, n=5):
    return df.head(n)


def numeric_summary(df):
    return df.describe()


def column_stats(df, column):
    s = df[column]
    
    # Check if column is numeric
    if not pd.api.types.is_numeric_dtype(s):
        raise ValueError(f"⚠️ Column '{column}' contains string values. Currently not supported for string values.")
    
    return {
        "min": s.min(),
        "max": s.max(),
        "mean": round(s.mean(), 2),
        "median": s.median(),
        "nulls": int(s.isna().sum()),
        "unique": int(s.nunique()),
    }


def top_n(df, column, n=10):
    return df.sort_values(by=column, ascending=False).head(n)


def groupby_aggregate(df, group_col, agg, value_col):
    return (
        df.groupby(group_col)[value_col]
        .agg(agg)
        .reset_index()
    )


def detect_outliers(df, column):
    if not pd.api.types.is_numeric_dtype(df[column]):
        return pd.DataFrame({"error": ["Column is non-numeric. Cannot detect outliers."]})
    
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    return df[
        (df[column] < q1 - 1.5 * iqr) |
        (df[column] > q3 + 1.5 * iqr)
    ]


def auto_insights(df):
    insights = []
    for col in df.columns:
        null_pct = df[col].isna().mean()
        if null_pct > 0.3:
            insights.append(f"⚠️ {col} has {int(null_pct*100)}% missing values")
        if df[col].dtype != "object" and df[col].nunique() > 10:
            if df[col].skew() > 1:
                insights.append(f"📈 {col} is highly right-skewed")
    if not insights:
        insights.append("✅ No obvious data issues detected")
    return insights


def compare_columns(df, c1, c2):
    result = {}
    
    if pd.api.types.is_numeric_dtype(df[c1]):
        result[c1] = df[c1].describe().to_dict()
    else:
        result[c1] = {"type": "non-numeric", "unique": int(df[c1].nunique())}
    
    if pd.api.types.is_numeric_dtype(df[c2]):
        result[c2] = df[c2].describe().to_dict()
    else:
        result[c2] = {"type": "non-numeric", "unique": int(df[c2].nunique())}
    
    return result

def filter_dataset(df, query):
    """
    Filters the dataframe using a pandas query string.
    Example: "Age > 30 and Department == 'Sales'"
    """
    try:
        subset = df.query(query)
        return subset, None
    except Exception as e:
        return df, f"⚠️ Filter Error: {str(e)}"
