import PySimpleGUI as sg
from user_vector_class import userVector
from Util.util_functions import read_user_ids
from user_similiraty import create_recommend_pairs
import re

sg.change_look_and_feel('TanBlue')


def user_exists_window():
    main_layout_existing_user = [[sg.Text('Steam Data Set Recommendation', justification='center')],
                                 [sg.Button('Existing User', key='existingUserButton', disabled=True),
                                  sg.VerticalSeparator(pad=None),
                                  sg.Button('New User', key='NewUserButton', disabled=True)],
                                 [sg.Combo(
                                     read_user_ids('/Users/tzvip/PycharmProjects/steamRec/steamData/game_purchase.dat'),
                                     size=(20, 1), key='UserChoice'), sg.Button('Submit')],
                                 # TODO: disable typing in combo list
                                 [sg.Radio('Feature Recommendation', 'selection', key='feature'),
                                  sg.Radio('Content Recommendation', 'selection', key='content'),
                                  sg.Radio('Similar User', 'selection', key='userSim')],
                                 [sg.Radio('Hybrid Recommendation', 'selection', key='hybrid', default=True)],
                                 [sg.Image('analyze.png', key='image', visible=False)]]
    main_window_existing_user = sg.Window('Steam Data Set Recommendation', main_layout_existing_user, )
    main_window_event_existing_user, main_window_values_existing_user = main_window_existing_user.read()
    while main_window_values_existing_user['UserChoice'] == '':
        sg.Popup('Error', 'Must choose user ID')
        main_window_event_existing_user, main_window_values_existing_user = main_window_existing_user.read()
    main_window_existing_user.FindElement('image').Update('analyze.png', visible=True)
    main_window_existing_user.refresh()
    if main_window_values_existing_user['feature'] is True:
        userID = main_window_values_existing_user['UserChoice']
        owned_games, results = src.recommend(userID)
        main_window_existing_user.close()
        user_results_window(owned_games, results, userID)
    if main_window_values_existing_user['content'] is True:
        userID = main_window_values_existing_user['UserChoice']
        owned_games = src.owned_game_list(userID)
        main_window_existing_user.close()
        content_recom_chooser(userID, owned_games)
    if main_window_values_existing_user['userSim'] is True:
        userID = main_window_values_existing_user['UserChoice']
        pairs = create_recommend_pairs()
        recom = src.owned_game_list(pairs[userID])
        myGames = src.owned_game_list(userID)
        recom = check_similar_games(myGames, recom)
        main_window_existing_user.close()
        user_results_window(myGames, recom, userID,
                            '| Recommendation by the user with the same taste: ' + str(pairs[userID]))
    if main_window_values_existing_user['hybrid'] is True:
        # Feature Recommendation
        userID = main_window_values_existing_user['UserChoice']
        owned_games, results_feature = src.recommend(userID)
        # Content Recommendation
        current_usr = userVector(str(userID))
        sorted_gameplay = current_usr.playTime
        if not sorted_gameplay:
            sg.Popup('Error', 'Destiny Failed! Not enough data!')
        game_Ids = src.load_gameIds()
        for key in sorted_gameplay.keys():
            sorted_gameplay[key] = float(sorted_gameplay[key])
        sorted_gameplay = {k: v for k, v in
                           sorted(current_usr.playTime.items(), key=lambda item: item[1], reverse=True)}
        results_content = content_recom.show_rec(game_Ids[str(list(sorted_gameplay)[0])])
        # Similar Users Recommendation
        pairs = create_recommend_pairs()
        recom = src.owned_game_list(pairs[userID])
        myGames = src.owned_game_list(userID)
        recom = check_similar_games(myGames, recom)
        # ===== Results analysis =====
        final_results = dict()
        alpha_content = 1
        beta_feature = 0.65
        gamma_similar = 1
        # Content results
        for _ in range(len(results_content)):
            score = float(results_content[_][results_content[_].find('Score'):].split(':')[1]) * alpha_content
            gameName = results_content[_][2:results_content[_].find('Score')].strip()
            final_results[gameName] = score
        # Feature results
        for _ in range(len(results_feature)):
            score = float(results_feature[_][results_feature[_].find('Score'):].split(':')[1]) * beta_feature
            gameName = results_feature[_][2:results_feature[_].find('Score')].strip()
            if gameName in final_results:
                final_results[gameName] = final_results[gameName] + score
            else:
                final_results[gameName] = score
        # Similar user recommendation
        for game in recom:
            if game[2:] in final_results:
                final_results[game[2:]] = final_results[game[2:]] + gamma_similar
        final_results = {k: v for k, v in sorted(final_results.items(), key=lambda item: item[1], reverse=True)}  # Sort the dict ascending values
        final_rec_list = check_similar_games(owned_games, list(final_results), True)
        final_rec_sort_dict = dict()
        for elem in final_rec_list:
            final_rec_sort_dict[elem] = final_results[elem]
        final_rec_sort_dict = {k: v for k, v in sorted(final_rec_sort_dict.items(), key=lambda item: item[1], reverse=True)}  # Sort the dict ascending values
        final_rec_list.clear()
        final_rec_list = list(final_rec_sort_dict)
        for _ in range(len(final_rec_list)):
            final_rec_list[_] = final_rec_list[_] + ' | Score:' + str(final_rec_sort_dict[final_rec_list[_]])
        main_window_existing_user.close()
        user_results_window(owned_games, final_rec_list, userID)


def content_recom_chooser(user_id, ownedGames):
    content_chooser_layout = [[sg.Text('Choose Option', justification='center')],
                              [sg.Button('I choose my Destiny', key='user_choice'), sg.VerticalSeparator(pad=None),
                               sg.Button('Destiny chooses for me', key='stats')]]
    content_chooser_window = sg.Window('Choose!', content_chooser_layout)
    content_chooser_event, content_chooser_value = content_chooser_window.read()
    if content_chooser_event is 'stats':
        current_usr = userVector(str(user_id))
        sorted_gameplay = current_usr.playTime
        if not sorted_gameplay:
            sg.Popup('Error', 'Destiny Failed! Not enough data!')
            content_chooser_window.close()
            content_recom_chooser(user_id, ownedGames)
        game_Ids = src.load_gameIds()
        for key in sorted_gameplay.keys():
            sorted_gameplay[key] = float(sorted_gameplay[key])
        sorted_gameplay = {k: v for k, v in
                           sorted(current_usr.playTime.items(), key=lambda item: item[1], reverse=True)}
        results = content_recom.show_rec(game_Ids[str(list(sorted_gameplay)[0])])
        content_chooser_window.close()
        user_results_window([game_Ids[str(list(sorted_gameplay)[0])]], results, user_id)
    if content_chooser_event is 'user_choice':
        content_chooser_window.close()
        contet_recom_window(user_id, ownedGames)


def contet_recom_window(user_id, ownedGames):
    content_layout = [[sg.Text('Choose one of your games: ')],
                      [sg.Listbox(values=ownedGames, select_mode=sg.LISTBOX_SELECT_MODE_SINGLE, key='chooser',
                                  size=(30, 6))],
                      [sg.Submit()]]
    content_window = sg.Window('Content Recommendation', content_layout)
    content_event, content_values = content_window.read()
    chosen_game = content_values['chooser']
    chosen_game = re.sub('^[0-9]+\s', '', chosen_game[0])
    results = content_recom.show_rec(chosen_game)
    content_window.close()
    user_results_window([chosen_game], results, user_id)
    print()


def user_results_window(owned_games, results, userID='New User', altText=''):
    user_results_window_layout = [[sg.Text('Displaying Results For ' + str(userID) + altText, justification='center')],
                                  [sg.Text('Owned Games', justification='center'), sg.VerticalSeparator(pad=None),
                                   sg.Text('Recommended games', justification='center')],
                                  [sg.Multiline('\n'.join(owned_games)), sg.VerticalSeparator(pad=None),
                                   sg.Multiline('\n'.join(results))],
                                  [sg.Button('Back')]]
    user_results_window_window = sg.Window('Results', user_results_window_layout)
    event, value = user_results_window_window.read()
    if event is 'Back':
        user_results_window_window.close()
        main_window_func()


welcome_screen_layout = [[sg.Text('Welcome to Steam Data Set Recommendation', justification='center')],
                         [sg.Button('Load Module')],
                         [sg.Image('loading3.png', key='image', visible=False)]]
welcome_screen_window = sg.Window('Welcome', welcome_screen_layout)

while True:
    welcome_event, welcome_value = welcome_screen_window.read()
    if welcome_event is None:
        exit()
    if welcome_event is 'Load Module':
        welcome_screen_window.FindElement('image').Update('loading3.png', visible=True)
        welcome_screen_window.Refresh()
        import src

        print('Loading content_recommendation model ....')
        import content_recom

        print('Done loading!')
        welcome_screen_window.close()
        break


# region Main Window
def main_window_func():
    main_layout = [[sg.Text('Steam Data Set Recommendation', justification='center')],
                   [sg.Button('Existing User'), sg.VerticalSeparator(pad=None), sg.Button('New User')]]
    main_window = sg.Window('Steam Data Set Recommendation', main_layout)

    while True:
        main_window_event, main_window_values = main_window.read()
        if main_window_event is None:  # If user closes the window
            break
        if main_window_event is 'Existing User':
            main_window.close()  # Close main window for updating with user existing
            user_exists_window()
        if main_window_event is 'New User':
            main_window.close()
            new_user_chooser()


# endregion

# region ============ New User windows ================
def new_user_chooser():
    new_user_layout = [[sg.Text('Choose games that you like from the list')],
                       [sg.Listbox(values=src.game_list(), select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE, size=(30, 6),
                                   key='chooser')],
                       [sg.Button('Submit')]]
    new_user_window = sg.Window('Game chooser for new user', new_user_layout)
    new_user_event, new_user_values = new_user_window.read()
    new_user_window.close()
    new_user_options(new_user_values['chooser'])


def new_user_options(new_user_games):
    new_user_options_layout = [[sg.Text('Choose the recommendation option', justification='center')],
                               [sg.Radio('Feature Recommendation', 'selection', key='feature', default=True),
                                sg.Radio('Content Recommendation', 'selection', key='content'),
                                sg.Radio('Similar User', 'selection', key='userSim')],
                               [sg.Button('Recommend!')],
                               [sg.Image('fallout_rec.png', key='image', visible=False)]]
    new_user_options_window = sg.Window('New user options', new_user_options_layout)
    new_user_options_event, new_user_options_values = new_user_options_window.read()
    new_user_options_window.FindElement('image').Update('fallout_rec.png', visible=True)
    new_user_options_window.refresh()
    if new_user_options_values['feature'] is True:
        games_chosen, results_list = src.create_new_user_vector_obj(new_user_games)
        new_user_options_window.close()
        user_results_window(games_chosen, results_list)
    if new_user_options_values['content'] is True:
        games_name = list()
        for game in new_user_games:
            game_split = game.split('=')
            games_name.append(game_split[1])
        new_user_options_window.close()
        contet_recom_window('New User', games_name)
    if new_user_options_values['userSim'] is True:
        usr_obj = src.create_new_user_vector_obj_class(new_user_games)
        pairs = create_recommend_pairs(usr_obj, True)
        myGames = usr_obj.gameOwned
        recom = src.owned_game_list(pairs[usr_obj.userID])
        recom = check_similar_games(myGames, recom)
        new_user_options_window.close()
        user_results_window(myGames, recom, usr_obj.userID,
                            '| Recommendation by the user with the same taste: ' + str(pairs[usr_obj.userID]))


# endregion


def check_similar_games(owned, recom, noNumbers=False):
    # Remove numbers
    for _ in range(len(owned)):
        owned[_] = re.sub('^[0-9]+\s', '', owned[_])
    for _ in range(len(recom)):
        recom[_] = re.sub('^[0-9]+\s', '', recom[_])
    # Remove already owned games from the list
    recom = list(set(recom) - set(owned))
    if noNumbers:
        return recom
    # Add order numbering
    for index in range(len(recom)):
        recom[index] = str(index + 1) + ' ' + recom[index]
    return recom


main_window_func()
