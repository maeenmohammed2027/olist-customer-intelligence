import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error

# ─────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────
df = pd.read_csv('/Users/maeenmohammed/Documents/Maeen_project/SQL_dataset/BI_data/monthly_sales.csv')
df['order_month'] = pd.to_datetime(df['order_month'])
df = df.sort_values(['market_region', 'order_month'])
df['market_region'] = df['market_region'].str.strip()


# ─────────────────────────────────────────
# Feature Engineering
# ─────────────────────────────────────────
df['month_index'] = (
    (df['order_month'].dt.year - 2016) * 12 +
    df['order_month'].dt.month
)

# Use simple numeric encoding instead of LabelEncoder
region_map = {name: i for i, name in enumerate(df['market_region'].unique())}
print("Region mapping:", region_map)
df['region_encoded'] = df['market_region'].map(region_map)

# ─────────────────────────────────────────
# Train Model
# ─────────────────────────────────────────
X = df[['month_index', 'region_encoded']]
y = df['total_revenue']

model = LinearRegression()
model.fit(X, y)

y_pred_train = model.predict(X)
r2   = r2_score(y, y_pred_train)
rmse = np.sqrt(mean_squared_error(y, y_pred_train))

print(f"\nR² Score: {r2:.4f}")
print(f"RMSE: {rmse:,.2f}")
print(f"Model: Revenue = {model.coef_[0]:.2f} × month + {model.intercept_:.2f}")

# ─────────────────────────────────────────
# Generate Predictions — Next 3 Months
# ─────────────────────────────────────────
future_rows = []

for region_name, region_code in region_map.items():
    last_month = df[df['market_region'] == region_name]['month_index'].max()
    future_dates = pd.date_range(
        df[df['market_region'] == region_name]['order_month'].max()
        + pd.DateOffset(months=1),
        periods=3, freq='MS'
    )
    for i, date in enumerate(future_dates):
        future_rows.append({
            'order_month'    : date,
            'market_region'  : region_name,
            'month_index'    : last_month + i + 1,
            'region_encoded' : region_code,
            'data_type'      : 'Predicted'
        })

future = pd.DataFrame(future_rows)
future['predicted_revenue'] = model.predict(
    future[['month_index', 'region_encoded']]
).round(2)

# ─────────────────────────────────────────
# Combine Actual + Predicted
# ─────────────────────────────────────────
actual = df[['order_month', 'market_region', 'total_revenue']].copy()
actual['predicted_revenue'] = actual['total_revenue']
actual['data_type'] = 'Actual'

combined = pd.concat([
    actual[['order_month', 'market_region', 'predicted_revenue', 'data_type']],
    future[['order_month', 'market_region', 'predicted_revenue', 'data_type']]
])

combined = combined.sort_values(['market_region', 'order_month'])

# ─────────────────────────────────────────
# Save Output
# ─────────────────────────────────────────
combined.to_csv('/Users/maeenmohammed/Documents/Maeen_project/SQL_dataset/BI_data/revenue_forecast.csv', index=False)
print(f"\n✅ Forecast saved to outputs/revenue_forecast.csv")
print("\nPredicted values:")
print(future[['order_month', 'market_region', 'predicted_revenue']].to_string())
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 6))

colors = {
    'Region A / Core Market'      : '#2196F3',
    'Region B / Expansion Market' : '#FF6600'
}

for region, group in combined.groupby('market_region'):
    color      = colors.get(region, 'grey')
    short_name = 'Region A' if 'Core' in region else 'Region B'

    actual_data    = group[group['data_type'] == 'Actual']
    predicted_data = group[group['data_type'] == 'Predicted']

    # Plot actual
    ax.plot(
        actual_data['order_month'],
        actual_data['predicted_revenue'],
        color=color,
        linewidth=2.5,
        label=f'{short_name} — Actual'
    )

    # Connect last actual to first predicted
    connect_dates  = [actual_data['order_month'].iloc[-1]] + \
                     list(predicted_data['order_month'])
    connect_values = [actual_data['predicted_revenue'].iloc[-1]] + \
                     list(predicted_data['predicted_revenue'])

    # Plot predicted
    ax.plot(
        connect_dates,
        connect_values,
        color=color,
        linewidth=2.5,
        linestyle='--',
        label=f'{short_name} — Forecast'
    )

    # Annotate predicted values
    for _, row in predicted_data.iterrows():
        ax.annotate(
            f"R${row['predicted_revenue']/1000:.0f}K",
            xy=(row['order_month'], row['predicted_revenue']),
            xytext=(0, 10),
            textcoords='offset points',
            fontsize=9,
            color=color,
            ha='center',
            fontweight='bold'
        )

# Add vertical line separating actual from forecast
ax.axvline(
    x=pd.Timestamp('2018-09-01'),
    color='grey',
    linestyle=':',
    linewidth=1.5,
    label='Forecast Start'
)

ax.text(
    pd.Timestamp('2018-09-01'),
    combined['predicted_revenue'].max() * 0.95,
    '  Forecast →',
    color='grey',
    fontsize=10
)

ax.set_title(
    f'Revenue Trend & 3-Month Forecast — Linear Regression (R² = {r2:.2f})',
    fontsize=14,
    fontweight='bold'
)
ax.set_xlabel('Month')
ax.set_ylabel('Revenue (R$)')
ax.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, p: f'R${x/1000000:.1f}M')
)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()

# Save high resolution
plt.savefig('/Users/maeenmohammed/Documents/Maeen_project/revenue_forecast.png', dpi=300, bbox_inches='tight')
plt.show()
print("✅ Chart saved to outputs/revenue_forecast.png")