/*
 * The mlgame client library for C++
 */
#ifndef _MLGAME_CLIENT_
#define _MLGAME_CLIENT_

#include <iostream>

/*
 * Additional json library. Download "json.hpp" from
 * https://github.com/nlohmann/json/blob/develop/single_include/nlohmann/json.hpp
 * and put it in the same directory of this file.
 */
#include "json.hpp"
using json = nlohmann::json;

using namespace std;

/*
 * Get the initial arguments
 */
json get_init_args()
{
    string init_args_str;
    getline(cin, init_args_str);

    // Ignore header "__init__"
    init_args_str.erase(0, init_args_str.find_first_of('{'));

    return json::parse(init_args_str);
}

/*
 * Inform the game that ml client is ready for receiving the data
 */
void ml_ready()
{
    cout << "__command__ READY" << endl;
}

/*
 * Receive the scene info sent from the game
 */
json get_scene_info()
{
    string scene_info_str;
    getline(cin, scene_info_str);

    // Ignore header "__scene_info__"
    scene_info_str.erase(0, scene_info_str.find_first_of('{'));

    return json::parse(scene_info_str);
}

/*
 * Send the game command to the game
 */
void send_command(json command)
{
    cout << "__command__ " << command << endl;
}

#endif //_MLGAME_CLIENT_
