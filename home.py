from flask import Flask, render_template, request, redirect, session
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'x'
app.config['MYSQL_DATABASE_PASSWORD'] = 'x'
app.config['MYSQL_DATABASE_DB'] = 'disney'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

app.secret_key = 'LGk@4*ur$^&Ap)74kG36y#gF(H9jy'

@app.route('/', methods=['GET'])
def index():
    cursor.execute("SELECT content FROM page_content WHERE page='home' AND location='header' AND status=1")
    header_text = cursor.fetchall()

    cursor.execute("SELECT content, header_text, image_link FROM page_content WHERE page='home' AND location='left_bar' AND status=1")
    data = cursor.fetchall()

    if header_text is None:
        return "Your query returns no results"
    else:
        return render_template('index.html', header=header_text, data = data)

@app.route('/admin')
def admin():
    return render_template('admin.html', failure=request.args.get('failure'), message="Login Failed")

@app.route('/logout')
def logout():
    session.clear()
    return render_template('admin.html', failure=request.args.get('failure'), message="Hambone")

@app.route('/admin_submit', methods=['GET', 'POST'])
def admin_submit():
    if request.form['username'] == 'admin' and request.form['password'] == 'admin':
        session['username'] = request.form['username']
        return redirect('/admin_portal')
    else:
        return redirect('/admin?failure=true')

@app.route('/admin_portal')
def admin_portal():
    if 'username' in session:
        cursor.execute("SELECT content, header_text, image_link, location, id FROM page_content WHERE page='home' AND status=1")
        data = cursor.fetchall()
        return render_template('admin_portal.html',
            hp_content = data)
    else:
        return redirect('/admin?failure=true')

@app.route('/admin_update', methods=['POST'])
def admin_update():
    if 'username' in session:
        body = request.form['body_text']
        header = request.form['header']
        image = request.form['image']

        query = "INSERT INTO page_content VALUES (DEFAULT, 'home', %s, 1, 1, 'left_bar', '', %s, %s)"
        cursor.execute(query, (body, header, image))
        conn.commit()
        return redirect('/admin_portal?failure=false')        
    else:
        return redirect('/admin?failure=true')

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'GET':
        cursor.execute("SELECT content, header_text, image_link, location, id, status, priority FROM page_content WHERE id = %s" % id)
        data = cursor.fetchone()
        return render_template('edit.html',
        data = data)
    else:
        body = request.form['body_text']
        header = request.form['header']
        image = request.form['image']
        location = request.form['location']
        status = request.form['status']
        priority = request.form['priority']
        query = "UPDATE page_content SET content = %s, status = %s, priority = %s, location = %s, header_text = %s, image_link = %s WHERE id = %s"
        cursor.execute(query, (body, status, priority, location, header, image, id))
        conn.commit()
        return redirect('/admin_portal?failure=false') 

if __name__ == '__main__':
    app.run(debug=True)
