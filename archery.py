import copy
import random
import matplotlib.pyplot as plt

max_luck_player_per_game = {}
gender_wins_per_game = {
    'F': 0,
    'M': 0,
}
gender_total_wins = {
    'F': 0,
    'M': 0,
}


def __make_teams(team_name: str) -> list:
    team = []

    for i in range(15):
        gender = 'F' if random.random() < 0.5 else 'M'
        team.append({'player': i + 1, 'gender': gender, 'team': team_name})

    return team


def __calculate_resistance() -> int:
    return 45 if random.random() < 0.5 else 65


def __calculate_luck() -> float:
    return random.uniform(1, 5)


def __fill_teams_data(team_name: str) -> list:
    teams = __make_teams(team_name)
    for team in teams:
        resistance = __calculate_resistance()
        team.update({
            'GResistance': resistance,
            'luck': __calculate_luck(),
            'points': 0,
            'experience': 10,
            'roundResistance': resistance,
            'winRounds': 0,
            'experienceEarn': 0
        })
    return teams


def __montecarlo_tired() -> int:
    return 1 if random.random() < 0.5 else 2


def __montecarlo_shoot_women() -> int:
    rand = random.randrange(0, 100)
    points = 0
    if 0 <= rand <= 29:
        points = 10
    elif 30 <= rand <= 67:
        points = 8
    elif 68 <= rand <= 94:
        points = 6
    elif 95 <= rand <= 99:
        points = 0

    return points


def __montecarlo_shoot_men() -> int:
    rand = random.randrange(0, 100)
    points = 0
    if 0 <= rand <= 19:
        points = 10
    elif 20 <= rand <= 52:
        points = 8
    elif 53 <= rand <= 92:
        points = 6
    elif 93 <= rand <= 99:
        points = 0

    return points


def __round_player_shoot(player: dict) -> int:
    resistance = player['roundResistance']
    points = 0
    while resistance >= 5:
        points = __shoot(player, points)
        resistance = resistance - 5

    return points


def __shoot(player: dict, points: int) -> int:
    gender = player['gender']
    if gender == 'F':
        points = points + __montecarlo_shoot_women()
    else:
        points = points + __montecarlo_shoot_men()

    return points


def __player_round(team: list) -> None:
    for p in team:
        points = __round_player_shoot(p)
        p.update({'points': points})
        new_resistance = p['roundResistance']
        p.update({'roundResistance': new_resistance - __montecarlo_tired()})


def __player_max_luck(team: list) -> dict:
    return max(team, key=lambda x: x['luck'])


def __calculate_player_max_luck_in_round(team_a: list, team_b: list) -> dict:
    global max_luck_player_per_game
    max_player_luck_team_a = __player_max_luck(team_a)
    max_player_luck_team_b = __player_max_luck(team_b)

    return max([max_player_luck_team_a, max_player_luck_team_b], key=lambda x: x['luck'])


def __calculate_player_max_luck_in_game(team_a: list, team_b: list) -> None:
    global max_luck_player_per_game
    max_player_per_round = copy.deepcopy(__calculate_player_max_luck_in_round(team_a, team_b))
    if max_luck_player_per_game:
        max_luck_player_per_game = max(
            [max_player_per_round, max_luck_player_per_game], key=lambda x: x['luck']
        )
        return
    max_luck_player_per_game = max_player_per_round


def __calculate_gender_wins_per_game(winner_player: dict) -> None:
    global gender_wins_per_game
    if winner_player is not None:
        winner_gender = winner_player["gender"]
        gender_wins_per_game[winner_gender] += 1


def __calculate_gender_total_wins(gender: str) -> None:
    global gender_total_wins
    gender_total_wins[gender] += 1


def __calculate_player_max_experience(team_a: list, team_b: list) -> dict:
    return max(team_a + team_b, key=lambda x: x['experience'])


def __round_winner_list(list_player: list, key_value: str) -> list:
    seq = [x[key_value] for x in list_player]
    max_point = max(seq)
    return list(filter(lambda person: person[key_value] == max_point, list_player))


def __round_winner(winner_list: list) -> dict:
    if len(winner_list) > 1:
        points = 0
        for x in winner_list:
            points = __shoot(x, points)
            x.update({'tie-breaker': points})
        __round_winner(__round_winner_list(winner_list, 'tie-breaker'))
    else:
        winner = winner_list[0]
        winner['experienceEarn'] = winner['experienceEarn'] + 3
        winner['winRounds'] = winner['winRounds'] + 1
        return winner


def __team_shot(team: list, team_general: dict) -> None:
    player = __player_max_luck(team)
    points = __shoot(player, 0)
    team_general['groupPoints'] = team_general['groupPoints'] + points


def __calculate_team_points_round(team: list, team_general: dict) -> None:
    seq = [x['points'] for x in team]
    result = sum(seq)
    team_general['groupPoints'] = team_general['groupPoints'] + result


def __restart_values_round(team: list, team_general: dict) -> None:
    for i in team:
        i['luck'] = __calculate_luck()
        i['experience'] = i['experience'] + i['experienceEarn']
        i['points'] = 0

    team_general['groupPointsTotal'] = team_general['groupPointsTotal'] + team_general['groupPoints']
    team_general['groupPoints'] = 0


def __restart_values_game(team: list, team_general: dict) -> None:
    for i in team:
        i['roundResistance'] = i['GResistance']
        i['winRounds'] = 0
    team_general['groupPointsTotal'] = 0


def __winner_team(team_a_general: dict, team_b_general: dict, key: str) -> dict:
    teams = [team_a_general, team_b_general]
    return max(teams, key=lambda x: x[key])


def __game_winner_player(players_list: list) -> dict:
    return max(players_list, key=lambda x: x['winRounds'])


def init_game() -> tuple:
    global max_luck_player_per_game, gender_wins_per_game
    total_games = 1000
    team_a = __fill_teams_data('A')
    team_b = __fill_teams_data('B')
    team_a_general = {'name': 'A', 'groupPoints': 0, 'groupPointsTotal': 0, 'winRound': 0, 'winGame': 0}
    team_b_general = {'name': 'B', 'groupPoints': 0, 'groupPointsTotal': 0, 'winRound': 0, 'winGame': 0}

    graph_team_x_data_points = []
    graph_team_y_data_points = []
    graph_total_games_data = list(range(1, total_games + 1))

    print(team_a_general)
    print(team_b_general)

    for game in range(total_games):
        for game_round in range(10):
            __player_round(team_a)
            __player_round(team_b)
            __team_shot(team_a, team_a_general)
            __team_shot(team_a, team_b_general)

            __calculate_player_max_luck_in_game(team_a, team_b)
            __calculate_gender_wins_per_game(__round_winner(__round_winner_list(team_a + team_b, 'points')))
            __calculate_team_points_round(team_a, team_a_general)
            __calculate_team_points_round(team_b, team_b_general)
            round_winner_team = __winner_team(team_a_general, team_b_general, 'groupPoints')
            print("Equipo ganador ronda", round_winner_team)
            __restart_values_round(team_a, team_a_general)
            __restart_values_round(team_b, team_b_general)

        gender_winner_per_game = max(gender_wins_per_game, key=gender_wins_per_game.get)
        print('equipo ganador del juego es ', __winner_team(team_a_general, team_b_general, 'groupPointsTotal'))
        print('ganador de juego es ', __game_winner_player(team_a + team_b))
        print("Mayor suerte juego", max_luck_player_per_game)
        print("Mejor genero", gender_winner_per_game)
        graph_team_x_data_points.append(team_a_general['groupPointsTotal'])
        graph_team_y_data_points.append(team_b_general['groupPointsTotal'])
        __calculate_gender_total_wins(gender_winner_per_game)

        max_luck_player_per_game = {}
        gender_wins_per_game = {'F': 0, 'M': 0}
        __restart_values_game(team_a, team_a_general)
        __restart_values_game(team_b, team_b_general)
        print('--------------------------------------------------------------------')
    print('Mayor experiencia juego', __calculate_player_max_experience(team_a, team_b))
    print('Mejor genero total', max(gender_total_wins, key=gender_total_wins.get))

    return graph_team_x_data_points, graph_team_y_data_points, graph_total_games_data


if __name__ == '__main__':
    team_a, team_b, y = init_game()

    plt.plot(y, team_a, label='Team A')
    plt.plot(y, team_b, label='Team B')
    plt.legend()
    plt.show()
