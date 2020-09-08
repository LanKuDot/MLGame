// The user script will be included here.
#include <ml_play.hpp>
#include <mlgame_client.hpp>

int main()
{
    AbstractMLPlay *ml = new MLPlay(get_init_args());
    client_ready();

    json command;
    while (1) {
        command = ml->update(get_scene_info());
        if (command == "RESET") {
            client_reset();
            ml->reset();
            client_ready();
            continue;
        }
        send_command(command);
    }

    delete ml;
    return 0;
}
