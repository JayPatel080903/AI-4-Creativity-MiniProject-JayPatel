import matplotlib.pyplot as plt
import seaborn as sns

def validate_columns(df, columns):
    """Returns missing columns if any."""
    missing = [col for col in columns if col and col not in df.columns]
    if missing:
        raise ValueError(f"⚠️ Columns not found: {', '.join(missing)}")

def bar_plot(df, x, y):
    validate_columns(df, [x, y])
    fig, ax = plt.subplots()
    sns.barplot(data=df, x=x, y=y, ax=ax)
    ax.set_title(f"{y} by {x}")
    return fig

def histogram(df, column):
    validate_columns(df, [column])
    fig, ax = plt.subplots()
    sns.histplot(df[column], kde=True, ax=ax)
    ax.set_title(f"Distribution of {column}")
    return fig

def auto_plot(df, x, y=None):
    if y:
        return bar_plot(df, x, y)
    return histogram(df, x)