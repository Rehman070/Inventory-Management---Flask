from flask import Flask, render_template, redirect, request, flash, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Numeric, BigInteger, func

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'a0455de1e15d46ad995c0d40928916ef'
db = SQLAlchemy(app)


# Model for LCD
class LCD(db.Model):
    lcd_id = db.Column(db.Integer, primary_key=True)
    lcd = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(100), nullable=False, default="null")
    unit = db.Column(db.String(20), nullable=False, default='0')
    add_value = db.Column(Numeric(precision=20, scale=2), nullable=False, default=0)
    target = db.Column(db.BigInteger, nullable=False, default=0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<LCD %r>' % self.lcd_id


# Model for Keyboard
class Keyboard(db.Model):
    kb_id = db.Column(db.Integer, primary_key=True)
    kbdd = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(100), nullable=False, default="Null")
    unit = db.Column(db.String(20), nullable=False, default='0')
    add_value = db.Column(Numeric(precision=20, scale=2), nullable=False, default=0)
    target = db.Column(db.BigInteger, nullable=False, default=0)
    Keyboard_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Keyboard %r>' % self.kb_id


# Model for Laptop
class Laptop(db.Model):
    lp_id = db.Column(db.Integer, primary_key=True)
    laptop = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(100), nullable=False, default="Null")
    unit = db.Column(db.String(20), nullable=False, default='0')
    add_value = db.Column(Numeric(precision=20, scale=2), nullable=False, default=0)
    target = db.Column(db.BigInteger, nullable=False, default=0)
    lp_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Laptop %r>' % self.lp_id


# Route for index page (LCD, Keyboard, Laptop Data Posting)
@app.route('/', methods=["GET", "POST"])
def Index():
    date_str_lcd = None  # Initialize date_str_lcd
    if request.method == 'POST':
        if 'LCD' in request.form:
            # LCD Data Posting
            lcd = request.form.get('LCD')
            description_lcd = request.form.get('Description')
            unit_lcd = request.form.get('Unit') or '0'  # Use default value if empty
            add_value_lcd = request.form.get('AddValue') or 0  # Use default value if empty
            target_lcd = request.form.get('Target') or 0  # Use default value if empty
            date_str_lcd = request.form.get('LCDDate')
            if date_str_lcd:  # Check if date_str_lcd is not None
                date_obj_lcd = datetime.strptime(date_str_lcd, '%m/%d/%Y')
            else:
                date_obj_lcd = datetime.utcnow()  # Use current time as default
            lcd_data = LCD(lcd=lcd, description=description_lcd, unit=unit_lcd, add_value=add_value_lcd,
                           target=target_lcd, date=date_obj_lcd)
            db.session.add(lcd_data)
            db.session.commit()
            flash('LCD Record Successfully Posted', 'success')

        elif 'kbdd' in request.form:
            # Keyboard Data Posting
            kbdd = request.form.get('kbdd')
            description_kbd = request.form.get('Description')
            unit_kbd = request.form.get('Unit') or '0'
            add_value_kbd = request.form.get('AddValue') or 0
            target_kbd = request.form.get('Target') or 0
            date_str_kbd = request.form.get('KeyboardDate')
            if date_str_kbd:  # Check if date_str_kbd is not None
                date_obj_kbd = datetime.strptime(date_str_kbd, '%m/%d/%Y')
            else:
                date_obj_kbd = datetime.utcnow()  # Use current time as default
            kbd_data = Keyboard(kbdd=kbdd, description=description_kbd, unit=unit_kbd, add_value=add_value_kbd,
                                 target=target_kbd, Keyboard_date=date_obj_kbd)
            db.session.add(kbd_data)
            db.session.commit()
            flash('  Keyboard Record Successfully Posted', 'success')

        elif 'laptop' in request.form:
            # Laptop Data Posting
            laptop = request.form.get('laptop')
            description_kbd = request.form.get('Description')
            unit_kbd = request.form.get('Unit') or '0'
            add_value_kbd = request.form.get('AddValue') or 0
            target_kbd = request.form.get('Target') or 0
            date_str_lp = request.form.get('LaptopDate')
            if date_str_lp:  # Check if date_str_lp is not None
                date_obj_lp = datetime.strptime(date_str_lp, '%m/%d/%Y')
            else:
                date_obj_lp = datetime.utcnow()  # Use current time as default
            laptop_data = Laptop(laptop=laptop, description=description_kbd, unit=unit_kbd, add_value=add_value_kbd,
                                 target=target_kbd, lp_date=date_obj_lp)
            db.session.add(laptop_data)
            db.session.commit()
            flash('  Laptop Record Successfully Posted', 'success')
            return redirect('/')
    return render_template('Index.html')


# Route for displaying inventory
@app.route('/inventory', methods=['GET', 'POST'])
def Inventory():
    if request.method == 'POST':
        # Get the selected dates from the form
        from_date_str = request.form['fromDate']
        to_date_str = request.form['toDate']

        # Check if the date strings are empty
        if not from_date_str or not to_date_str:
            return redirect('/inventory')

        try:
            # Convert the date strings to datetime objects
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d')
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d')
        except ValueError:
            return redirect('/inventory')

        # Query the database to retrieve records within the selected date range
        filtered_lcd_data = LCD.query.filter(LCD.date.between(from_date, to_date)).all()
        filtered_kbd_data = Keyboard.query.filter(Keyboard.Keyboard_date.between(from_date, to_date)).all()
        filtered_laptop_data = Laptop.query.filter(Laptop.lp_date.between(from_date, to_date)).all()

        # Compute averages for each column using filtered data
        lcd_avg_add_value = "{:.2f}".format(
            db.session.query(func.avg(LCD.add_value)).filter(LCD.date.between(from_date, to_date)).scalar() or 0)
        lcd_avg_target = "{:.2f}".format(
            db.session.query(func.avg(LCD.target)).filter(LCD.date.between(from_date, to_date)).scalar() or 0)
        kbd_avg_add_value = "{:.2f}".format(
            db.session.query(func.avg(Keyboard.add_value)).filter(Keyboard.Keyboard_date.between(from_date, to_date)).scalar() or 0)
        kbd_avg_target = "{:.2f}".format(
            db.session.query(func.avg(Keyboard.target)).filter(Keyboard.Keyboard_date.between(from_date, to_date)).scalar() or 0)
        laptop_avg_add_value = "{:.2f}".format(
            db.session.query(func.avg(Laptop.add_value)).filter(Laptop.lp_date.between(from_date, to_date)).scalar() or 0)
        laptop_avg_target = "{:.2f}".format(
            db.session.query(func.avg(Laptop.target)).filter(Laptop.lp_date.between(from_date, to_date)).scalar() or 0)

        return render_template("Inventory.html",
                               lcd_data=filtered_lcd_data,
                               kbd_data=filtered_kbd_data,
                               laptop_data=filtered_laptop_data,
                               lcd_avg_add_value=lcd_avg_add_value,
                               lcd_avg_target=lcd_avg_target,
                               kbd_avg_add_value=kbd_avg_add_value,
                               kbd_avg_target=kbd_avg_target,
                               laptop_avg_add_value=laptop_avg_add_value,
                               laptop_avg_target=laptop_avg_target)

    # If the request method is GET, render the page with all records
    all_lcd = LCD.query.all()
    all_kbd = Keyboard.query.all()
    all_laptop = Laptop.query.all()

    # Compute averages for each column using all data
    lcd_avg_add_value = "{:.2f}".format(db.session.query(func.avg(LCD.add_value)).scalar() or 0)
    lcd_avg_target = "{:.2f}".format(db.session.query(func.avg(LCD.target)).scalar() or 0)
    kbd_avg_add_value = "{:.2f}".format(db.session.query(func.avg(Keyboard.add_value)).scalar() or 0)
    kbd_avg_target = "{:.2f}".format(db.session.query(func.avg(Keyboard.target)).scalar() or 0)
    laptop_avg_add_value = "{:.2f}".format(db.session.query(func.avg(Laptop.add_value)).scalar() or 0)
    laptop_avg_target = "{:.2f}".format(db.session.query(func.avg(Laptop.target)).scalar() or 0)

    return render_template("Inventory.html",
                           lcd_data=all_lcd,
                           kbd_data=all_kbd,
                           laptop_data=all_laptop,
                           lcd_avg_add_value=lcd_avg_add_value,
                           lcd_avg_target=lcd_avg_target,
                           kbd_avg_add_value=kbd_avg_add_value,
                           kbd_avg_target=kbd_avg_target,
                           laptop_avg_add_value=laptop_avg_add_value,
                           laptop_avg_target=laptop_avg_target)


# Route for deleting LCD data
@app.route('/delete_lcd/<int:lcd_id>', methods=['DELETE'])
def delete_lcd(lcd_id):
    # Get the row to delete
    lcd_data = LCD.query.get_or_404(lcd_id)
    try:
        # Delete the row
        db.session.delete(lcd_data)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Route for deleting Keyboard data
@app.route('/delete_keyboard/<int:kbd_id>', methods=['DELETE'])
def delete_keyboard(kbd_id):
    # Get the row to delete
    kbd_data = Keyboard.query.get_or_404(kbd_id)
    try:
        # Delete the row
        db.session.delete(kbd_data)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Route for deleting Laptop data
@app.route('/delete_laptop/<int:lap_id>', methods=['DELETE'])
def delete_laptop(lap_id):
    # Get the row to delete
    laptop_data = Laptop.query.get_or_404(lap_id)
    try:
        # Delete the row
        db.session.delete(laptop_data)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Route for updating LCD data
@app.route('/update_lcd', methods=['POST'])
def update_lcd():
    lcd_id = request.form.get('LCDId')
    description = request.form.get('Description')
    unit = request.form.get('Unit')
    add_value = request.form.get('AddValue')
    target = request.form.get('Target')
    lcd_date_str = request.form.get('LCDDate')  # Get date string from form

    # Parse the date string into a datetime object
    lcd_date = datetime.strptime(lcd_date_str, '%m/%d/%Y')

    # Find the LCD record by its ID
    lcd_data = LCD.query.get_or_404(lcd_id)

    try:
        # Update the LCD record with the new data
        lcd_data.description = description
        lcd_data.unit = unit
        lcd_data.add_value = add_value
        lcd_data.target = target
        lcd_data.date = lcd_date

        # Commit the changes to the database
        db.session.commit()

        # Redirect the user to the inventory page after successful update
        return redirect(url_for('Inventory'))
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Route for updating Keyboard data
@app.route('/update_keyboard', methods=['POST'])
def update_keyboard():
    kbd_id = request.form.get('KbdId')
    description = request.form.get('Description')
    unit = request.form.get('Unit')
    add_value = request.form.get('AddValue')
    target = request.form.get('Target')
    kbd_date_str = request.form.get('KeyboardDate')  # Get date string from form

    try:
        # Parse the date string into a datetime object
        kbd_date = datetime.strptime(kbd_date_str, '%m/%d/%Y')

        # Find the keyboard record by its ID
        kbd_data = Keyboard.query.get_or_404(kbd_id)

        # Update the keyboard record with the new data
        kbd_data.description = description
        kbd_data.unit = unit
        kbd_data.add_value = add_value
        kbd_data.target = target
        kbd_data.Keyboard_date = kbd_date

        # Commit the changes to the database
        db.session.commit()

        # Redirect the user to the inventory page after successful update
        return redirect(url_for('Inventory'))
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Route for updating Laptop data
@app.route('/update_laptop', methods=['POST'])
def update_laptop():
    laptop_id = request.form.get('LaptopId')
    description = request.form.get('Description')
    unit = request.form.get('Unit')
    add_value = request.form.get('AddValue')
    target = request.form.get('Target')
    laptop_date_str = request.form.get('LaptopDate')  # Get date string from form

    try:
        # Parse the date string into a datetime object
        laptop_date = datetime.strptime(laptop_date_str, '%m/%d/%Y')

        # Find the laptop record by its ID
        laptop_data = Laptop.query.get_or_404(laptop_id)

        # Update the laptop record with the new data
        laptop_data.description = description
        laptop_data.unit = unit
        laptop_data.add_value = add_value
        laptop_data.target = target
        laptop_data.lp_date = laptop_date

        # Commit the changes to the database
        db.session.commit()

        # Redirect the user to the inventory page after successful update
        return redirect(url_for('Inventory'))
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# Route for getting graph data
@app.route('/get-graph-data')
def get_graph_data():
    # Query all records from the database
    all_lcd = LCD.query.all()
    all_kbd = Keyboard.query.all()
    all_laptop = Laptop.query.all()

    # Extract add values and target values for each type of data
    add_values_lcd = [lcd.add_value for lcd in all_lcd]
    target_values_lcd = [lcd.target for lcd in all_lcd]

    add_values_kbd = [kbd.add_value for kbd in all_kbd]
    target_values_kbd = [kbd.target for kbd in all_kbd]

    add_values_laptop = [laptop.add_value for laptop in all_laptop]
    target_values_laptop = [laptop.target for laptop in all_laptop]

    # Combine add values and target values for all data
    combined_add_values = add_values_lcd + add_values_kbd + add_values_laptop
    combined_target_values = target_values_lcd + target_values_kbd + target_values_laptop

    # Return data as JSON
    return jsonify({
        'labels': ['LCD'] * len(add_values_lcd) + ['Keyboard'] * len(add_values_kbd) + ['Laptop'] * len(
            add_values_laptop),
        'addValues': combined_add_values,
        'targetValues': combined_target_values
    })


if __name__ == '__main__':
    app.run(debug=True)
