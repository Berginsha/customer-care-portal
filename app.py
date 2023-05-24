import pymysql.cursors
import pymysql.err as e
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from app import mailing, random_generator, mail_templates
import json
import sys
from waitress import serve


app = Flask(__name__)
app.config['SECRET_KEY'] = 'helloworld'
app.config['SESSION_PERMANENT'] = False


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
        return file['bank']


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
                mailing.send_mail("Register @ BANKARE", session['email'],
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
            sql = "insert into user (username, email, password,bank) values(%s,%s,%s,'iob')"
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


def agent_session_refresh():
    cursor.execute(
        "select * from user where user.assigned_agent=%s and user.review_status=0", (session['agent']['username'],))
    session['customer'] = cursor.fetchall()
    print(session['customer'])


def user_session_refresh():
    print('refresh success')
    sql = "select user.*,bank.bank_email from user inner join bank on user.bank=bank.bank_name where user.username=%s"
    cursor.execute(sql, (session['customer']['username'],))
    session['customer'] = cursor.fetchone()
    print(session['customer'])


def admin_refresh_session():
    cursor.execute(
        "select * from user where assigned_agent=NULL or review_status=0")
    session['customer'] = cursor.fetchall()
    cursor.execute("select * from agent")
    session['agent'] = cursor.fetchall()
    print(session['customer'], session['agent'])


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        name = request.form['name']
        password = request.form['password']
        values = (name, password)
        sql = "select user.*,bank.bank_email from user inner join bank on user.bank=bank.bank_name where user.username=%s and user.password=%s"
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
            session['agent'] = rs
            session['role'] = 'agent'
            session['bank'] = getJson()
            agent_session_refresh()
            print(
                f'''session role:{session['role']}\n
                agent name:{session['agent']['username']}\n
                all customers:{session['customer']}\n
                all_agents:{session['agent']}\n
                bank detains:{session['bank']}''')
            return redirect(url_for('dashboard'))
        sql = "select * from admin where username=%s and password=%s"
        cursor.execute(sql, values)
        rs = cursor.fetchone()
        if rs:
            session['role'] = 'admin'
            session['logged_in'] = True
            admin_refresh_session()

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
    if session['logged_in'] and session['role'] == 'agent':
        agent_session_refresh()
    elif session['logged_in'] and session['role'] == 'user':
        user_session_refresh()
    elif session['logged_in'] and session['role'] == 'admin':
        admin_refresh_session()
    else:
        flash('Please log in first')
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/user/complaints', methods=["POST", "GET"])
def complaint():
    if request.method == "POST" and session['role'] == 'user':
        topic = str(request.form['topic'])
        description = request.form['desc']
        email = session['customer']['bank_email']
        values = (session['customer']['username'],
                  session['customer']['bank'], topic, description)
        try:
            context = mail_templates.mail_complaint(
                session['customer']['username'], session['customer']['bank'])
            print(context)
            mailing.send_mail(
                f"{session['customer']['username'].capitalize()} from BANKARE", email, topic, context['html_content'])
            cursor.execute(
                "insert into complaints values(%s,%s,%s,%s)", values)
        except:
            flash('error submitting complaint!!! Retry ')
            return redirect(url_for('complaint'))
        connection.commit()
        flash('Complaint posted successfully')
        return redirect(url_for('home'))
    else:
        return render_template('complaint.html')


@app.route('/loanCalculator', methods=["GET"])
def loan_calculator():
    return render_template('loanCalculator.html')


@app.route('/query', methods=["POST", "GET"])
def query():
    if request.method == "POST" and session['role'] == 'user':
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
    else:
        return render_template('query.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/querying', methods=['POST', 'GET'])
def admin_assign_customer():
    if request.method == "POST" and session['role'] == 'admin':
        agents = tuple(request.form.getlist('agent_name'))
        usernames = tuple(request.form.getlist('customer_name'))
        emails = tuple(request.form.getlist('email'))
        print(agents, usernames, emails)
        combined = tuple(zip(agents, usernames, emails))
        for item in combined:
            if not item[0] == 'none':
                try:
                    print(item[0], item[1], item[2])
                    context = mail_templates.mail_agent_assigned(
                        item[1], item[0])
                    mailing.send_mail(f"{session['role'].capitalize()} from BANKARE",
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


@app.route('/addAgent', methods=['POST', 'GET'])
def add_agent():
    if request.method == 'POST' and session['role'] == 'admin':
        agent_name = request.form['agent_name']
        agent_password = request.form['agent_password']
        try:
            cursor.execute('Insert into agent values(%s,%s)',
                           (agent_name, agent_password))
        except:
            flash('Error adding agent')
            return redirect(url_for('add_agent'))
        connection.commit()
        flash('Successfully added Agent')
        admin_refresh_session()
        return redirect(url_for('add_agent'))
    else:
        return render_template('addAgent.html')


@app.route('/delAgent', methods=["POST", "GET"])
def del_agent():
    if request.method == "POST":
        agentName = request.form['agent_name']
        try:
            cursor.execute(
                'delete from agent where username = %s', (agentName,))
            cursor.execute(
                'update user set assigned_agent=NULL where review_status=0 and assigned_agent=%s', (agentName,))
            admin_refresh_session()
        except:
            flash('Error deleting agent')
            return redirect(url_for('del_agent'))
        connection.commit()
        flash('Agent Deleted')
        return redirect(url_for('del_agent'))
    else:
        return render_template('delAgent.html')


@app.route('/executing', methods=['POST', 'GET'])
def agent_submit_reply():
    if request.method == 'POST':
        names = tuple(request.form.getlist('name'))
        text = tuple(request.form.getlist('text'))
        emails = tuple(request.form.getlist('email'))
        combined = zip(names, text, emails)
        print(names, text, emails)
        for item in combined:
            if not item[1] == '':
                try:
                    context = mail_templates.mail_agent_reply(item[0])
                    mailing.send_mail(f"{session['agent']['username'].capitalize()} from Bankare",
                                      item[2], context['subject'], context['html_content'])
                    sql = "update user set reply=%s,review_status='1' where username=%s"
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


@app.errorhandler(404)
def not_found(error):
    flash('URL not found')
    return redirect(url_for('home'))


@app.errorhandler(500)
def server_error(error):
    flash('Server Error')
    return redirect(url_for('home'))


@app.errorhandler(e.OperationalError)
def mysql_error():
    return "check whether mysql server is up"


@app.errorhandler(e.ProgrammingError)
def mysql_program_error():
    return "Restarting the application may fix this"


mode = str(sys.argv[1])

if __name__ == '__main__':
    if mode == 'dev':
        app.run(debug=True, host="0.0.0.0", port=5000)
    elif mode == 'dep':
        serve(app, host='0.0.0.0', port=5000)
    else:
        print(f"Invalid mode '{mode}'")
