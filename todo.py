import sqlite3
from bottle import route, run, debug, template, request, static_file, error

@route('/todo')
def todo_list():
	conn = sqlite3.connect('todo.db')
	c = conn.cursor()
	c.execute("SELECT id, task FROM todo WHERE status=1")
	result = c.fetchall()
	c.close()
	return template('make_table', rows=result)

@route('/new', method=['POST', 'GET'])
def new_item():
	if request.forms.get('save', '').strip():

		new = request.forms.get('task', '').strip()
		conn = sqlite3.connect('todo.db')
		c = conn.cursor()

		c.execute("INSERT INTO todo (task, status) VALUES (?,?)", (new, 1))
		new_id = c.lastrowid

		conn.commit()
		c.close()

		return '''
			<p>The new task was inserted into the database, the ID is %s</p>
			<a href='/todo'>Back</a>''' % new_id
	else:
		return template('new_task.tpl')

@route('/edit/:no', method=['GET','POST'])
def edit_item(no):

	if request.forms.get('save', '').strip():
		edit = request.forms.get('task', '').strip()
		status = request.forms.get('status', '').strip()

		if status == 'open':
			status = 1
		else:
			status = 0

		conn = sqlite3.connect('todo.db')
		c = conn.cursor()
		c.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (edit, status, no))
		conn.commit()

		return '''
			<p>The item number %s was successfully updated.</p>
			<a href='/todo'>Back</a>''' % no

	else:
		conn = sqlite3.connect('todo.db')
		c = conn.cursor()
		c.execute("SELECT task FROM todo WHERE id LIKE ?", (str(no)))
		cur_data = c.fetchone()

		return template('edit_task', old=cur_data, no=no)


@route('/item:item#[0-9]+#')
def show_item(item):

        conn = sqlite3.connect('todo.db')
        c = conn.cursor()
        c.execute("SELECT task FROM todo WHERE id LIKE ?", (item))
        result = c.fetchall()
        c.close()

        if not result:
            return 'This item number does not exist!'
        else:
            return 'Task: %s' %result[0]

@route('/help')
def help():
    return static_file('help.html', root='.')

@route('/json:json#[0-9]+#')
def show_json(json):
    conn = sqlite3.connect('todo.db')
    c = conn.cursor()
    c.execute("SELECT task FROM todo WHERE id LIKE ?", (json))
    result = c.fetchall()
    c.close()

    if not result:
        return {'task':'This item number does not exist!'}
    else:
        return {'Task': result[0]}

@error(403)
def mistake403(code):
    return 'There is a mistake in your url!'

@error(404)
def mistake404(code):
    return 'Sorry, this page does not exist!'
    
debug(True)
run()