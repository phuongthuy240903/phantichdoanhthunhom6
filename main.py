import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Đọc file CSV khi server khởi động
df = pd.read_csv('file.csv', encoding='utf-8')

# Chuyển đổi cột 'Order Date' sang định dạng datetime
df['Order Date'] = pd.to_datetime(df['Order Date'], format='%m/%d/%y %H:%M', errors='coerce')

# Chuyển đổi cột 'Quantity Ordered' và 'Price Each' sang dạng số
df['Quantity Ordered'] = pd.to_numeric(df['Quantity Ordered'], errors='coerce')
df['Price Each'] = pd.to_numeric(df['Price Each'], errors='coerce')

# Thêm cột 'Total Price' tính tổng tiền cho mỗi đơn hàng
df['Total Price'] = df['Quantity Ordered'] * df['Price Each']

def calculate_total_revenue(start_date, end_date):
    # Chuyển đổi start_date và end_date sang định dạng datetime
    start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
    end_date = pd.to_datetime(end_date, format='%d/%m/%Y')

    # Lọc dữ liệu trong khoảng thời gian
    filtered_df = df[(df['Order Date'] >= start_date) & (df['Order Date'] <= end_date)]

    # Tính tổng doanh thu
    total_revenue = filtered_df['Total Price'].sum()
    return float(total_revenue)

def calculate_monthly_revenue(year):
    # Lọc dữ liệu theo năm được chọn
    filtered_df = df[df['Order Date'].dt.year == year]

    # Tính tổng doanh thu theo từng tháng
    monthly_revenue = filtered_df.resample('MS', on='Order Date')['Total Price'].sum().reset_index()

    # Chuyển đổi định dạng ngày tháng của cột 'Order Date' thành tháng/năm
    monthly_revenue['Order Date'] = monthly_revenue['Order Date'].dt.strftime('%m/%Y')

    return monthly_revenue

def calculate_product_revenue(year):
    # Lọc dữ liệu theo năm được chọn
    filtered_df = df[df['Order Date'].dt.year == year]

    # Nhóm theo sản phẩm và tính tổng doanh thu
    product_revenue = filtered_df.groupby('Product')['Total Price'].sum().reset_index()

    return product_revenue

@app.route('/', methods=['GET', 'POST'])
def index():
    total_revenue = None
    selected_year = None
    monthly_revenue = None

    if request.method == 'POST':
        # Xử lý khi submit form để tính tổng doanh thu theo khoảng thời gian
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        total_revenue = calculate_total_revenue(start_date, end_date)
        # Trả về dữ liệu dạng JSON để JavaScript xử lý
        return jsonify({'total': total_revenue})

    else:
        # Mặc định hiển thị doanh thu hàng tháng cho năm hiện tại
        selected_year = pd.Timestamp.now().year
        monthly_revenue = calculate_monthly_revenue(selected_year)

    return render_template('index.html', total_revenue=total_revenue, selected_year=selected_year, monthly_revenue=monthly_revenue)

@app.route('/chart-data', methods=['GET'])
def chart_data():
    selected_year = int(request.args.get('year'))
    monthly_revenue = calculate_monthly_revenue(selected_year)

    # Chuẩn bị dữ liệu cho biểu đồ Chart.js
    months = monthly_revenue['Order Date'].tolist()
    revenue_data = monthly_revenue['Total Price'].tolist()

    # Tạo một dictionary chứa dữ liệu để trả về dưới dạng JSON
    chart_data = {
        'months': months,
        'revenue_data': revenue_data
    }

    return jsonify(chart_data)

@app.route('/product-revenue', methods=['GET'])
def product_revenue():
    year = int(request.args.get('year'))
    product_revenue_data = calculate_product_revenue(year).to_dict(orient='records')

    return jsonify(product_revenue_data)
if __name__ == '__main__':
    app.run(debug=True)
