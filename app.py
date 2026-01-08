from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from werkzeug.utils import secure_filename
from database import get_db_connection, init_db
from utils import hash_data, generate_otp, verify_hash
from blockchain import Blockchain, Block, time

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo_only' # Change for production
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize Blockchain
blockchain = Blockchain()

# Initialize DB if not exists
if not os.path.exists('database.db'):
    init_db()

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

# --- Admin Routes ---

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Hardcoded credentials as per requirements
        if username == 'admin1' and password == '123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Credentials')
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    parties = conn.execute('SELECT * FROM parties').fetchall()
    voters = conn.execute('SELECT * FROM voters').fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', parties=parties, voters=voters, blockchain=blockchain.chain)

@app.route('/add-party', methods=['POST'])
def add_party():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    party_name = request.form['party_name']
    candidate_name = request.form['candidate_name']
    
    # Handle File Uploads
    party_logo = request.files['party_logo']
    candidate_pic = request.files['candidate_pic']
    
    logo_filename = secure_filename(party_logo.filename)
    pic_filename = secure_filename(candidate_pic.filename)
    
    party_logo.save(os.path.join(app.config['UPLOAD_FOLDER'], logo_filename))
    candidate_pic.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_filename))
    
    conn = get_db_connection()
    conn.execute('INSERT INTO parties (party_name, party_logo, candidate_name, candidate_pic) VALUES (?, ?, ?, ?)',
                 (party_name, logo_filename, candidate_name, pic_filename))
    conn.commit()
    conn.close()
    
    flash('Party Added Successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/register-voter', methods=['POST'])
def register_voter():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    aadhar = request.form['aadhar']
    name = request.form['name']
    dob = request.form['dob']
    pin = request.form['pin']
    email = request.form['email']
    
    # Hash sensitive data
    aadhar_hash = hash_data(aadhar)
    name_hash = hash_data(name)
    dob_hash = hash_data(dob)
    pin_hash = hash_data(pin)
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO voters (aadhar_hash, name_hash, dob_hash, pin_hash, email) VALUES (?, ?, ?, ?, ?)',
                     (aadhar_hash, name_hash, dob_hash, pin_hash, email))
        conn.commit()
        flash('Voter Registered Successfully')
    except sqlite3.IntegrityError:
        flash('Voter already registered (Aadhar hash collision)')
    finally:
        conn.close()
        
    return redirect(url_for('admin_dashboard'))

@app.route('/mine-block', methods=['POST'])
def mine_block():
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 403
        
    if not blockchain.unconfirmed_transactions:
        return jsonify({'message': 'No transactions to mine'})

    block_index = blockchain.mine()
    return jsonify({'message': f'Block {block_index} mined successfully!', 'chain': [b.__dict__ for b in blockchain.chain]})


# --- Voter Routes ---

@app.route('/voter-login', methods=['GET', 'POST'])
def voter_login():
    if request.method == 'POST':
        aadhar = request.form['aadhar']
        name = request.form['name']
        dob = request.form['dob']
        pin = request.form['pin']
        
        aadhar_hash = hash_data(aadhar)
        name_hash = hash_data(name)
        dob_hash = hash_data(dob)
        pin_hash = hash_data(pin)
        
        conn = get_db_connection()
        voter = conn.execute('SELECT * FROM voters WHERE aadhar_hash = ? AND name_hash = ? AND dob_hash = ? AND pin_hash = ?',
                             (aadhar_hash, name_hash, dob_hash, pin_hash)).fetchone()
        conn.close()
        
        if voter:
            if voter['has_voted']:
                flash('You have already voted!')
                return redirect(url_for('voter_login'))
                
            # Generate and Send OTP
            otp = generate_otp()
            session['otp'] = otp
            session['voter_id'] = voter['id']
            session['voter_email'] = voter['email']
            
            # Simulate sending email
            import sys
            print(f"---------------------------------------------------", file=sys.stderr)
            print(f"SENDING OTP to {voter['email']}: {otp}", file=sys.stderr)
            print(f"---------------------------------------------------", file=sys.stderr)
            
            return redirect(url_for('verify_otp'))
        else:
            flash('Invalid Details or Voter Not Registered')
            
    return render_template('voter_login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'otp' not in session:
        return redirect(url_for('voter_login'))
        
    if request.method == 'POST':
        user_otp = request.form['otp']
        if user_otp == session['otp']:
            session['voter_verified'] = True
            return redirect(url_for('vote'))
        else:
            flash('Invalid OTP')
            
    return render_template('voter_otp.html')

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if not session.get('voter_verified'):
        return redirect(url_for('voter_login'))
        
    conn = get_db_connection()
    parties = conn.execute('SELECT * FROM parties').fetchall()
    conn.close()
    
    if request.method == 'POST':
        party_id = request.form['party_id']
        private_key = request.form['private_key'] # Simulated Private Key
        
        # In a real blockchain, private key signs the transaction. 
        # Here we simulate it by using it as part of the transaction data.
        
        voter_id = session['voter_id']
        
        # Create Transaction
        transaction = {
            'voter_id_hash': hash_data(str(voter_id)), # Anonymize voter ID in block
            'party_id': party_id,
            'timestamp': time.time(),
            'signature': hash_data(private_key) # Simulate signature
        }
        
        blockchain.add_new_transaction(transaction)
        
        # Update Voter Status
        conn = get_db_connection()
        conn.execute('UPDATE voters SET has_voted = 1 WHERE id = ?', (voter_id,))
        conn.execute('UPDATE parties SET vote_count = vote_count + 1 WHERE id = ?', (party_id,))
        conn.commit()
        conn.close()
        
        # Clear Session
        session.clear()
        
        flash('Vote Cast Successfully! Transaction added to pool.')
        return redirect(url_for('index'))
        
    return render_template('vote.html', parties=parties)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
