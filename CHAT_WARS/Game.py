from flask import Flask, session, render_template, request, redirect, g, url_for, flash, Response, json
#~ from flask_sqlalchemy import SQLAlchemy
#~ from sqlalchemy import create_engine, MetaData, Table
from Models import db,Castles,Player,Quests
import os
import random
import math
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from time import sleep
from passlib.hash import sha256_crypt


app = Flask(__name__)
app.secret_key = os.urandom(67)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'



from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


#-------------------------GAME LOGIC---------------------------------/

@app.before_first_request
def initialize():
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler.add_job(
        func=evaluate,
        trigger=IntervalTrigger(seconds=216000),
        id='eval_job',
        name='Evaluate battle report',
        replace_existing=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


def evaluate():
    attacks = []
    attacksum = [0]*7
    for i in range(1,8):
        castlename=Castles.query.filter_by(id=i).first().name
        attacks.append(Player.query.filter_by(state=castlename).all())
    

    defs = []
    defsum = [0]*7
    for i in range(1,8):
        defs.append(Player.query.filter_by(    
            castle_id=i, state='DEFEND').all())
    print(defs)
    
    f = open("warreport.txt","w")
    for i in range(7):
        for attak in attacks[i]:
            attacksum[i] += attak.attack
            attak.state = 'DEFEND'
            db.session.commit()
        for defnd in defs[i]:
            defsum[i] += defnd.defense
        if attacksum[i] == 0 :
            f.write("No Attacks on " + Castles.query.filter_by(id=i+1).first().name + "\n")
        elif defsum[i] > attacksum[i]:
            f.write(Castles.query.filter_by(id=i+1).first().name+" was successful in defending it's glory!"+'\n')
            for attak in attacks[i]:
                attak.gold += 20
                db.session.commit()
        else:
            f.write(Castles.query.filter_by(id=i+1).first().name+" was pillaged by the attackers."+'\n')
            for defnd in defs[i]:
                defnd.exp += 5
                if defnd.exp >= math.pow(2, defnd.level):
                    defnd.level += 1
                db.session.commit()
    f.close()

    print("Battle Report Ready")



# -----------------------VIEWS-----------------------------------------/

# register page
@app.route('/reg')
def register():
    return render_template('register.html')


@app.route('/add', methods=['POST'])
def add():
    try:
	    player = Player(
	        username=request.form['username'], password=sha256_crypt.encrypt(request.form['password']), castle_id=request.form['castle'], email=request.form['email'])
	    db.session.add(player)
	    db.session.commit()
	    return redirect(url_for('login'))
    except:
        return ('User already exists !!')


# login page
@app.route('/')
@app.route('/login')
def login():
    try:
        if session['user']:
            return redirect('/home')
    except:
	    return render_template('login.html')


@app.route('/enter', methods=['POST'])
def enter():
    try:
	    session.pop('user', None)
	    player = Player.query.filter_by(
	        username=request.form['username']).first()
	    if (sha256_crypt.verify(request.form['password'],player.password)):
	        session['user'] = request.form['username']
	        flash('Logged in Successfully')
	        return redirect('/home')
	    else:
	        return redirect('/login')
    except:
        return "Username or Password Invalid"

# logout page
@app.route('/logout')
def logout():
    try:
        session.pop('user', None)
        return redirect(url_for('login'))
    except:
        return redirect(url_for('login'))
# Player home


@app.route('/home')
def home():
    try:
	    return render_template('MainView.html', user=Player.query.filter_by(username=session['user']).first())
    except:
        return redirect(url_for('login'))
# Attack page


@app.route('/attack')
def attack():
    try:
	    castle=[]
	    playercastle = Player.query.filter_by(username=session['user']).first()
	    if playercastle:
	        for row in Castles.query.all():
	            if row != playercastle.castle:
	                castle.append(row)
	    return render_template('AttackView.html', user=Player.query.filter_by(username=session['user']).first(), castle=castle)
    except:
        return redirect(url_for('login'))

# attack function
@app.route('/attack/<castlename>')
def attackcastle(castlename):
    try:
	    player = Player.query.filter_by(
	        username=session['user']).first()
	    player.state = castlename
	    db.session.commit()
	    return render_template('confirmation.html', state='attacking', castle=player.state, user=player)
    except:
        return redirect(url_for('login'))


# defend function
@app.route('/defend')
def defendcastle():
    try:
	    player = Player.query.filter_by(
	        username=session['user']).first()
	    player.state = 'DEFEND'
	    db.session.commit()
	    return render_template('confirmation.html', state='defending', castle=player.castle.name, user=player)
    except:
	    return redirect(url_for('login'))
# quests


@app.route('/quests')
def quests():
    try:
        flash('Wait for 5 secs')
        sleep(5)
        quest = questgo()
        player = Player.query.filter_by(username=session['user']).first()
        if(player.exp >= math.pow(2, player.level)):
            player.level += 1
            db.session.commit()
            return render_template('levelup.html', quest=quest.text, user=player)
        return render_template('QuestView.html', quest=quest.text, user=player)
    except:
        return redirect(url_for('login'))


def questgo():
    quest = Quests.query.filter_by(id=int(random.randint(1, 5))).first()
    player = Player.query.filter_by(username=session['user']).first()
    player.gold += quest.gold
    player.exp += quest.exp
    db.session.commit()
    return quest

# castle


@app.route('/castle')
def castle():
    try:
        return render_template('CastleView.html', user=Player.query.filter_by(username=session['user']).first())
    except:
        return redirect(url_for('login'))


@app.route('/sword')
def sword():
    try:
        player = Player.query.filter_by(username=session['user']).first()
        if player.gold >= math.pow(2, player.sword):
            player.gold -= math.pow(2, player.sword)
            player.sword += 1
            player.attack += 2*player.sword
            db.session.commit()
            return render_template('sword.html', user=player)
        else:
            return render_template('neg.html',user=player)
    except:
        return redirect(url_for('login'))


@app.route('/sheild')
def sheild():
    try:
        player = Player.query.filter_by(username=session['user']).first()
        if player.gold >= math.pow(2, player.sheild):            
            player.gold -= math.pow(2, player.sheild)
            player.sheild += 1
            player.defense += 2*player.sheild
            db.session.commit()
            return render_template('sheild.html', user=player)
        else:
            return render_template('neg.html',user=player)
    except:
        return redirect(url_for('login'))

@app.route('/increase',methods=['PUT'])
def increase():
    data = request.get_json()
    print (data)
    player = Player.query.filter_by(username=session['user']).first()
    player.attack += data['attack']
    player.defense += data['defend']
    db.session.commit()
    return Response(
        json.dumps({'message': 'Successfully updated stats','attack':'{0}'.format(player.attack),'defense':'{0}'.format(player.defense)}),
        status=200,
        mimetype='application/json'
    )


@app.route('/info')
def about():
    try:
        f=open("warreport.txt",'r')
        report=[]
        for line in f:
            report.append(line)
        print(report)
        return render_template('Warreport.html',user=Player.query.filter_by(username=session['user']).first(),text=report)
    except:
        return redirect(url_for('login'))


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


if __name__ == "__main__":
    db.init_app(app=app)
    db.create_all(app=app)
    app.run(debug=True)
