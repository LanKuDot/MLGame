/*
 * The API for the user to implement the MLPlay class
 */
#ifndef _ML_PLAY_HPP_
#define _ML_PLAY_HPP_

/*
 * Additional json library. Download "json.hpp" from
 * https://github.com/nlohmann/json/blob/develop/single_include/nlohmann/json.hpp
 * and put it in the same directory of this file.
 */
#include "json.hpp"
using json = nlohmann::json;

/*
 * The abstract class for MLPlay class
 */
class AbstractMLPlay
{
public:
    /*
     * Generate the command according to the received scene information
     *
     * @param scene_info The scene information
     * @return The game command or the reset command. The game command should have
     *  two field. One is "frame", the other is "command". The value of "frame" is an
     *  integer which is the same as the value of `scene_info["frame"]`. The value of
     *  "command" is an array in which elements are string of commands. If the value of
     *  "command" is a string "RESET", then this game command is a reset command.
     */
    virtual json update(json scene_info) = 0;

    /*
     * The reset function would be invoked while received the reset command.
     */
    virtual void reset() = 0;
};

#endif // _ML_PLAY_HPP_