import random
import math
from flask import Flask, jsonify, request, render_template, send_from_directory

# --- Game Configuration ---
LOCATIONS = ["Bridge", "Engine Room", "Hydroponics", "Cafeteria", "MedBay"]
PET_DATA = {
    "Captain Whiskers": "😼", "Commander Rex": "🐶", "Dr. Bubbles": "🐠", "Navigator Nibbles": "🐹", "Engineer Squeaky": "🐭", "Pawsmonaut Prime": "🧑‍🚀"
}
MAX_TURNS = 10
PAWSMONAUT_TASK_SUCCESS_RATE = 0.9

# --- Pet & AI Classes (Python Version) ---


class Pet:
    def __init__(self, name, player_controlled=False):
        self.name = name
        self.avatar = PET_DATA.get(name, '🐾')
        self.is_alive = True
        self.current_location = None
        self.player_controlled = player_controlled
        self.suspicion_score = 0
        self.is_impostor = False

    def to_dict(self):
        return self.__dict__


class Pawsmonaut(Pet):
    def choose_action(self, locations):
        return random.choice(locations)


class DetectiveDoggo:
    def __init__(self, pets):
        self.prior_prob_impostor = 1 / len(pets)
        self.prob_evidence_given_impostor = {
            'was_at_sabotage_location': 0.7, 'completed_task': 0.05, 'was_alone': 0.6}
        self.prob_evidence_given_pawsmonaut = {
            'was_at_sabotage_location': 0.25, 'completed_task': 0.9, 'was_alone': 0.3}

    def calculate_suspicion(self, pets, evidence_log):
        raw_suspicions = {}
        living_pets = [p for p in pets if p.is_alive]

        for pet in living_pets:
            likelihood_impostor = self.prior_prob_impostor
            for evidence, value in evidence_log[pet.name].items():
                if isinstance(value, bool):
                    if value:
                        likelihood_impostor *= self.prob_evidence_given_impostor.get(
                            evidence, 1.0)
                    else:
                        likelihood_impostor *= (
                            1 - self.prob_evidence_given_impostor.get(evidence, 0.0))
            raw_suspicions[pet.name] = likelihood_impostor

        total_suspicion = sum(raw_suspicions.values())
        normalized_suspicions = {}

        if total_suspicion == 0:
            for pet in living_pets:
                normalized_suspicions[pet.name] = 1 / len(living_pets)
            return normalized_suspicions

        for name, score in raw_suspicions.items():
            normalized_suspicions[name] = score / total_suspicion

        return normalized_suspicions


class Impawster(Pet):
    def __init__(self, name):
        super().__init__(name)
        self.is_impostor = True

    def choose_action(self, game_state):
        _, best_move = self.minimax(
            game_state, depth=3, alpha=-math.inf, beta=math.inf, is_maximizing=True)
        return best_move if best_move else random.choice(self.get_possible_moves(game_state['locations']))

    def heuristic_evaluation(self, game_state):
        score = 0
        living_pawsmonauts = [p for p in game_state['pets']
                              if p['is_alive'] and not p['is_impostor']]
        if len(living_pawsmonauts) <= 1:
            return 1000
        if game_state['turn'] >= MAX_TURNS:
            return -1000
        score += len(living_pawsmonauts) * 20
        my_suspicion = game_state['suspicions'].get(self.name, 0)
        score -= my_suspicion * 100
        for pet_name, suspicion in game_state['suspicions'].items():
            if pet_name != self.name:
                score += suspicion * 50
        return score

    def get_possible_moves(self, locations):
        moves = []
        for loc in locations:
            moves.append({'type': 'sabotage', 'location': loc})
            moves.append({'type': 'fake_task', 'location': loc})
        return moves

    def minimax(self, game_state, depth, alpha, beta, is_maximizing):
        if depth == 0 or game_state['game_over']:
            return self.heuristic_evaluation(game_state), None

        if is_maximizing:
            max_eval = -math.inf
            best_move = None
            for move in self.get_possible_moves(game_state['locations']):
                evaluation, _ = self.minimax(self.simulate_move(
                    game_state, move), depth - 1, alpha, beta, False)
                if evaluation > max_eval:
                    max_eval, best_move = evaluation, move
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = math.inf
            evaluation, _ = self.minimax(self.simulate_pawsmonaut_turn(
                game_state), depth - 1, alpha, beta, True)
            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            return min_eval, None

    # Simplified simulation functions for Minimax planning
    def simulate_move(self, game_state, move):
        # This is a deep-copy-like simulation
        new_state = {k: v for k, v in game_state.items()}
        new_state['turn'] += 1
        return new_state

    def simulate_pawsmonaut_turn(self, game_state):
        new_state = {k: v for k, v in game_state.items()}
        # Simulate voting out most suspicious
        if game_state['suspicions']:
            # This part can be simplified as it's just for heuristic evaluation
            pass
        return new_state


# --- Main Game Class ---
class Game:
    def __init__(self, player_name="Pawsmonaut Prime"):
        self.turn = 1
        self.game_over = False
        self.winner = None
        self.log = []

        pet_names = [name for name in PET_DATA.keys() if name !=
                     "Pawsmonaut Prime"]
        random.shuffle(pet_names)

        self.player = Pawsmonaut(player_name, True)
        self.player.avatar = '🧑‍🚀'
        self.pets = [self.player]

        impostor_name = pet_names.pop()
        self.impawster = Impawster(impostor_name)
        self.pets.append(self.impawster)

        for name in pet_names[:3]:
            self.pets.append(Pawsmonaut(name))

        random.shuffle(self.pets)
        self.detective = DetectiveDoggo(self.pets)
        self.add_log("Mission Start! Good luck.", "system")

    def add_log(self, message, msg_type="normal"):
        self.log.append({'message': message, 'type': msg_type})

    def get_state(self):
        return {
            "turn": self.turn,
            "pets": [p.to_dict() for p in self.pets],
            "game_over": self.game_over,
            "winner": self.winner,
            "log": self.log,
            "locations": LOCATIONS
        }

    def process_player_action(self, action_data):
        self.log = []  # Clear log for the new turn's events
        action_type = action_data['type']

        if action_type == 'night_action':
            player_location = action_data['location']
            self.player.move(player_location)
            self.add_log(
                f"You head to the {player_location} to work.", "player")
            self.run_ai_night_phase()
            self.run_day_phase()

        elif action_type == 'vote':
            player_vote_name = action_data['vote']
            self.run_voting_phase(player_vote_name)

        self.check_win_conditions()
        return self.get_state()

    def run_ai_night_phase(self):
        # Impawster moves
        current_game_state_dict = {
            "pets": [p.to_dict() for p in self.pets],
            "locations": LOCATIONS,
            "turn": self.turn,
            "game_over": self.game_over,
            "suspicions": {p.name: p.suspicion_score for p in self.pets}
        }
        impawster_move = self.impawster.choose_action(current_game_state_dict)
        self.impawster.move(impawster_move['location'])

        self.sabotaged_location = None
        if impawster_move['type'] == 'sabotage':
            self.sabotaged_location = impawster_move['location']

        # Pawsmonauts move
        self.tasks_completed_by = []
        for pet in self.pets:
            if pet.is_alive and not pet.is_impostor and not pet.player_controlled:
                pet.move(pet.choose_action(LOCATIONS))
                if pet.current_location != self.sabotaged_location and random.random() < PAWSMONAUT_TASK_SUCCESS_RATE:
                    self.tasks_completed_by.append(pet.name)
        # Player can also complete tasks
        if self.player.current_location != self.sabotaged_location and random.random() < PAWSMONAUT_TASK_SUCCESS_RATE:
            self.tasks_completed_by.append(self.player.name)

    def run_day_phase(self):
        self.add_log(f"--- Day {self.turn}: Morning Report ---", 'system')
        if self.sabotaged_location:
            self.add_log(
                f"SABOTAGE in the {self.sabotaged_location}!", 'sabotage')
        else:
            self.add_log("The night was quiet... suspiciously quiet.")

        if self.tasks_completed_by:
            self.add_log(
                f"Tasks successfully completed by: {', '.join(self.tasks_completed_by)}")

        location_log = {loc: [] for loc in LOCATIONS}
        for p in self.pets:
            if p.is_alive:
                location_log[p.current_location].append(p.name)

        report = "Location Report:\n" + \
            "\n".join([f"<b>{loc}:</b> {', '.join(occ)}" for loc,
                      occ in location_log.items() if occ])
        self.add_log(report)

        # Detective's analysis
        evidence_log = self.gather_evidence()
        suspicions = self.detective.calculate_suspicion(
            self.pets, evidence_log)
        for pet in self.pets:
            pet.suspicion_score = suspicions.get(pet.name, 0)

        self.sorted_suspicions = sorted(
            suspicions.items(), key=lambda item: item[1], reverse=True)
        detective_report = "<b>Detective's Analysis:</b>\n" + \
            "\n".join([f"{name}: <b>{score:.1%}</b> suspicious" for name,
                      score in self.sorted_suspicions])
        self.add_log(detective_report, 'detective')

    def gather_evidence(self):
        evidence = {}
        living_pets = [p for p in self.pets if p.is_alive]
        for pet in living_pets:
            evidence[pet.name] = {
                'was_at_sabotage_location': pet.current_location == self.sabotaged_location,
                'completed_task': pet.name in self.tasks_completed_by,
                'was_alone': len([p for p in living_pets if p.current_location == pet.current_location]) == 1,
            }
        return evidence

    def run_voting_phase(self, player_vote_name):
        self.add_log("--- Emergency Meow-ting ---", 'system')
        votes = {p.name: 0 for p in self.pets if p.is_alive}
        if player_vote_name:
            votes[player_vote_name] += 1
            self.add_log(f"You voted for {player_vote_name}.", 'player')

        # AI Voting
        most_suspicious_name = self.sorted_suspicions[0][0]
        second_suspicious_name = self.sorted_suspicions[1][0] if len(
            self.sorted_suspicions) > 1 else most_suspicious_name

        for pet in self.pets:
            if pet.is_alive and not pet.player_controlled:
                target = second_suspicious_name if pet.name == most_suspicious_name else most_suspicious_name
                votes[target] += 1
                self.add_log(f"{pet.name} voted for {target}.", 'vote')

        max_votes = 0
        if votes:
            max_votes = max(votes.values())

        ejected_pets = [name for name,
                        v_count in votes.items() if v_count == max_votes]

        if not player_vote_name and not any(v > 0 for v in votes.values()):
            self.add_log("The vote was skipped. No one was ejected.", 'system')
        elif len(ejected_pets) > 1:
            self.add_log(
                f"Vote tied between {', '.join(ejected_pets)}. No one was ejected.", 'system')
        else:
            ejected_pet_name = ejected_pets[0]
            ejected_pet = next(
                p for p in self.pets if p.name == ejected_pet_name)
            ejected_pet.is_alive = False
            self.add_log(f"{ejected_pet_name} was ejected...", 'sabotage')
            if ejected_pet.is_impostor:
                self.add_log(
                    f"{ejected_pet_name} was the Im-paw-ster!", 'system')
                self.game_over = True
                self.winner = "Pawsmonauts"
            else:
                self.add_log(f"{ejected_pet_name} was a Pawsmonaut.", 'system')

        self.turn += 1

    def check_win_conditions(self):
        if self.game_over:
            return
        living_pets = [p for p in self.pets if p.is_alive]
        living_pawsmonauts = [p for p in living_pets if not p.is_impostor]
        living_impawsters = [p for p in living_pets if p.is_impostor]

        if not living_impawsters:
            self.game_over, self.winner = True, "Pawsmonauts"
        elif len(living_impawsters) >= len(living_pawsmonauts):
            self.game_over, self.winner = True, "Im-paw-ster"
        elif self.turn > MAX_TURNS:
            self.game_over, self.winner = True, "Im-paw-ster"


# --- Flask App ---
app = Flask(__name__, template_folder='templates', static_folder='static')
game = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/api/start', methods=['POST'])
def start_game():
    global game
    player_name = request.json.get('player_name', 'Pawsmonaut Prime')
    game = Game(player_name=player_name)
    return jsonify(game.get_state())


@app.route('/api/action', methods=['POST'])
def handle_action():
    global game
    if not game or game.game_over:
        return jsonify({"error": "Game not started or is over"}), 400

    action_data = request.json
    game_state = game.process_player_action(action_data)
    return jsonify(game_state)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
