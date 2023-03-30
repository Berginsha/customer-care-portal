from flask_mail import Mail, Message
from flask import Flask, render_template, request, redirect, url_for, session
from app import config


app = Flask(__name__)
app.config['SECRET_KEY'] = 'helloworld'
conn = config.mysql_connect()
cursor = conn.cursor()
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = config.mailid()
app.config['MAIL_PASSWORD'] = config.mailpass()
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        global rs
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password1 = request.form.get('password1')
        if password != password1:
            msg = "Passwords do not match"
            return render_template('register.html', msg=msg)
        cursor.execute(f'select * from user where username="{name}"')
        rs = cursor.fetchall()
        print(rs)
        if rs:
            msg = 'Account already Exists'
            return render_template('register.html', msg=msg)
        else:
            sql = "insert into user (username, email, password) VALUES(%s,%s,%s)"
            values = (name, email, password)
            val = cursor.execute(sql, values)
            conn.commit()
            print(val)
            msg = 'Successfully Registered'
            return render_template('register.html', msg=msg)
    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        customer = list()
        agent = list()
        name = request.form['name']
        password = request.form['password']
        values = (name, password)
        sql = "select * from user where username=%s and password=%s"
        cursor.execute(sql, values)
        rs = cursor.fetchall()
        if rs:
            session['role'] = 'user'
            session['customer'] = rs
            print(rs)
            return render_template('dashboard.html')
        sql = "select * from agent where username=%s and password=%s"
        cursor.execute(sql, values)
        rs = cursor.fetchall()
        if rs:
            cursor.execute('select * from user')
            customers = cursor.fetchall()
            cursor.execute('select * from agent')
            agents = cursor.fetchall()
            for cus in customers:
                customer.append(cus)
            for agt in agents:
                agent.append(agt)
            print(customer, agent)
            session['role'] = 'agent'
            session['name'] = rs[0][0]
            session['customer'] = customer
            session['agent'] = agent
            return render_template('dashboard.html')
        sql = "select * from admin where username=%s and password=%s"
        cursor.execute(sql, values)
        rs = cursor.fetchone()
        if rs:
            cursor.execute("select * from user")
            customers = cursor.fetchall()
            cursor.execute("select * from agent")
            agents = cursor.fetchall()
            for cus in customers:
                customer.append(cus)
            for agt in agents:
                agent.append(agt)
            print(customer)
            print(agent)
            session['role'] = 'admin'
            session['customer'] = customer
            session['agent'] = agent
            return render_template('dashboard.html', agent=agent, customer=customer)
        else:
            msg = 'UID/Password is incorrect'
            return render_template('login.html', msg=msg)
    else:
        return render_template('login.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    return render_template('dashboard.html')


@app.route('/success', methods=['POST', 'GET'])
def success():
    if request.method == "POST":
        ticket = session['ticket'] = config.alphanumeric()
        query = request.form['query']
        print(ticket, query, session['customer'][0][0])
        print(session['customer'])
        sql = "UPDATE user SET QUERY=%s,TICKET=%s,REVIEW_STATUS='0' where USERNAME=%s"
        status = cursor.execute(
            sql, (query, session['ticket'], session['customer'][0][0]))
        conn.commit()
        if status:
            msg = 'Success ! Your Ticket Nno is :', ticket, 'You can now return to the home page'
            return render_template('success.html', msg=msg)
        else:
            msg = 'Error Submitting your Query'
            return render_template('success.html', msg=msg)


@app.route('/redirect')
def redir():
    return redirect(url_for('home'))


@app.route('/querying', methods=['POST'])
def admin_query():
    msg = ""
    agent = request.form.getlist('agent_name')
    usr_name = request.form.getlist('cus_name')
    emails = request.form.getlist('email')
    print(agent, usr_name, emails)
    for i in range(0, len(agent)):
        if agent[i] != 'none':
            try:
                print(agent[i], usr_name[i], emails[i])
                sql = "update user set assigned_agent=%s where username=%s"
                cursor.execute(
                    sql, (agent[i], usr_name[i]))
                print(sql)
                conn.commit()
                print(agent[i], usr_name[i], emails[i])
                msg = Message(
                    f'Hello {usr_name[i]}',
                    sender='jebajeba7907@gmail.com',
                    recipients=[f'{emails[i]}']
                )
                msg.body = f'Agent named {agent[i]} alloted to your query.{agent[i]} will be responding you soon within 24 hrs.'
                mail.send(msg)
                msg = 'Allotments updated Successfully'
            except:
                msg = "Error saving allotments/sending emails"
    return render_template('done.html', msg=msg)


@app.route('/executing...', methods=['POST', 'GET'])
def agent_submit_reply():
    names = request.form.getlist('name')
    text = request.form.getlist('text')
    print(names)
    print(text)
    for i in range(0, len(names)):
        if not text[i] == '':
            try:
                sql = "update user set reply=%s,review_status='1' where username=%s"
                cursor.execute(sql, (text[i], names[i]))
                conn.commit()
                msg = 'Replies sent successfully'
            except:
                msg = 'Error Sending replies'
    return render_template('done.html', msg=msg)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
