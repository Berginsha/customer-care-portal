import pymysql.cursors
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from app import mailing, random_generator, mail_templates
import json
import sys
from waitress import serve


app = Flask(__name__)
app.config['SECRET_KEY'] = 'helloworld'
connection = pymysql.connect(
    host=os.getenv('mysql_db_endpoint'),
    user=os.getenv('mysql_db_username'),
    passwd=os.getenv('mysql_db_password'),
    port=3306,
    db=os.getenv('mysql_db_database'),
    cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()


@app.route('/healthz')
def health():
    test = cursor.execute('SELECT VERSION()')
    if test:
        return render_template('healthy.html')
    else:
        return '', 500


def getJson():
    with open('data.json') as f:
        file = json.load(f)
        return file['bank_name']


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        global rs
        session['name'] = name = request.form.get('name')
        session['email'] = email = request.form.get('email')
        session['password'] = password = request.form.get('password')
        password1 = request.form.get('password1')
        if password != password1:
            flash('passwords do not match')
            return redirect(url_for('register'))
        cursor.execute(f'select * from user where username="{name}"')
        rs = cursor.fetchall()
        print(rs)
        if rs:
            flash('Account already Exists')
            return redirect(url_for('register'))
        else:
            session['otp'] = random_generator.generate_otp()
            flash('An OTP has been sent to your email !!')
            try:
                context = mail_templates.mail_otp(
                    session['name'], session['otp'])
                mailing.mail("Register @ BANKARE", session['email'],
                             context['subject'], context['html_content'])
            except:
                flash('Error sending OTP')
                return redirect(url_for('register'))
            print(session['email'], context['subject'],
                  context['html_content'])
            return redirect(url_for('verify'))
    else:
        return render_template('register.html')


@app.route('/verify', methods=['POST', 'GET'])
def verify():
    if request.method == "POST":
        otp = request.form.get('otp')
        if session['otp'] == otp:
            sql = "insert into user (username, email, password) values(%s,%s,%s)"
            values = (session['name'], session['email'], session['password'])
            cursor.execute(sql, values)
            connection.commit()
            flash('Successfully Registered,Please Login!!')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP')
            return redirect(url_for('verify'))
    else:
        return render_template('verify.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        values = (name, password)
        sql = "select user.*,bank.bank_email from user inner join bank on bank=user.bank where username=%s and password=%s"
        cursor.execute(sql, values)
        rs = cursor.fetchone()
        if rs:
            session['logged_in'] = True
            session['role'] = 'user'
            session['customer'] = rs
            print(rs)
            return redirect(url_for('dashboard'))
        sql = "select * from agent where username=%s and password=%s"
        cursor.execute(sql, values)
        rs = cursor.fetchone()
        if rs:
            session['logged_in'] = True
            cursor.execute('select * from user')
            customers = cursor.fetchall()
            cursor.execute('select * from agent')
            agents = cursor.fetchall()
            print(customers, agents)
            session['role'] = 'agent'
            session['name'] = rs['username']
            session['customer'] = customers
            session['agent'] = rs
            session['bank'] = getJson()
            print(
                f'''session role:{session['role']}\n
                agent name:{session['name']}\n
                all customers:{session['customer']}\n
                all_agents:{session['agent']}\n
                bank detains:{session['bank']}''')
            return redirect(url_for('dashboard'))
        sql = "select * from admin where username=%s and password=%s"
        cursor.execute(sql, values)
        rs = cursor.fetchone()
        if rs:
            session['logged_in'] = True
            cursor.execute("select * from user")
            customers = cursor.fetchall()
            cursor.execute("select * from agent")
            agents = cursor.fetchall()
            print(customers, agents)
            session['role'] = 'admin'
            session['customer'] = customers
            session['agent'] = agents
            print(f'''role:{session['role']}\n
            all customers:{session['customer']}\n
            all agents: {session['agent']}''')
            return redirect(url_for('dashboard'))
        else:
            flash('UID/Password is incorrect')
            return redirect(url_for('login'))
    else:
        return render_template('login.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if not session.get('logged_in'):
        flash('Please log in first')
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/user/complaints', methods=["POST", "GET"])
def complaint():
    if request.method == "POST":
        topic = request.form['topic']
        description = request.form['desc']
        email=session['customer']['email']
        print(session['customer'])
        values = (session['customer']['username'],
                  session['customer']['bank'],session['customer']['email'], topic, description)
        print(values)
        try:
            cursor.execute(
                "insert into complaints values(%s,%s,%s,%s)", values)
            mailing.mail(
                f"{session['name'].capitalize()} from BANKARE",email, subject=topic, template=description)
            connection.commit()
            flash('Complaint posted successfully')
        except:
            flash('error submitting complaint!!! Retry ')
            return redirect(url_for('complaint'))
        return redirect(url_for('home'))
    else:
        return render_template('complaint.html')


@app.route('/success', methods=['POST', 'GET'])
def success():
    if request.method == "POST":
        ticket = session['ticket'] = random_generator.alphanumeric()
        query = request.form['query']
        feature = request.form['feature']
        bank = request.form['bank']
        print(ticket, query, session['customer']['username'])
        print(session['customer']['username'])
        sql = "UPDATE user SET QUERY=%s,TICKET=%s,REVIEW_STATUS='0',bank=%s,query_category=%s,assigned_agent=NULL,reply=NULL where USERNAME=%s"
        try:
            cursor.execute(
                sql, (query, session['ticket'], bank, feature, session['customer']['username']))
            connection.commit()
            flash(f'Success ! Your Ticket id is {ticket}')
        except:
            flash('Error Submitting your Query')
            return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/querying', methods=['POST', 'GET'])
def admin_assign_customer():
    if request.method == "POST":
        agents = tuple(request.form.getlist('agent_name'))
        usernames = tuple(request.form.getlist('cus_name'))
        emails = tuple(request.form.getlist('email'))
        combined = zip(agents, usernames, emails)
        print(combined)
        for item in combined:
            if item[0] != 'none':
                try:
                    print(item[0], item[1], item[2])
                    context = mail_templates.mail_agent_assigned(
                        item[1], item[0])
                    mailing.mail(f"{session['role'].capitalize()} from BANKARE",
                                 item[2], context['subject'], context['html_content'])
                    sql = "update user set assigned_agent=%s where username=%s"
                    cursor.execute(
                        sql, (item[0], item[1]))
                except:
                    flash('Error saving allotments/sending emails')
                    return redirect(url_for('dashboard'))
                connection.commit()
                flash('Allotments updated Successfully')
                return redirect(url_for('dashboard'))
    else:
        flash('Unauthorized !!')
        return redirect(url_for('home'))


@app.route('/executing', methods=['POST', 'GET'])
def agent_submit_reply():
    if request.method == 'POST':
        names = tuple(request.form.getlist('name'))
        text = tuple(request.form.getlist('text'))
        emails = tuple(request.form.getlist('email'))
        combined = zip(names, text, emails)
        print(combined)
        for item in combined:
            if not item[1] == '':
                try:
                    context = mail_templates.mail_agent_reply(item[0])
                    mailing.mail(f"{session['agent']['username'].capitalize()} from Bankare",
                                 item[2], context['subject'], context['html_content'])
                    sql = "update user set reply=%s,review_status='1',assigned_agent=NULL where username=%s"
                    cursor.execute(sql, (item[1], item[0]))
                except:
                    flash('Something went wrong')
                    return redirect(url_for('dashboard'))
                connection.commit()
                flash('Replies sent successfully')
                return redirect(url_for('dashboard'))
    else:
        flash('Unauthorized !')
        return redirect(url_for('home'))


mode = str(sys.argv[1])
print(mode)
if __name__ == '__main__':
    if mode == 'dev':
        app.run(debug=True, host="0.0.0.0", port=5000)
    elif mode == 'dep':
        serve(app, host='0.0.0.0', port=5000)
