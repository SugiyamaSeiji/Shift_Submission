import pandas as pd
from src import app
from flask import flash
from flask import redirect
from flask import request
from flask import render_template
from flask import url_for
from flask import session
from src import db
from src.models.employee import Employee, EmployeeDate
from datetime import datetime, timedelta
import pandas as pd

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    return redirect('/employees')

# ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        user = Employee.query.filter_by(name = request.form['name']).first()
        if request.form['name'] == '':
            flash('ユーザ名を入力してください')

        elif request.form['password'] == '':
            flash('パスワードを入力してください')

        elif request.form['name'] != user.name:
            flash(f'ユーザ名が異なります')

        elif request.form['password'] != user.password:
            flash(f'パスワードが異なります')
        else:
            session['logged_in'] = True
            #flash('ログインしました')
            return redirect('/')  # nameとpasswordが合っていたい時だけ、indexにリダイレクトされる
    return render_template('login.html')

# ログアウト
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('logged_in', None)
    flash('ログアウトしました')
    return redirect('/')

# 従業員の追加
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'GET':
        return render_template('add_employee.html')
    if request.method == 'POST':
        form_name = request.form.get('name')  # str
        form_pass = request.form.get('password')  # str
        employee = Employee(
            name=form_name,
            password=form_pass,
        )
        db.session.add(employee)
        db.session.commit()
        return redirect(url_for('index'))

# 従業員の一覧
@app.route('/employees')
def employee_list():
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees)

# シフトの入力ボタンが押された
@app.route('/employees/<int:id>', methods=['GET','POST'])  
def employee_input(id):
    if request.method =='GET':
        return render_template('input_shift.html')
    
    if request.method =='POST':
        if not request.form['start']:
            flash(f'開始日を入力してください')
            return render_template('input_shift.html')
    
        elif not request.form['end']:
            flash(f'終了日を入力してください')
            return render_template('input_shift.html')
    
        else:
            employee = Employee.query.get(id)
            start = request.form['start']
            end = request.form['end']
            
            d_start = datetime.datetime.strptime(str(start), '%Y-%m-%d')
            d_end = datetime.datetime.strptime(str(end), '%Y-%m-%d')
            
            diff = (d_end-d_start).days # 日付の差をとっている
            if diff <= 0:
                flash('適切な日付を設定してください')
                return render_template('input_shift.html', employee= employee)
            
            dates = []
            weeks = []
            week_dic = {'Monday':"月", 'Tuesday':"火", 'Wednesday':"水", 'Thursday':"木", 'Friday':"金", 'Saturday':"土", 'Sunday':"日"}

            tem = d_start
            while tem <= d_end:
                dates.append(tem.strftime('%Y-%m-%d'))
                weeks.append(week_dic[tem.strftime('%A')])
                tem += timedelta(days=1)
            
            return render_template('input_shift.html', employee=employee, dates=dates, weeks=weeks, diff=diff, id=id)

# 辞書型に変更
def name_date_shift(year, month):
    dates = {}
    employees = Employee.query.all()
    for employee in employees:
        shifts = EmployeeDate.query.filter_by(employee_id=employee.id, year=year, month=month).all()
        for shift in shifts:
            key = (employee.name, shift.year, shift.month)
            if key not in dates:
                dates[key] = {} 
            dates[key][shift.day] = shift.shift   # dates[('太郎', 2024, 3)][24] = 3 / 太郎：2024-3-24：3
    
    return dates

# html用の表(table)に変換
def to_table(dates, year, month):
    days = calendar.monthrange(year, month)[1]
    month_days = list(range(1, days+1))

    df =[]
    shift_dict = {1:'×', 2:'昼', 3:'夜', 4:'17', 5:'18', 6:'w', ' ':' '}
    for (name, year, month), shifts in dates.items():
        row = {'名前': name}
        for day in month_days:
            key = shifts.get(day, ' ') # dayがなかったら、'-'に設定
            row[day] = shift_dict[key]
        
        df.append(row)
    df = pd.DataFrame(df)

    html_table = "<table class='table table-bordered table-striped'>\n"
    html_table += "<thead class='thead-light'><tr><th>名前</th>"
    for day in month_days:
        html_table += f"<th>{day}</th>"
    html_table += "</tr></thead>\n<tbody>"
    
    for index, row in df.iterrows():
        html_table += "<tr>"
        html_table += f"<td>{row['名前']}</td>"
        for day in month_days:
            shift = row[day]
            if calendar.weekday(year, month, day) == 5: # 土曜日
                html_table += f"<td style='background-color: #DBFFFF;'>{shift}</td>"
            elif calendar.weekday(year, month, day) == 6: # 日曜日
                html_table += f"<td style='background-color: #FFDBDB;'>{shift}</td>"
            else:
                html_table += f"<td>{shift}</td>"
        html_table += "</tr>"
    
    html_table += "</tbody></table>"
    return html_table

# 全ての従業員を考慮したシフトを表示させる
import calendar
import datetime
@app.route('/all_confirms', methods=['GET', 'POST'])
def all_confirms():
    if request.method == 'POST':
        dt_now = datetime.datetime.now()
        year = int(dt_now.year)
        if request.form['month'] == '月':
            dt_now = datetime.datetime.now()
            year = int(dt_now.year) 
            month = int(dt_now.month) 
            dates = name_date_shift(year, month) # {('太郎', 2024, 3):{19:1, 20:3...}, ..., ('花子', 2024, 3):{9:1, 22:3...}}
            to_tabled = to_table(dates, year, month)
            return render_template('all_confirms.html', to_tabled=to_tabled, month=month) 

        month = int(request.form['month'])

        if month == 1:
            year += 1 # 12月の人が1月のシフトを確認する時だけ、年を跨ぐため

        dates = name_date_shift(year, month) 
        to_tabled = to_table(dates, year, month)

    elif request.method == 'GET':
        dt_now = datetime.datetime.now()
        year = int(dt_now.year) 
        month = int(dt_now.month) 
        dates = name_date_shift(year, month) # {('太郎', 2024, 3):{19:1, 20:3...}, ..., ('花子', 2024, 3):{9:1, 22:3...}}
        to_tabled = to_table(dates, year, month)

    return render_template('all_confirms.html', to_tabled=to_tabled, month=month) 

#　シフトをデータベースに登録
@app.route('/confirm/<int:id>', methods=['POST'])
def confirm_shifts(id):
    if request.method == 'POST':
        for work in request.form: # 例) work : 2024-04-03
            year, month, day = work.split('-')
            shift = request.form[work]

            employee_date = EmployeeDate.query.filter_by(employee_id=id, year=year, month=month, day=day).first()

            if employee_date is None:
                # 新たにシフトを作成
                employee_date = EmployeeDate(
                    employee_id = id,
                    year = int(year),
                    month = int(month),
                    day = int(day),
                    shift = int(shift)
                )
                db.session.add(employee_date)
            else:
                # 既にある日付に関しては、シフトのみ変更
                employee_date.shift = shift
            
            # データベースの更新
            db.session.commit()

    dates = name_date_shift(int(year), int(month)) # {('太郎', 2024, 3):{19:1, 20:3...}, ..., ('花子', 2024, 3):{9:1, 22:3...}}
    to_tabled = to_table(dates, int(year), int(month))
    return render_template('confirm.html', to_tabled=to_tabled, month=int(month))

#　削除ページ(データベース)
@app.route('/del_login', methods=['GET', 'POST'])
def del_login():
    if request.method =='GET':
        return render_template('del_login.html')
    
    if request.method =='POST':
        if request.form['password'] == '':
            flash('パスワードを入力してください')
            return render_template('del_login.html')

        elif request.form['password'] != 'bunkoumanager':
            flash(f'パスワードが異なります')
            return render_template('del_login.html')
        
        return redirect(url_for('del_database'))
    
# 不要になったシフトをデータベースから削除    
@app.route('/del_database', methods=['GET', 'POST'])
def del_database():
    if request.method == 'GET':
        return render_template('del_database.html')

    if request.method == 'POST':
        del_date = request.form['del_date']
        del_year, del_month, del_day = del_date.split('-')

        must_del = EmployeeDate.query.filter((EmployeeDate.year < int(del_year)) |
            (EmployeeDate.year == int(del_year)) & (EmployeeDate.month < int(del_month)) |
            (EmployeeDate.year == int(del_year)) & (EmployeeDate.month == int(del_month)) & (EmployeeDate.day < int(del_day))
        ).all()
    
        for date in must_del:
            db.session.delete(date)
        
        db.session.commit()
        return redirect('/employees')

#　削除ページ(従業員)
@app.route('/del_login_em', methods=['GET', 'POST'])
def del_login_em():
    if request.method =='GET':
        return render_template('del_login_em.html')
    
    if request.method =='POST':
        if request.form['password'] == '':
            flash('パスワードを入力してください')
            return render_template('del_login_em.html')

        elif request.form['password'] != 'bunkoumanager':
            flash(f'パスワードが異なります')
            return render_template('del_login_em.html')
        
        return redirect(url_for('del_employee_list'))
    
# 従業員の削除
@app.route('/del_employee')
def del_employee_list():
    employees = Employee.query.all()
    return render_template('del_employee.html', employees=employees)

@app.route('/del_employee/<int:id>', methods=['POST'])
def del_employee(id):
    employee = Employee.query.get(id)   
    db.session.delete(employee)  
    db.session.commit()
    return redirect(url_for('employee_list'))

