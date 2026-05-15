import time
import math
import random
from flask import Flask, render_template, session, request, jsonify

app = Flask(__name__)
app.secret_key = 'super-secret-key'

leaderboard = []

CANVAS_WIDTH = 600
CANVAS_HEIGHT = 400

# 5 типов мишеней: радиус, цвет, базовые очки
TARGET_TYPES = [
    {'radius': 40, 'color': 'red', 'points': 2},
    {'radius': 34, 'color': 'yellow', 'points': 4},
    {'radius': 28, 'color': 'green', 'points': 6},
    {'radius': 22, 'color': 'violet', 'points': 8},
    {'radius': 16, 'color': 'orange', 'points': 10},
]

def new_target():
    t = random.choice(TARGET_TYPES)
    radius = t['radius']
    x = random.randint(radius, CANVAS_WIDTH - radius)
    y = random.randint(radius, CANVAS_HEIGHT - radius)
    return {
        'x': x,
        'y': y,
        'radius': radius,
        'color': t['color'],
        'base_points': t['points']
    }

@app.route('/')
def index():
    session['score'] = 0
    session['combo'] = 0
    session['last_hit_time'] = 0.0
    session['target'] = new_target()
    session['target_created_at'] = time.time()
    return render_template('index.html')

@app.route('/target')
def get_target():
    if 'target' not in session:
        session['score'] = 0
        session['combo'] = 0
        session['last_hit_time'] = 0.0
        session['target'] = new_target()
        session['target_created_at'] = time.time()
    return jsonify(
        target=session['target'],
        score=session.get('score', 0),
        combo=session.get('combo', 0)
    )

@app.route('/shoot', methods=['POST'])
def shoot():
    data = request.get_json()
    click_x = data.get('x')
    click_y = data.get('y')
    if click_x is None or click_y is None:
        return jsonify(error='No coordinates'), 400

    if 'target' not in session:
        return jsonify(error='No target'), 400

    target = session['target']
    dist = math.hypot(click_x - target['x'], click_y - target['y'])
    hit = dist <= target['radius']
    score = session.get('score', 0)
    combo = session.get('combo', 0)
    last_hit_time = session.get('last_hit_time', 0.0)
    now = time.time()

    points_earned = 0
    if hit:
        if last_hit_time and (now - last_hit_time) < 2.0:
            combo += 1
        else:
            combo = 1
        session['combo'] = combo
        session['last_hit_time'] = now

        combo_mult = 1 + 0.25 * (combo - 1)
        base_points = target['base_points']
        points_earned = max(1, round(base_points * combo_mult))
        score += points_earned
        session['score'] = score

        session['target'] = new_target()
        session['target_created_at'] = time.time()

        return jsonify(
            hit=True,
            score=score,
            combo=combo,
            points_earned=points_earned,
            target=session['target']
        )
    else:
        session['combo'] = 0
        session['last_hit_time'] = 0.0
        return jsonify(
            hit=False,
            score=score,
            combo=0,
            points_earned=0,
            target=target
        )

@app.route('/end_game', methods=['POST'])
def end_game():
    data = request.get_json()
    player_name = data.get('name', 'Аноним')
    final_score = session.get('score', 0)
    leaderboard.append({'name': player_name, 'score': final_score})
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    top10 = leaderboard[:10]
    session.clear()
    return jsonify(score=final_score, leaderboard=top10)

if __name__ == '__main__':
    app.run(debug=True)